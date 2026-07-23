import _sqlite3 as SQ
import sys
import pandas as pan
import csv
import os

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
    for char in selection: #second loop extract column numbers
        if(char.isdigit()):
            colSelection.append(optionList[int(char)])
        elif(selection == ',' or selection == ' '):
            continue
        elif(char.upper() == 'A'):
            colSelection = optionList    
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
        "(V)view, (C)calculations, (F)find range, (E)edit my selection, (S)save to .CSV, (Q)quit\n")

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
            print(createColumnTable(infos[0], activeUser, infos[1]))
            break

        if action.upper()[0] == 'C':
                calualation = input('What would you like to Calculate?:\n'\
                        "(T)Total, (H)Highest, (L)Lowest, (A)Average, (M)Median, (B)Back:\n")
                if calualation.upper()[0] == 'T':
                    print("\n**Note that categorical data types cannot be summed up.**\n")
                    
                    for column in infos[0]:
                        cursor.execute(f"SELECT SUM({column}) FROM '{activeUser}'")
                        total_stock = cursor.fetchone()[0]
                        print(f"Total of {column}: {total_stock}")
                        action =''
                if calualation.upper()[0] == 'H':
                    for column in infos[0]: 
                        cursor.execute(f"SELECT MAX({column})FROM'{activeUser}'")
                        maxstock=cursor.fetchone()[0]
                        print(f"Max of {column}: {maxstock}")
                        action =''
                if calualation.upper()[0] == 'L':
                    for column in infos[0]: 
                        cursor.execute(f"SELECT MIN({column})FROM'{activeUser}'")
                        minstock=cursor.fetchone()[0]
                        print(f"Lowest of {column}: {minstock}")
                        action =''
                if calualation.upper()[0] == 'A':
                    for column in infos[0]: 
                        cursor.execute(f"SELECT ROUND(AVG({column}),2) FROM'{activeUser}'")
                        avgStock=cursor.fetchone()[0]
                        print(f"Average of {column}: {avgStock}")
                        action =''
                if calualation.startswith('B'):
                        action = input(f"What would you like to do with {len(infos[0])} column(s)?\n" \
                        "(V)view, (C)calculations, (F)find range, (E)edit my selection, (Q)quit")
                        break
                
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
    action = ''
    newQuery()
    print("You have quit.")
    sys.exit()

def checkActive():
    if activeUser =='exit':
        sys.exit()

def getTables():
    tableList = []
    for i in cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';").fetchall():
        tableList.append(i[0])
    return tableList

def newQuery():
        con = input('\nNew column query,Same columns, Exit? (N/S/E):\n')
        if con.upper()[0] == 'E':
            print("You have quit.")
            sys.exit()
        if con.upper()[0] == 'N':
            return begin() 
        if con.upper()[0] == 'S':
            actionChoice()

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

def createColumnTable(listOfColumns, table, rowLimit):
    rowLimit = int(rowLimit) 

    pan.set_option("display.max_rows", None)
    pan.set_option("display.max_columns", None)

    columnTable = pan.DataFrame(columns=listOfColumns)

    for i in listOfColumns:
        if rowLimit != 0:
            rows = cursor.execute(f"SELECT {i} FROM {table} LIMIT {rowLimit}").fetchall()
        else:
            rows = cursor.execute(f"SELECT {i} FROM {table}").fetchall()

        columnTable[i] = [r[0] for r in rows]

    return columnTable


#-----PROGRAM-----
while activeUser != "exit":
    
    
    begin()

    checkActive()