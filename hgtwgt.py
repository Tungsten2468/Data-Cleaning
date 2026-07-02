import csv

import math

patients = []
dataFile = open("input_data/heightweight.csv", newline="")
fileRead = csv.DictReader(dataFile)

for entry in fileRead:
    patients.append(entry)

dataFile.close()

filteredPatients = []
def isDupe(comparing):
    for e in filteredPatients:
        compValues = list(e.values())
        if compValues[1:] == comparing:
            return True
        else:
            return False
for i in patients:
    patientToAdd = list(i.values())
    if(not isDupe(patientToAdd[1:])):
        filteredPatients.append(i)

patients = filteredPatients









newCSV = open("output_data/heightweight.csv", "w", newline="")
writtenCSV = csv.DictWriter(newCSV, fieldnames=fileRead.fieldnames)
dataFile.close()
writtenCSV.writeheader()
for entry in patients:
    writtenCSV.writerow(entry)
newCSV.close()
