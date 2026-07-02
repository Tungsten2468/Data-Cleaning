import csv
import matplotlib.pyplot as plt
import math

data = []
fileName = "heightweight.csv"
dataFile = open("input_data/"+fileName, newline="")
fileRead = csv.DictReader(dataFile)

for entry in fileRead:
    data.append(entry)

dataFile.close()

#variables
under =0
norm=0
over=0
obs=0

#convert values to integer:
'''for i in data:
    if i['Age'] == '' or i['Age']== 'nan':
        i['Age']= 'N/A'
    else:
        x = int(float(i['Age']))
        i['Age']= x'''

#handle all empty cells:
for i in data:
    keys = list(i.keys())
    for e in keys:
        if i[e] == '' or i[e] == 'nan':
            i[e] = 'N/A'

def newColumn(columnName):
    fileRead.fieldnames.append(columnName)

#report rows and columns
def reportRowsColumns():
    totalRows = 0
    totalColumns = 0
    for i in data: #count rows
        totalRows += 1
    for i in fileRead.fieldnames: 
        totalColumns += 1
    return "Rows: "+str(totalRows)+"; Columns:"+str(totalColumns)

#check data types
def checkEveryDataType():
    for i in data:
        values = list(i.values())
        for e in range(len(values)):
            print(values[e]+" is "+str(type(values[e])))

#delete dupes
filteredData = []
def isDupe(comparing):
    for e in filteredData:
        compValues = list(e.values())
        if compValues[1:] == comparing:
            return True
        else:
            return False
for i in data:
    dataToAdd = list(i.values())
    if(not isDupe(dataToAdd[1:])):
        filteredData.append(i)
    else:
        print("ignoring duplicate ",dataToAdd)

data = filteredData

#fix binary values
def checkFirstChar(word):
    if(len(word) > 0):
        if(word[0] == 'y' or word[0] == 'Y' or word[0] == '1'):
            return "Yes"
        elif(word[0] == 'n' or word[0] == 'N' or word[0] == "0" and word[0] != 'N/A'):
            return "No"
    return "N/A"

def demicalfix(valueToFix):
    valueToFix = float(valueToFix)
    valueToFix = round(valueToFix,2)
    return valueToFix


def getPercentage(key, targetValue):
    totalEntries = 0
    totalYes = 0
    for entry in range(len(data)):
        totalEntries += 1
    for i in data:
        if i[key] == targetValue:
            totalYes += 1
    percentage = (totalYes/totalEntries) * 100
    #truncate if needed
    percentage = str(percentage)
    if(len(percentage) > 4):
        percentage = percentage[0:5]
    analysis = targetValue+" percentage: "+percentage+"%"
    return analysis 

def inchToCm(valueToConvert):
    valueToConvert = float(valueToConvert) * 2.54
    valueToConvert=round(valueToConvert , 2)
    return valueToConvert

def poundToKg(valueToConvert):
    valueToConvert = float(valueToConvert) * 0.453592
    valueToConvert=round(valueToConvert , 2)
    return valueToConvert

#height must be in cm becuase from cm it is converted to meters
#weight must be in kg
def calcBMI(height, weight):
    bmi = float(weight) / ((float(height) / 100) * (float(height) / 100))
    return bmi

def categorizeBMI(BMI):
    category = ""
    global under,norm,over,obs
    if(BMI < 18.5):
        category = 'Underweight'
        under +=1
    elif(BMI >= 18.5 or BMI <= 24.9):
        category = 'Normal'
        norm +=1
    elif(BMI >= 25.0 or BMI <= 29.9):
        category = 'Overweight'
        over +=1
    elif(BMI >= 30):
        category = 'Obese'
        obs+=1
    
    return category  



#calc mean
def calcMean(key):
    entryAmnt = 0
    sum = 0
    for i in data:
        try:
            sum += float(i[key])
            entryAmnt += 1
        except:
            return "Value must only contain numbers, not text"
        mean = round((sum/entryAmnt),2)
    return "Mean "+key+" :"+str(mean)

def calcMean(key):
    entryAmnt = 0
    sum = 0
    for i in data:
        try:
            sum += float(i[key])
            entryAmnt += 1
        except:
            return "Value must only contain numbers, not text"
        mean = round((sum/entryAmnt),2)
    return "Mean "+key+" : "+str(mean)


def histoPlot(g):
    mean =calcMean(g)
    xVals = []
    for i in data:
        xVals.append(i[g])
    plt.hist(xVals)
    plt.title(mean)
    plt.ylabel('Amount of People')
    plt.xlabel(g)
    plt.show()

newColumn("Height(Centimeters)")
newColumn("Weight(Kilograms)")
newColumn("BMI")
newColumn("BMI Category")

#compute height in cm, weight in kg and BMI
for i in data:
    i['Height(Centimeters)'] = inchToCm(i['Height(Inches)'])
    i['Weight(Kilograms)'] = poundToKg(i['Weight(Pounds)'])
    i['BMI'] = calcBMI(i['Height(Centimeters)'], i['Weight(Kilograms)'])
    i['BMI Category'] = categorizeBMI(i['BMI'])
print(reportRowsColumns())


for i in data:
    i['Height(Inches)'] = demicalfix(i['Height(Inches)'])
    i['Weight(Pounds)'] = demicalfix(i['Weight(Pounds)'])
    i['BMI'] = demicalfix(i['BMI'])

#checkEveryDataType()

print ('Underweights:',under
        ,'\nNormal:',norm,
        '\nOverweight:',over,
        '\nObese',obs)

histoPlot('Weight(Pounds)')
histoPlot('Weight(Kilograms)')
histoPlot('Height(Centimeters)')
histoPlot('Height(Inches)')
histoPlot('BMI')
print(reportRowsColumns())
print(calcMean('BMI'))
print(calcMedian('BMI'))


newCSV = open("output_data/"+"clean"+fileName, "w", newline="")
writtenCSV = csv.DictWriter(newCSV, fieldnames=fileRead.fieldnames)
dataFile.close()
writtenCSV.writeheader()
for entry in data:
    writtenCSV.writerow(entry)
newCSV.close()