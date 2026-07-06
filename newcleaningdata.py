import csv
import math
from typing import List
import matplotlib.pyplot as plt

data = []
fileName = "heightweight.csv"
dataFile = open("input_data/"+fileName, newline="")
fileRead = csv.DictReader(dataFile)

for entry in fileRead:
    data.append(entry)

dataFile.close()

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

    return mean

def calcMedian(key):
    inOrder = []
    for i in data:
        inOrder.append(i[key])
    inOrder.sort()
    median = 0
    print(len(inOrder))
    if(len(inOrder) % 2 == 0): #if list amount is even
        median = inOrder[int(len(inOrder)/2)]
        #middle2 = middle1 + 1
        #median = (middle1+middle2)/2
    elif(not len(inOrder) % 2 == 0): #if list amount is odd
        median = inOrder[int((len(inOrder) + 1)/2)]
    return median

def findMinMax(key, minMax):
    listOfValues = []
    for i in data:
        listOfValues.append(i[key])
    listOfValues.sort()
    if(minMax == "Min"):
        return "Min of "+key+" is: "+str(listOfValues[0])
    elif(minMax == "Max"):
        return "Max of "+key+" is: "+str(listOfValues[len(listOfValues) - 1])

def calcStandardDeviation(key):
    mean = calcMean(key)
    listOfValues = []
    for i in data:
        listOfValues.append(i[key])
    for value in listOfValues:
        value -= mean
        value *= value
    sum = 0
    for value in listOfValues:
        sum += value
    sum = sum/len(listOfValues) - 1
    stDev = math.sqrt(sum)
    return str(stDev)[:4]

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

def scatterPlot(g,l):
    xVals=[]
    yVals=[]
    for i in data:
        xVals.append(i[g])
        yVals.append(i[l])   
    x = str(len(xVals))
    plt.scatter(xVals,yVals,color='purple',alpha=0.1, marker='o') 
    plt.title('Amount of people:'+ x )
    plt.ylabel(l)
    plt.xlabel(g)
    plt.show()

def BMIbar(g):

    xVals=['Underweight','Normal','Overweight','Obese']
    yVals=[]
    underList =[]
    normList=[]
    overList=[]
    obsList=[]
    for i in data:
        BMI = i['BMI']
        if(BMI < 18.5):
            underList.append(i[g])
        elif(BMI >= 18.5 or BMI <= 24.9):
            normList.append(i[g])
        elif(BMI >= 25.0 or BMI <= 29.9):
            overList.append(i[g])
        elif(BMI >= 30):
            obsList.append(i[g])
    Lists= [underList,normList,overList,obsList]
    for x in Lists:
        total= 0
        length=0
        for p in x:
            total= total+p
            length += 1
        if length ==0:
            avg =0
        else:
            avg= round((total/length),2)
        yVals.append(avg)
    plt.bar(xVals,yVals)
    plt.title('Average '+g+' in BMI catagories')
    plt.ylabel('Average '+g)
    plt.xlabel('BMI category')
    plt.show()
   
    

'''
histoPlot('Weight(Pounds)')
histoPlot('Weight(Kilograms)')
histoPlot('Height(Centimeters)')
histoPlot('Height(Inches)')
histoPlot('BMI')

scatterPlot('Height(Inches)','Weight(Pounds)')
scatterPlot('Height(Centimeters)','Weight(Kilograms)')
'''

    
BMIbar('Weight(Pounds)')
BMIbar('Weight(Kilograms)')
BMIbar('Height(Centimeters)')
BMIbar('Height(Inches)')

print(reportRowsColumns())
print("Mean BMI is: "+str(calcMean('BMI')))
print("Median BMI is: "+str(calcMedian('BMI')))
print(findMinMax('Height(Inches)', 'Min'))
print(findMinMax('Height(Inches)', 'Max'))
print("Standard Deviation of BMI is: "+str(calcStandardDeviation('BMI')))


newCSV = open("output_data/"+"clean"+fileName, "w", newline="")
writtenCSV = csv.DictWriter(newCSV, fieldnames=fileRead.fieldnames)
dataFile.close()
writtenCSV.writeheader()
for entry in data:
    writtenCSV.writerow(entry)
newCSV.close()