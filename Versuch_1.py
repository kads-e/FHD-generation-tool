import csv

with open("Grün_neu.txt", "r", encoding="utf-8", newline="") as in_file1, \
     open("Blau_neu.txt", "r", encoding="utf-8", newline="") as in_file2:
         

    reader_gruen = csv.reader(in_file1, delimiter=";")
    reader_blau = csv.reader(in_file2, delimiter=";")

    # Grün.txt in ein zweidimensionales Array einlesen
    for row in reader_gruen:
        if row:  # Leere Zeilen überspringen
            gruen.append([value.strip() for value in row])

    # Blau.txt in ein zweidimensionales Array einlesen
    for row in reader_blau:
        if row:
            blau.append([value.strip() for value in row])

kopfzeile_gruen = gruen[0]
daten_gruen = gruen[1:]

kopfzeile_blau = blau[0]
daten_blau = blau[1:]

print("\nInhalt von Grün.txt:")
print(kopfzeile_gruen)
if len(daten_gruen)>25:
    print(gruen[1:20])
    print("......")
else:
    print(daten_gruen)

print("\nInhalt von Blau.txt:")
print(kopfzeile_blau)
if len(daten_blau)>25:
    print(blau[1:20])
    print("......\n")
else:
    print(daten_blau)


