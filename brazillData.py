import _sqlite3 as SQ
import csv

data = []
fileName = "heightweight.csv"
dataFile = open("input_data/"+fileName, newline="")
fileRead = csv.DictReader(dataFile)





newCSV = open("output_data/"+"clean"+fileName, "w", newline="")
writtenCSV = csv.DictWriter(newCSV, fieldnames=fileRead.fieldnames)
dataFile.close()
writtenCSV.writeheader()
for entry in data:
    writtenCSV.writerow(entry)
newCSV.close()