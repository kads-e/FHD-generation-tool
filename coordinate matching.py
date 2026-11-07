import csv
import scipy as sp
from astropy.coordinates import SkyCoord
import astropy.units as u
import numpy as np
from scipy.optimize import linear_sum_assignment
import matplotlib.pyplot as plt

# constants
pc = 3.085677581e16  # Parsec in m
rr_lyrae_absolute_magnitude = 0.75 # as seen in sources (TODO: what source)


# input
header_lines = 10 # the astropy script gives 10 header lines by dafault, lower if needed
infiles = ["Blau_M13.txt", "Grün_M13.txt"]
rr_lyrae_visual_magnitude = 15 # Set to a float value of magnitude if known
distance_error = 0.5 # in magnitudes, range in which a bound gets calculated for distance calculations
min_NS = 0  # minimum Noise to Signal ratio => lower brightness stars will be ignored, numbers used: 5-20
min_ADU = 0 # 0 for M13 and 10000 for M48

# data
gruen = []
blau = []
star_data = [blau, gruen]
matches = []
bv_data = []

blau_war_heller = 0
gruen_war_heller = 0


# functions
def read_csv_file(filename):
    return read_csv_file_with_header(filename, header_lines)

def read_csv_file_with_header(filename, header_lines):
    with open(filename, "r", encoding="utf-8") as infile:
        # Skip metadata/header lines if present
        for _ in range(header_lines):
            next(infile)
        reader = csv.reader(
            (line.replace(" ; ", ";").replace("False", "0").replace("True", "1") for line in infile),
            delimiter=";", 
            quoting=csv.QUOTE_NONNUMERIC
        )
        return [row for row in reader if row[6] > min_NS and row[5] > min_ADU] # lower brightness stars will be ignored

        


def match_stars(in_blau, in_gruen, max_sep_arcsec=1):
    blau = SkyCoord(
        ra=[row[3] for row in in_blau] * u.deg,
        dec=[row[4] for row in in_blau] * u.deg,
        frame="icrs",
    )
    gruen = SkyCoord(
        ra=[row[3] for row in in_gruen] * u.deg,
        dec=[row[4] for row in in_gruen] * u.deg,
        frame="icrs",
    )

    cost = blau[:, None].separation(gruen[None, :]).arcsec
    cost[cost > max_sep_arcsec] = 1e9

    row_ind, col_ind = linear_sum_assignment(cost)

    return [
        (int(row), int(col))
        for row, col in zip(row_ind, col_ind)
        if cost[row, col] <= max_sep_arcsec
    ]


def match_stars_old(in_blau, in_gruen):
    # 1. Kostenmatrix zwischen den beiden Sternlisten aufstellen:
    #   https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.cdist.html
    #   scipy.spatial.distance.cdist
    kosten_bg = []
    cdist_in_blau = [row[3:5] for row in in_blau]
    cdist_in_gruen = [row[3:5] for row in in_gruen]
    try:
        kosten_bg = sp.spatial.distance.cdist(cdist_in_blau, cdist_in_gruen, metric='sqeuclidean') 
    except ValueError:
        print("ValueError when trying to calculate cdist. Check your inputs.")



    # 2. Matching optimal lösen lassen:
    #   https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html
    #   scipy.optimize.linear_sum_assignment
    row_ind = []
    col_ind = []
    try:
        row_ind, col_ind = sp.optimize.linear_sum_assignment(kosten_bg)
    except ValueError:
        print("ValueError when trying to solve linear sum assignment. Check your inputs.")
    # 3. Ergebnis zurückgeben
    # Liste aus Paaren (Blau(i), Grün(i)) zurückgeben, mit der Länge des kürzeren Arrays (falls ungleich lang)
    return [(row_ind[i], col_ind[i]) for i in range(0, min(len(row_ind), len(col_ind)) - 1)]

def calc_bv(b_g_pair):
    return b_g_pair[0][7] - b_g_pair[1][7]

def calc_bv_data(blau, gruen, matching):
    return [calc_bv((blau[pair[0]], gruen[pair[1]])) for pair in matching]

def calc_Entfernungsmodul(m, M):         # m = scheinbare Helligkeit, M = absolute Helligkeit (auszurechnen)
    return 10**(0.2 * (m - M)) * 10 # * pc           falls in m gewünscht, sonst in pc

def pc_to_ly(pc):
    return pc * 3.26156

def calc_AngenäherteAbsoluteHelligkeit(m, d):  # m = scheinbare Helligkeit, d = Entfernung in pc
    return m - 5 * (np.log10(d) - 1)

def calc_AngenäherteScheinbareHelligkeit_TEMP(blau, gruen, matching):
    scheinbare_helligkeit = []
    blau_war_heller = 0
    gruen_war_heller = 0
    for pair in matching:
        m_blau = blau[pair[0]][7]
        m_gruen = gruen[pair[1]][7]
        scheinbare_helligkeit.append(m_gruen)
        if m_blau > m_gruen:
            blau_war_heller += 1
        else:
            gruen_war_heller += 1
    return scheinbare_helligkeit   

def calc_distance(rr_lyrae_visual_magnitude, rr_lyrae_absolute_magnitude):
    distance = calc_Entfernungsmodul(rr_lyrae_visual_magnitude, rr_lyrae_absolute_magnitude)
    upper_distance = calc_Entfernungsmodul(rr_lyrae_visual_magnitude+distance_error/2 , rr_lyrae_absolute_magnitude)
    lower_distance = calc_Entfernungsmodul(rr_lyrae_visual_magnitude-distance_error/2 , rr_lyrae_absolute_magnitude)
    print(f"Distance: {lower_distance} - {upper_distance} pc or {pc_to_ly(lower_distance)} - {pc_to_ly(upper_distance)} light years")
# pyplot event handler

def on_pick(event):
    if event.artist is FHD:
        for index in event.ind:
            print(f"Star number: {index + 1}")
            print(f"B-V: {bv_data[index]}, Apparent Magnitude: {app_mag_data[index]}, Coordinates: RA={star_data[0][matches[index][0]][3]}, Dec={star_data[0][matches[index][0]][4]}, blue Coordinates: X={star_data[1][matches[index][0]][1]}, Y={star_data[1][matches[index][0]][2]}, green coordinates: X={star_data[0][matches[index][1]][1]}, Y={star_data[0][matches[index][1]][2]}")
            print()
            ax.annotate(str(index + 1), xy=(bv_data[index], app_mag_data[index]), xytext=(-10, 7), textcoords="offset points")
        fig.canvas.draw()



# get data
for i,f in enumerate(infiles):
    star_data[i] = read_csv_file(f)

matches = match_stars(star_data[0], star_data[1])

bv_data = calc_bv_data(star_data[0], star_data[1], matches)
app_mag_data = calc_AngenäherteScheinbareHelligkeit_TEMP(star_data[0], star_data[1], matches)


# calc distance and absolute magnitude, if RR lyrae visual magnitude is known
if rr_lyrae_visual_magnitude is not None:
    calc_distance(rr_lyrae_visual_magnitude, rr_lyrae_absolute_magnitude)

fig = plt.figure()
ax = fig.add_subplot(111)

FHD = ax.plot(bv_data, app_mag_data, "o", picker=5)[0] # picker = 5 => tolleranz
plt.title("FHD M13")
plt.xlabel("B-V")
plt.ylabel("Apparent Magnitude")
plt.gca().invert_yaxis()  # Invert y-axis for apparent magnitude

#for i, (bv, app_mag) in enumerate(zip(bv_data, app_mag_data), start=1):
#    ax.annotate(str(i), xy=(bv, app_mag), xytext=(-10, 7), textcoords="offset points")

fig.canvas.mpl_connect("pick_event", on_pick)


plt.show()
exit()







