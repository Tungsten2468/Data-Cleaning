import _sqlite3 as SQ
import sys
import pandas as pan
import csv
import os
from enum import Enum
from main import dataConnect
from main import cursor
from main import fileName

from pipeline import beginQueryCreation as returnToStart
#from pipeline.beginQueryCreation import queryTable

pan.set_option("display.max_rows", None)
pan.set_option("display.max_columns", None)

class dataType(Enum):
    NUMERICAL = 0
    CATEGORICAL = 1

def contains(container, targetElement):
    for i in container:
        if(i == targetElement):
            return True
    return False

def csvMaker(cursor, fileName, query):
    if isinstance(query.columnNames, (tuple, list)):
        columns_str = ", ".join(query.columnNames)
    else:
        columns_str = query.columnNames

    clean_columns = columns_str.replace("'", "").replace('"', "")
    folderpath ="queryfolder/"+fileName+".csv"
    cursor.execute(f"SELECT {columns_str} FROM '{query.tableName}'")


    with open(folderpath, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
    

        headers = [description[0] for description in cursor.description]
        writer.writerow(headers)
    

        writer.writerows(cursor.fetchall())

def viewCSV(filename):
    data = []
    dataFile = open(f"queryfolder/"+filename+'.csv', newline="")
    fileRead = csv.DictReader(dataFile)

    for entry in fileRead:
        data.append(entry)

    dataFile.close()
    for g in data:
        print(g)
        
def parseTextToList(stringToParse, options):
    result = []
    for char in stringToParse: #second loop extract column numbers
        if(char.isdigit()):
            result.append(options[int(char)])
        elif(stringToParse == ',' or stringToParse == ' '):
            continue
        '''elif(char.upper() == 'A'):
            colSelection = options'''
    return result   

def checkDataType(column, table):
    typeOfData = dataType.NUMERICAL #numerical data is default
    rawData = cursor.execute(f'SELECT {column} FROM {table}').fetchall()
    dataToCheck = [d[0] for d in rawData]
    if type(dataToCheck[0]) == str:
        typeOfData = dataType.CATEGORICAL
    return typeOfData

def checkActive(queryTable):
    if queryTable =='exit':
        sys.exit()

def getTables():
    tableList = []
    for i in cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';").fetchall():
        tableList.append(i[0])
    return tableList

def newQuery():
        con = input('\nAre you sure you want to make a new query? You will lose this one if you do(Y/N):\n')
        if con.upper()[0] == 'N':
            return
        if con.upper()[0] == 'Y':
            returnToStart.begin()

def getColumns(tableName):
    tableColumns=f"PRAGMA table_info('{tableName}');"
    cursor.execute(tableColumns)

    raw_results = cursor.fetchall()
    column_names = [col[1] for col in raw_results]
    return column_names

def showOptions(options):
    for idx, val in enumerate(options):
        print(idx, val)

def checkExists(input, checkAgainst):
    if(input == 'exit'):
        return True
    for i in checkAgainst:
        if(i == input):
            return True
    return False

def whitespace():
    print(" ")