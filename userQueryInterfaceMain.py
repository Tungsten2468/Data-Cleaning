import _sqlite3 as SQ
import sys
import pandas as pan
import csv
import os
from enum import Enum
import textwrap

class userQuery():
    def __init__(self, tableName, columnNames, limit, stringSelection, SQLconnection):
        self.tableName = tableName
        self.columnNames = columnNames
        self.limit = limit
        self.SQLconnection = SQLconnection
        self.stringSelection = stringSelection #the format in which the user enters the initial query (0,2,4(90))
        
        if(self.limit != 0):
            self.stringQuery = f"SELECT * FROM {self.tableName} LIMIT {limit}"
        else:
            self.stringQuery = f"SELECT * FROM {self.tableName}"
        self.dataFrame = pan.read_sql_query(self.stringQuery, self.SQLconnection)
    def runQuery(self, cursor):
        result = cursor.execute(self.stringQuery, self.SQLconnection).fetchall()

    def calculate(self, column, calc):
        df = self.dataFrame
        if(calc == 'A'): #Average
            return df[column].mean()
        if(calc == 'M'): #Median
            return df[column].median()
        if(calc == 'T'): #Total
            return df[column].sum()
        if(calc == 'H'): #Highest(max)
            return df[column].max()
        if(calc == 'L'): #Lowest(min)
            return df[column].min()

    def totalCategorical(self, column, targetVal):
        df = self.dataFrame
        return (df[column] == targetVal).sum()

    def filterCategorical(self, column, targetValue):
        df = self.dataFrame
        #change the actual dataframe itself
        self.dataFrame = df[df[column] == targetValue]

class dataType(Enum):
    NUMERICAL = 0
    CATEGORICAL = 1

#-----SETUP-----
pan.set_option("display.max_rows", None)
pan.set_option("display.max_columns", None)
fileName = "final_reports"
dataConnect = SQ.connect(f"syn_output_data/{fileName}.db")
cursor = dataConnect.cursor()

print(f"\nYou are querying {fileName}.\n")
print("You may query the following tables (name or #): \n")

uQuery = 'SELECT name FROM sqlite_master WHERE type="table"'
#-----FUNCTIONS-----
def selectionHandler(queryTable):
    
    restultingInfo = []
    optionList = getColumns(queryTable)
    colSelection = []
    showOptions(optionList)
    selection = input("\nSelect the column(s) and limit you want to work with (using the # on the left side) in the following format:\n"
    "[column_number,column_number,...,(limit)]\n"
    "Input column number as 'A' to view all columns and () as 0 for no limit\n")
    while not contains(selection, '(') or not contains(selection, ')'):
        print("You didn't specify a limit! Please specify a limit by enclosing it in parenthesis ().\n")
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
            selection = selection[:start-1] + selection[end+1:]
            break 
    if 'A' in originalSelection.upper():
        colSelection = optionList
    else:
        try:
            colSelection = parseTextToList(selection, optionList)
        except:
            print("Your selection was structured incorrectly. Try again.")
            return selectionHandler(queryTable)
    for char in selection:
        if char.isdigit():
            idx = int(char)
            if idx < 0 or idx >= len(optionList):
                print("Your selection does not exist. Please enter only available numbers.")
                return selectionHandler(queryTable)
    restultingInfo.append(colSelection)
    restultingInfo.append(limit)
    restultingInfo.append(originalSelection)
    return restultingInfo 

def contains(container, targetElement):
    for i in container:
        if(i == targetElement):
            return True
    return False

def csvMaker(fileName, query):
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

'''def dataSep():
            global numeric_columns
            global text_columns
            active_columns = infos[0] if isinstance(infos, list) and isinstance(infos[0], list) else infos

            numeric_columns = []
            text_columns = []

            for column in active_columns:
                cursor.execute(f'SELECT typeof("{column}") FROM "{queryTable}" WHERE "{column}" IS NOT NULL LIMIT 1;')
                result = cursor.fetchone()
                col_type = result[0] if result else 'null'
                
                if col_type in ('integer', 'real'):
                    numeric_columns.append(column)
                else:
                    text_columns.append(column)
            return numeric_columns, text_columns'''

def begin():
    optionList = getTables()
    showOptions(optionList)

    print("\n")
    queryTable = input("What table would you like to query? (type 'exit' to exit)\n")

    while queryTable != "exit" and (not queryTable.isdigit() or int(queryTable) not in range(len(optionList))):
        print("That table doesn't exist! Try again, available numbers only please.")
        queryTable = input("What table would you like to query? (type 'exit' to exit)\n")
    if queryTable == "exit":
        sys.exit()
    queryTable = optionList[int(queryTable)]

    checkActive()
    infos = selectionHandler(queryTable)
    myQuery = userQuery(queryTable, infos[0], int(infos[1]), infos[2], dataConnect)

    actionChoice(myQuery)

def actionChoice(query):
    print(f"\nYou are querying {query.tableName} in {fileName}")
    #Remember that selection handler returns the following in the exact order: [columns selected, limit, original selection]
    
    optionList = getColumns(query.tableName)
    action = input(f"What would you like to do with {len(query.columnNames)} column(s)?\n" \
        "(V)view, (C)calculations, (F)filter, (E)edit my selection, (S)save to .CSV, (Q)quit\n")
    while action.upper() != 'Q':
        #colSelection = query.columnNames
        print("\n")
        
        '''if action.upper()[0] == 'A':
            
            cursor.execute(query.stringQuery)
            data = cursor.fetchall()
            for row in data:
                print(row) 
            
            newQuery()
            break'''
            
        if action.upper()[0] == 'V':
            print(query.dataFrame)
            action = input(f"What would you like to do with {len(query.columnNames)} column(s)?\n" \
        "(V)view, (C)calculations, (F)filter, (E)edit my selection, (S)save to .CSV, (Q)quit\n")

        if action.upper().startswith('C'):
            print("\nNote that non-numerical columns cannot have most calculations performed on them\n")
            myColumns = query.columnNames
            showOptions(myColumns)

            columnAffected = input ("Which of your column do you want to perform calcs on?")
            chosenColumn = myColumns[int(columnAffected)]
            calculation = input('What would you like to Calculate?:\n'
                                "(T)Total, (H)Highest, (L)Lowest, (A)Average, (M)Median, (B)Back:\n")
            
            if calculation.upper().startswith('T'):
                if(checkDataType(chosenColumn, query.tableName) == dataType.CATEGORICAL):
                    possibleVals = list(set([d[0] for d in cursor.execute(f"SELECT {myColumns[int(columnAffected)]} FROM {query.tableName}")]))
                    possibleVals = list(set(possibleVals))
                    showOptions(possibleVals)
                    chosenVal = input("The column you chose does not contain numerical data. Please select a specific value of your column to use for calculations:")
                    print(f"{possibleVals[int(chosenVal)]} total: {query.totalCategorical(chosenColumn, possibleVals[int(chosenVal)])}")
                else:
                    print(f"{myColumns[columnAffected]} total: {query.calculate(chosenColumn,'T')}")
            if calculation.upper().startswith('H'):
                print(f"{myColumns[columnAffected]} highest: {query.calculate(chosenColumn,'H')}")
            if calculation.upper().startswith('L'):
                print(f"{myColumns[columnAffected]} lowest: {query.calculate(chosenColumn,'L')}")
            if calculation.upper().startswith('A'):
                print(f"{myColumns[columnAffected]} average: {query.calculate(chosenColumn,'H')}")
            if calculation.upper().startswith('M'):
                print(f"{myColumns[columnAffected]} median: {query.calculate(chosenColumn,'M')}")
            if calculation.upper().startswith('B'):
                action = input(f"What would you like to do with {len(query.columnNames)} column(s)?\n"
                            "(V)view, (C)calculations, (F)find range, (E)edit my selection, (S)save to .csv, (Q)quit: ")
                
            action =''
                
        if action.upper().startswith('E'):       
                while True:
                    newOptions = getColumns(query.tableName)
                    showOptions(newOptions)
                    print(f"Current Selection: {query.stringSelection}")
                    edit = input("What edit would you like to perform?\n(A)Add, (R)Remove, (L)Change limit, (N)New Query or (B)Back:\n").upper()
                    
                    if edit.startswith('B'):
                        action = input(f"What would you like to do with {len(query.columnNames)} column(s)?\n" \
                        "(V)view, (C)calculations, (F)find range, (E)edit my selection, (Q)quit")
                        break
                        
                    elif edit.startswith('R'):
                        print(query.columnNames)
                        removal = input("Enter column indices to remove (separated by commas):\n")
                        indices = sorted([int(i) for i in removal.split(',') if i.strip().isdigit()], reverse=True)
                        for idx in indices:
                            if 0 <= idx < len(query.columnNames):
                                query.columnNames.pop(idx)
                        newSelecton = ''
                        for i in query.columnNames:
                            newSelecton = newSelecton + str(newOptions.index(i))
                            if(query.columnNames.index(i) != len(query.columnNames) - 1):
                                newSelecton = newSelecton + ','
                        newSelecton = newSelecton + f'({query.columnNames})'
                        query.stringSelection = newSelecton
                    elif edit.startswith('L'):
                        newLimit = input('Enter your new limit (no formatting, just digits)\n:')
                        query.limit = newLimit
                        edit =''
                    elif edit.startswith('N'):
                        edit =''
                        newQuery()
                    elif edit.startswith('A'):
                                          
                        for x in query.columnNames:
                            for y in optionList:
                                if x == y:
                                    optionList.remove(x)

                        showOptions(optionList)
                        print(f'Current Selection:{query.columnNames}')
                        new_col = input("Enter the name of the column to add:\n").strip()
                        if new_col:
                            query.columnNames.append(new_col)
                        newSelecton = ''
                        for i in query.columnNames:
                            newSelecton = newSelecton + str(newOptions.index(i))
                            if(query.columnNames.index(i) != len(query.columnNames) - 1):
                                newSelecton = newSelecton + ','
                        newSelecton = newSelecton + f'({query.limit})'
                        query.stringSelection = newSelecton 
       
        if action.upper().startswith('S'):

                csvName = input('Please name your .CSV file:\n')
                print("Saving...")
                csvMaker(csvName,query.columnNames, query.tableName)
                print(f"{csvName}.csv has been save at {os.path.dirname("queryfolder/"+csvName+".csv")}\n")
                break
        
        if action.upper().startswith('F'):
            filterBy = input('What would you like to filter by?' \
            '(C)category, (R)range, (B)back')
            while filterBy.upper()[0] != 'B':
                if(filterBy.upper().startswith('C')):
                    print(f"Here are the categories you can sort by (based on your selected columns):\n")
                    possibleCategories = []
                    for i in query.columnNames:
                        if(checkDataType(i, query.tableName) == dataType.CATEGORICAL):
                            possibleCategories.append(i)
                    showOptions(possibleCategories)
                    category = input('Select your category by number:\n')
                    possibleFilters = list(set([d[0] for d in cursor.execute(f"SELECT {possibleCategories[int(category)]} FROM {queryTable}")]))
                    showOptions(possibleFilters)
                    chosenFilter = input('Choose what to filter by with number:\n')
                    query.filterCategorical(possibleCategories[int(category)], possibleFilters[int(chosenFilter)])
                    query.stringQuery = f'SELECT * FROM {query.tableName} WHERE {possibleCategories[int(category)]}= "{possibleFilters[int(chosenFilter)]}"'
                    print(f'Filtered your selection by {possibleFilters[int(chosenFilter)]}.\n')
                    filtered = pan.read_sql(query.stringQuery, dataConnect)
                    print(query.dataFrame)
                    break 
                
                while filterBy.upper().startswith('R'):
                    #dataSep()
                    validColumns = []
                    print("\n**The following text columns cannot be calculated and will be skipped:**")
                    for col in query.columnNames:
                        if(checkDataType(col, query.tableName) == dataType.CATEGORICAL):
                            print(f" - {col}")
                        else:
                            validColumns.append(col)
                    
                    showOptions(validColumns)
                    affectedCol = int(input("What column do you want the range to affect?: \n"))
                    affectedCol = validColumns[affectedCol]
                    if affectedCol in validColumns:
                        cursor.execute(f'SELECT MIN("{affectedCol}"), MAX("{affectedCol}") FROM "{queryTable}"')
                        db_min, db_max = cursor.fetchone()
                        print(f"\nCurrent bounds for '{affectedCol}': Min is {db_min}, Max is {db_max}")

                        try:
                            Startr = float(input('What range do you want to filter by?(For a specific number make the start and end the same)\nStart: '))
                            endr = float(input('End: '))
                            
                            rangQue = f'SELECT * FROM "{queryTable}" WHERE "{affectedCol}" BETWEEN ? AND ?'
                            cursor.execute(rangQue, (Startr, endr))
                            
                            results = cursor.fetchall()
                            print(f"\nFound {len(results)} matching row(s):")
                            for row in results:
                                print(row)
                            choi = input('Continue filtering?(Y/N):\n')
                            if choi.upper().startswith('Y'):
                             filterBy == 'R'
                            elif choi.upper().startswith('N'):
                                filterBy == ''

                                actionChoice()
                        except ValueError:
                            print("\nError: Please enter numbers only for the range bounds.")
                    else:
                        print(f"\nError: '{affectedCol}' is not a valid numeric column.")
                        filterBy = input('Continue filtering?(Y/N):\n')
                    
                        if filterBy.upper().startswith('Y'):
                            filterBy == 'R'
                        elif filterBy.upper().startswith('N'):
                            actionChoice()
        action = input(f"What would you like to do with {len(query.columnNames)} column(s)?\n" \
                                "(V)view, (C)calculations, (F)find range, (E)edit my selection, (Q)quit")

    #newQuery()
    #print("You have quit.")
    sys.exit()
        
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
    if queryTable =='exit':
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


queryTable = ''

#-----PROGRAM-----
while queryTable != "exit":
    begin()

    checkActive()