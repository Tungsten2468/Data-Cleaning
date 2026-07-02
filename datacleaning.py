import csv

import math

patients = []
dataFile = open("input_data/uncleanmedical.csv", newline="")
fileRead = csv.DictReader(dataFile)

for entry in fileRead:
    patients.append(entry)

dataFile.close()


#convert values to integer:
for i in patients:
    if i['Age'] == '' or i['Age']== 'nan':
        i['Age']= 'N/A'
    else:
        x = int(float(i['Age']))
        i['Age']= x


#fix male/female
for i in patients:
    values = list(i.values())
    gender = values[2]
    if gender != 'Male' or gender !='Female':
        if gender[0] == 'M'or gender[0] =='m':
            gender = 'Male'
            i['Gender']=gender
        elif gender[0] == 'F' or gender[0] =='f':
            gender = 'Female'
            i['Gender']=gender
        elif gender =='nan' or len(gender) == 0:
            gender = 'N/A'
            i['Gender']=gender

#delete dupes
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

#fix binary values
def checkFirstChar(word):
    if(len(word) > 0):
        if(word[0] == 'y' or word[0] == 'Y' or word[0] == '1'):
            return "Yes"
        elif(word[0] == 'n' or word[0] == 'N' or word[0] == "0" and word[0] != 'nan'):
            return "No"
    return "Unknown"

for i in patients:
    values = list(i.values())
    smoke = values[6]
    
    i['Smoker'] = checkFirstChar(smoke)

#old one
def getPercentage(v):
    totalEntries = 0
    totalYes = 0
    for entry in range(len(patients)):
        totalEntries += 1
    for i in patients:
        if i[v] == "Yes":
            totalYes += 1
    percentage = (totalYes/totalEntries) * 100
    #truncate if needed
    percentage = str(percentage)
    if(len(percentage) > 4):
        percentage = percentage[0:5]
    analysis = v+"(s): "+percentage+"%"
    return analysis 

def getPercentage(key, targetValue):
    totalEntries = 0
    totalYes = 0
    for entry in range(len(patients)):
        totalEntries += 1
    for i in patients:
        if i[key] == targetValue:
            totalYes += 1
    percentage = (totalYes/totalEntries) * 100
    #truncate if needed
    percentage = str(percentage)
    if(len(percentage) > 4):
        percentage = percentage[0:5]
    analysis = targetValue+" percentage: "+percentage+"%"
    return analysis 

def percentGend(key, targetValue ,gender):
    totalYes =0
    genderYes=0
    for i in patients:
        if i[key] == targetValue and i['Gender'] == gender:
            totalYes +=1
            genderYes +=1
        if i[key] == targetValue and not i['Gender'] ==gender:
            totalYes +=1
    percentage =(genderYes/totalYes)*100
    percentage= str(percentage)
    if(len(percentage)>4):
        percentage = percentage[0:5]
    if(targetValue == 'Yes' or targetValue == 'No'): #appropriate message based off if answer is binary or specific
        analysis = gender+' '+key+" percentage:"+percentage+"%" 
    else:
        analysis = gender+' '+targetValue+" percentage:"+percentage+"%"  
    return analysis



newCSV = open("output_data/cleanedmedical.csv", "w", newline="")
writtenCSV = csv.DictWriter(newCSV, fieldnames=fileRead.fieldnames)
dataFile.close()
writtenCSV.writeheader()
for entry in patients:
    writtenCSV.writerow(entry)
newCSV.close()