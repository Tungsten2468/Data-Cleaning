import matplotlib.pyplot as plt
patients = [
    {"id": 1, "age": "45", "gender": "M", "height_cm": "180", "weight_kg": "82", "smoker": "Yes", "diabetes": "No"},
    {"id": 2, "age": "31", "gender": "Female", "height_cm": "165", "weight_kg": "61", "smoker": "N", "diabetes": "No"},
    {"id": 3, "age": "", "gender": "male", "height_cm": "172", "weight_kg": "75", "smoker": "yes", "diabetes": "Unknown"},
    {"id": 4, "age": "52", "gender": "F", "height_cm": "160", "weight_kg": "", "smoker": "No", "diabetes": "Yes"},
    {"id": 5, "age": "27", "gender": "female", "height_cm": "168", "weight_kg": "58", "smoker": "False", "diabetes": "No"},
    {"id": 6, "age": "45", "gender": "Male", "height_cm": "180", "weight_kg": "82", "smoker": "Yes", "diabetes": "No"},  # duplicate
    {"id": 7, "age": "39", "gender": "M", "height_cm": "175", "weight_kg": "abc", "smoker": "No", "diabetes": "No"},
    {"id": 8, "age": "22", "gender": "F", "height_cm": "158", "weight_kg": "54", "smoker": "Y", "diabetes": "No"},
    {"id": 9, "age": "67", "gender": "Female", "height_cm": "162", "weight_kg": "70", "smoker": "No", "diabetes": "Yes"},
    {"id":10, "age": "29", "gender": "Male", "height_cm": "", "weight_kg": "77", "smoker": "yes", "diabetes": "No"},
    {"id":11, "age": "54", "gender": "female", "height_cm": "170", "weight_kg": "68", "smoker": "No", "diabetes": "yes"},
    {"id":12, "age": "41", "gender": "M", "height_cm": "182", "weight_kg": "90", "smoker": "0", "diabetes": "No"},
    {"id":13, "age": "36", "gender": "F", "height_cm": "159", "weight_kg": "60", "smoker": "1", "diabetes": "No"},
    {"id":14, "age": "18", "gender": "Male", "height_cm": "177", "weight_kg": "69", "smoker": "No", "diabetes": ""},
    {"id":15, "age": "73", "gender": "female", "height_cm": "155", "weight_kg": "64", "smoker": "No", "diabetes": "Yes"},
    {"id":16, "age": "34", "gender": "m", "height_cm": "181", "weight_kg": "83", "smoker": "No", "diabetes": "No"},
    {"id":17, "age": "50", "gender": "FEMALE", "height_cm": "166", "weight_kg": "71", "smoker": "YES", "diabetes": "NO"},
    {"id":18, "age": "44", "gender": "Male", "height_cm": "174", "weight_kg": "79", "smoker": "", "diabetes": "No"},
    {"id":19, "age": "60", "gender": "F", "height_cm": "161", "weight_kg": "67", "smoker": "No", "diabetes": "Yes"},
    {"id":20, "age": "28", "gender": "female", "height_cm": "169", "weight_kg": "59", "smoker": "No", "diabetes": "No"},
    {"id":21, "age": "47", "gender": "Male", "height_cm": "183", "weight_kg": "85", "smoker": "Y", "diabetes": "No"},
    {"id":22, "age": "33", "gender": "female", "height_cm": "164", "weight_kg": "63", "smoker": "N", "diabetes": "No"},
    {"id":23, "age": "", "gender": "F", "height_cm": "170", "weight_kg": "66", "smoker": "Unknown", "diabetes": "No"},
    {"id":24, "age": "56", "gender": "male", "height_cm": "178", "weight_kg": "88", "smoker": "Yes", "diabetes": "Yes"},
    {"id":25, "age": "40", "gender": "Female", "height_cm": "", "weight_kg": "72", "smoker": "No", "diabetes": "No"},
    {"id":26, "age": "24", "gender": "M", "height_cm": "176", "weight_kg": "68", "smoker": "false", "diabetes": "No"},
    {"id":27, "age": "65", "gender": "F", "height_cm": "157", "weight_kg": "73", "smoker": "Yes", "diabetes": "YES"},
    {"id":28, "age": "38", "gender": "Female", "height_cm": "171", "weight_kg": "NaN", "smoker": "No", "diabetes": "No"},
    {"id":29, "age": "51", "gender": "male", "height_cm": "179", "weight_kg": "81", "smoker": "1", "diabetes": "No"},
    {"id":30, "age": "30", "gender": "f", "height_cm": "163", "weight_kg": "57", "smoker": "0", "diabetes": "No"},
    {"id":31, "age": "42", "gender": "Male", "height_cm": "185", "weight_kg": "91", "smoker": "Yes", "diabetes": "No"},
    {"id":32, "age": "37", "gender": "Female", "height_cm": "167", "weight_kg": "65", "smoker": "", "diabetes": "No"},
    {"id":33, "age": "49", "gender": "M", "height_cm": "173", "weight_kg": "76", "smoker": "No", "diabetes": "unknown"},
    {"id":34, "age": "26", "gender": "Female", "height_cm": "168", "weight_kg": "61", "smoker": "No", "diabetes": "No"},
    {"id":35, "age": "58", "gender": "FEMALE", "height_cm": "160", "weight_kg": "74", "smoker": "YES", "diabetes": "Yes"},
    {"id":36, "age": "21", "gender": "male", "height_cm": "182", "weight_kg": "", "smoker": "No", "diabetes": "No"},
    {"id":37, "age": "63", "gender": "F", "height_cm": "156", "weight_kg": "69", "smoker": "Y", "diabetes": ""},
    {"id":38, "age": "46", "gender": "Male", "height_cm": "177", "weight_kg": "84", "smoker": "No", "diabetes": "Yes"},
    {"id":39, "age": "35", "gender": "female", "height_cm": "165", "weight_kg": "62", "smoker": "n", "diabetes": "No"},
    {"id":40, "age": "45", "gender": "M", "height_cm": "180", "weight_kg": "82", "smoker": "Yes", "diabetes": "No"}  # duplicate of id=1
]

def convertToInt(value):
    try:
        convertedValue = value
        convertedValue = int(value)
        return convertedValue
    except:
        return "Unknown"

#convert values to integer:
for i in patients:
    i['age'] = convertToInt(i['age'])
    i['height_cm'] = convertToInt(i['height_cm'])
    i['weight_kg'] = convertToInt(i['weight_kg'])

#fix male/female
for i in patients:
    values = list(i.values())
    gender = values[2]
    if values != 'Male' or values !='Female':
        if gender[0] == 'M'or gender[0] =='m':
            gender = 'Male'
            i['gender']=gender
        elif gender[0] == 'F' or gender[0] =='f':
            gender = 'Female'
            i['gender']=gender
    
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

#fix smoker/diabetes
def checkFirstChar(word):
    if(len(word) > 0):
        if(word[0] == 'y' or word[0] == 'Y' or word[0] == '1'):
            return "Yes"
        elif(word[0] == 'n' or word[0] == 'N' or word[0] == "0"):
            return "No"
    return "Unknown"

for i in patients:
    values = list(i.values())
    smoke = values[5]
    diabete= values[6]
    
    i['smoker'] = checkFirstChar(smoke)
    i['diabetes'] = checkFirstChar(diabete)

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

#for additional filters
'''def getPercentage(v, targetValue, v2 = None, targetValue2 = None):
    hasAdditionalParameter = v2 != None
    totalEntries = 0
    totalYes = 0
    for entry in range(len(patients)):
        if(hasAdditionalParameter):
            if(patients[entry][v2] == targetValue2):
                totalEntries += 1
        else:
            totalEntries += 1
    for i in patients:
        if i[v] == targetValue:
            totalYes += 1
    percentage = (totalYes/totalEntries) * 100
    #truncate if needed
    percentage = str(percentage)
    if(len(percentage) > 4):
        percentage = percentage[0:5]
    if(hasAdditionalParameter):
        analysis = targetValue2 + " "+ targetValue+" "+v+"(s): "+percentage+"%"
    else:
        analysis = targetValue+" "+v+"(s): "+percentage+"%"
    return analysis     
    
print(getPercentage("gender", "Female", "smoker", "Yes"))'''
def percentGend(g ,gender):
    totalYes =0
    genderYes=0
    for i in patients:
        if i[g] =='Yes'and i['gender'] == gender:
            totalYes +=1
            genderYes +=1
        if i[g] =='Yes'and not i['gender'] ==gender:
            totalYes +=1
    percentage =(genderYes/totalYes)*100
    percentage= str(percentage)
    if(len(percentage)>4):
        percentage = percentage[0:5]
    analysis = gender+' '+g+" percentage:"+percentage+"%" 
    return analysis
print(patients)

def plotgraph(g):
    for i in patients:
        if i[g] =='Yes'and i['gender'] == "Male":
            if i['weight_kg'] == 'Unknown'or i['height_cm'] =='Unknown':
                continue
            else:
                x = i['weight_kg']
                y = i['height_cm']
                line1 = plt.scatter(x,y,color = 'blue', marker= 'o',label='Male')
        elif i[g] =='Yes'and i['gender'] == "Female":
            if i['weight_kg'] == 'Unknown'or i['height_cm'] =='Unknown':
                continue
            else:
                x = i['weight_kg']
                y = i['height_cm']
                line2 = plt.scatter(x,y,color = 'pink', marker= 'o',label='Female')
    plt.xlabel('Weight in kg')  
    plt.ylabel('Height in cm')
    plt.title(g+'(s)')
    plt.legend(loc = "lower right", handles = [line1, line2], labels=["Male", "Female"])
    plt.show()

def plotBar(g, targetValue):
    barValues = [0,0,0,0,0,0]
    for i in patients: 
        try:
            if(i[g] == targetValue):     
                if i['age'] < 20:
                    barValues[0] += 1
                elif i['age'] >= 20 and i['age'] <= 30:
                    barValues[1] += 1
                elif i['age'] >= 30 and i['age'] <= 40:
                    barValues[2] += 1
                elif i['age'] >= 40 and i['age'] <= 50:
                    barValues[3] += 1
                elif i['age'] >= 50 and i['age'] <= 60:
                    barValues[4] += 1
                elif i['age'] >= 60:
                    barValues[5] += 1
        except:
            continue

    categories = ['>20', '20-30', '30-40', '40-50', '50-60', '60<']

    plt.bar(categories, barValues)
    plt.title(g+"(s) among age groups")
    plt.xlabel("Age Group")
    plt.ylabel("Amount")
    #plt.bar(['>20', '20-30', '30-40', '40-50', '50-60', '60<'],[category], totalYes)


#plotgraph('smoker')
#plotgraph('diabetes')
plotBar('smoker', 'Yes')
plt.show()
plotBar('diabetes', 'Yes')
plt.show()