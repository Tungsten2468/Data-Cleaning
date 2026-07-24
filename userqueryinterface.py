import _sqlite3 as SQ
import sys
import pandas as pan
import csv
import os
from enum import Enum
import textwrap

class dataType(Enum):
    NUMERICAL = 0
    CATEGORICAL = 1

fileName = "final_reports"
dataConnect = SQ.connect(f"syn_output_data/{fileName}.db")
cursor = dataConnect.cursor()

print(f"\nYou are querying {fileName}.\n")
print("You may query the following tables (name or #): \n")

userQuery = 'SELECT name FROM sqlite_master WHERE type="table"'
#-----FUNCTIONS-----
def selectionHandler():
    global colSelection
    restultingInfo = []
    optionList = getColumns()
    colSelection = []
    showOptions(optionList)
    selection = input("\nSelect the column(s) and limit you want to work with (using the # on the left side) in the following format:\n"
    "[column_number,column_number,...,(limit)]\n"
    "Input column number as 'A' to view all columns and () as 0 for no limit\n")
    while(contains(selection, '(') == False and contains(selection, ')') == False):
        print("You didn't specify a limit! Please specify a limit by enclosing it in commas.\n")
        selection = input("\nSelect the column(s) and limit you want to work with (using the # on the left side) in the following format:\n"
            "[column_number,column_number,...,(limit)]\n"
            "Input column number as 'A' to view all columns and () as 0 for no limit\n")
    charIndex = 0
    originalSelection = selection #Keep record of the selection made for later editing purposes
    selection = list(selection)
    limit = '' #keep as string initially so numbers can be concactenated
    for char in selection: #first loop extracts the limit, wherever it was specified in the string
        if(char == '('):
            start = selection.index('(') + 1
            end = selection.index(')', start)
            limit = ''.join(selection[start:end])
            del selection[start-1:end+1]
            break 
    if(char.upper() == 'A'):
        colSelection = optionList   
    else:
        colSelection = parseTextToList(selection, optionList)
    restultingInfo.append(colSelection)
    restultingInfo.append(limit)
    restultingInfo.append(originalSelection)
    return restultingInfo 

def contains(container, targetElement):
    for i in container:
        if(i == targetElement):
            return True
    return False

def csvMaker(fileName, columns ,tableName):
    if isinstance(colSelection, (tuple, list)):
        columns_str = ", ".join(colSelection)
    else:
        columns_str = colSelection

    clean_columns = columns_str.replace("'", "").replace('"', "")
    folderpath ="queryfolder/"+fileName+".csv"
    cursor.execute(f"SELECT {columns_str} FROM '{tableName}'")


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

def begin():
    global activeUser
    global optionList
    global limit
    global infos
    optionList = getTables()
    showOptions(optionList)
        
    print("\n")
    activeUser = input("What table would you like to query? (type 'exit' to exit)\n")
    if(activeUser[0].isdigit()):
        activeUser = optionList[int(activeUser)]
    else:
        activeUser = activeUser
    
    checkActive()

    global infos
    infos = selectionHandler()
    actionChoice()

def actionChoice():
    print(f"\nYou are querying {activeUser} in {fileName}")
    #Remember that selection handler returns the following in the exact order: [columns selected, limit, original selection]
    
    optionList = getColumns()
    action = input(f"What would you like to do with {len(infos[0])} column(s)?\n" \
        "(V)view, (S)select, (C)calculations, (F)filter, (E)edit my selection, (SS)save to .CSV, (Q)quit\n")

    while action.upper() != 'Q':
        print("\n")
        
        if action.upper()[0] == 'A':
            userQuery = f'SELECT * FROM {activeUser}'
            cursor.execute(userQuery)
            data = cursor.fetchall()
            for row in data:
                print(row) 
            
            newQuery()
            break
            
        if action.upper()[0] == 'V':
            print(createColumnTable(infos[0], activeUser, infos[1], 'n'))

        if action.upper().startswith('C'):
            calculation = input('What would you like to Calculate?:\n'
                                "(T)Total, (H)Highest, (L)Lowest, (A)Average, (M)Median, (B)Back:\n")
            
            calc_type = calculation.upper() if calculation else ''
            active_columns = infos[0] if isinstance(infos, list) and isinstance(infos[0], list) else infos

            numeric_columns = []
            text_columns = []

            for column in active_columns:
                cursor.execute(f'SELECT typeof("{column}") FROM "{activeUser}" WHERE "{column}" IS NOT NULL LIMIT 1;')
                result = cursor.fetchone()
                col_type = result[0] if result else 'null'
                
                if col_type in ('integer', 'real'):
                    numeric_columns.append(column)
                else:
                    text_columns.append(column)

            if text_columns and calc_type in ('T', 'H', 'L', 'A', 'M'):
                print("\n**The following text columns cannot be calculated and will be skipped:**")
                for col in text_columns:
                    print(f" - {col}")
                print()

            if calc_type == 'T':
                for column in numeric_columns:
                    cursor.execute(f'SELECT SUM("{column}") FROM "{activeUser}"')
                    total_stock = cursor.fetchone()[0]
                    print(f"Total of {column}: {total_stock}")
                break

            elif calc_type == 'H':
                for column in numeric_columns: 
                    cursor.execute(f'SELECT MAX("{column}") FROM "{activeUser}"')
                    maxstock = cursor.fetchone()[0]
                    print(f"Max of {column}: {maxstock}")
                break

            elif calc_type == 'L':
                for column in numeric_columns: 
                    cursor.execute(f'SELECT MIN("{column}") FROM "{activeUser}"')
                    minstock = cursor.fetchone()[0]
                    print(f"Lowest of {column}: {minstock}")
                break

            elif calc_type == 'A':
                for column in numeric_columns: 
                    cursor.execute(f'SELECT ROUND(AVG("{column}"), 2) FROM "{activeUser}"')
                    avgStock = cursor.fetchone()[0]
                    print(f"Average of {column}: {avgStock}")
                break

            elif calc_type == 'B':
                action = input(f"What would you like to do with {len(infos)} column(s)?\n"
                            "(V)view, (C)calculations, (F)find range, (E)edit my selection, (Q)quit: ")
                
            action =''
                
        if action.upper().startswith('E'):       
                while True:
                    newOptions = getColumns()
                    showOptions(newOptions)
                    print(f"Current Selection: {infos[2]}")
                    edit = input("What edit would you like to perform?\n(A)Add, (R)Remove, (L)Change limit, (N)New Query or (B)Back:\n").upper()
                    
                    if edit.startswith('B'):
                        action = input(f"What would you like to do with {len(infos[0])} column(s)?\n" \
                        "(V)view, (C)calculations, (F)find range, (E)edit my selection, (Q)quit")
                        break
                        
                    elif edit.startswith('R'):
                        print(colSelection)
                        removal = input("Enter column indices to remove (separated by commas):\n")
                        indices = sorted([int(i) for i in removal.split(',') if i.strip().isdigit()], reverse=True)
                        for idx in indices:
                            if 0 <= idx < len(infos[0]):
                                infos[0].pop(idx)
                        newSelecton = ''
                        for i in infos[0]:
                            newSelecton = newSelecton + str(newOptions.index(i))
                            if(infos[0].index(i) != len(infos[0]) - 1):
                                newSelecton = newSelecton + ','
                        newSelecton = newSelecton + f'({infos[1]})'
                        infos[2] = newSelecton
                    elif edit.startswith('L'):
                        newLimit = input('Enter your new limit (no formatting, just digits)\n:')
                        infos[1] = newLimit
                        edit =''
                    elif edit.startswith('N'):
                        edit =''
                        newQuery()
                    elif edit.startswith('A'):
                                          
                        for x in colSelection:
                            for y in optionList:
                                if x == y:
                                    optionList.remove(x)

                        showOptions(optionList)
                        print(f'Current Selection:{colSelection}')
                        new_col = input("Enter the name of the column to add:\n").strip()
                        if new_col:
                            infos[0].append(new_col)
                        newSelecton = ''
                        for i in infos[0]:
                            newSelecton = newSelecton + str(newOptions.index(i))
                            if(infos[0].index(i) != len(infos[0]) - 1):
                                newSelecton = newSelecton + ','
                        newSelecton = newSelecton + f'({infos[1]})'
                        infos[2] = newSelecton 
        if action.upper().startswith('S'):
                csvName = input('Please name your .CSV file:\n')
                print("Saving...")
                csvMaker(csvName,colSelection,activeUser)
                print(f"{csvName}.csv has been save at {os.path.dirname("queryfolder/"+csvName+".csv")}\n")
                action = ''
        if action.upper().startswith('F'):
            filterBy = input('What would you like to filter by?' \
            '(C)category, (R)range, (N)number, (B)back')
            while filterBy.upper()[0] != 'B':
                if(filterBy.upper().startswith('C')):
                    print(f"Here are the categories you can sort by (based on your selected columns):\n")
                    possibleCategories = []
                    for i in colSelection:
                        if(checkDataType(i, activeUser) == dataType.CATEGORICAL):
                            possibleCategories.append(i)
                    possibleCategories = list(possibleCategories)
                    showOptions(possibleCategories)
                    category = input('Select your category by number:')
                    possibleFilters = list(set([d[0] for d in cursor.execute(f"SELECT {possibleCategories[int(category)]} FROM {activeUser}")]))
                    showOptions(possibleFilters)
                    chosenFilter = input('Choose what to filter by with number:\n')
                    userQuery = f'SELECT * FROM {activeUser} WHERE {possibleCategories[int(category)]}= "{possibleFilters[int(category)]}"'
                    print(f'Filtered your selection by {possibleCategories[int(category)]}.\n')
                    filtered = pan.read_sql(userQuery, dataConnect)
                    print(filtered)
                    break

                    
            
    action = ''
    newQuery()
    print("You have quit.")
    sys.exit()

def compoundOptions(listOfOptions, table):
    print(listOfOptions)
    dictList = []
    dictID = 0
    for col in listOfOptions:
        query = f'SELECT {col} FROM {table}'
        possibleVals = list(set(row[0] for row in cursor.execute(query).fetchall()))
        optionDictionary = {i: v for i, v in enumerate(possibleVals)}
        print(f"\nValues for {col}, (DictID: {dictID})")
        all_vals = ", ".join(str(v) for v in optionDictionary.values())
        dictList.append(all_vals)
        wrapped = textwrap.fill(all_vals, width=80)
        print(wrapped)
        dictID += 1
    return dictList
        

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

def checkActive():
    if activeUser =='exit':
        sys.exit()

def getTables():
    tableList = []
    for i in cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';").fetchall():
        tableList.append(i[0])
    return tableList

def newQuery():
        con = input('\nAre you sure you want to make a new query?(Y/N):\n')
        if con.upper()[0] == 'N':
            return
        if con.upper()[0] == 'Y':
            begin()

def getColumns():
    tableColumns=f"PRAGMA table_info({activeUser});"
    cursor.execute(tableColumns)

    raw_results = cursor.fetchall()
    column_names = [col[1] for col in raw_results]
    return column_names

def showOptions(options):
        for i in options:
            print (options.index(i), i)

activeUser = ''

def checkExists(input, checkAgainst):
    if(input == 'exit'):
        return True
    for i in checkAgainst:
        if(i == input):
            return True
    return False

def createColumnTable(listOfColumns, table, rowLimit, unique):
    rowLimit = int(rowLimit)

    pan.set_option("display.max_rows", None)
    pan.set_option("display.max_columns", None)

    data = {}

    for col in listOfColumns:
        if rowLimit != 0:
            rows = cursor.execute(f"SELECT {col} FROM {table} LIMIT {rowLimit}").fetchall()
        else:
            rows = cursor.execute(f"SELECT {col} FROM {table}").fetchall()

        vals = [r[0] for r in rows]

        if unique == 'u':
            vals = list(dict.fromkeys(vals)) 

        data[col] = vals

    columnTable = pan.DataFrame(dict([(col, pan.Series(vals)) for col, vals in data.items()]))

    return columnTable


def assignGlobalIDs(pdDataFrame):
    valueToID = {}
    currentID = 1

    for col in pdDataFrame.columns:
        newVals = []
        for val in pdDataFrame[col]:
            if val not in valueToID:
                valueToID[val] = currentID
                currentID += 1
            newVals.append(valueToID[val])
        pdDataFrame[col] = newVals

    return pdDataFrame, valueToID




#-----PROGRAM-----
while activeUser != "exit":
    begin()

    checkActive()
    










