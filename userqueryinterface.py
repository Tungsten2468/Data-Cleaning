import _sqlite3 as SQ
import sys
import pandas as pan

fileName = "final_reports"
dataConnect = SQ.connect(f"syn_output_data/{fileName}.db")
cursor = dataConnect.cursor()

print(f"\nYou are querying {fileName}.\n")
print("You may query the following tables (name or #): \n")

userQuery = 'SELECT name FROM sqlite_master WHERE type="table"'
#-----FUNCTIONS-----
def contains(container, targetElement):
    for i in container:
        if(i == targetElement):
            return True
    return False

def csvMaker(tableName):
    folderpath ="queryfolder/"+tableName+".csv"
    cursor.execute(f"SELECT * FROM '{tableName}'")


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


def checkActive():
    if activeUser =='exit':
        sys.exit()

def getTables():
    tableList = []
    for i in cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';").fetchall():
        tableList.append(i[0])
    return tableList

def newQuery():
        con = input('\nNew Query? (Y/N):\n')
        if con.upper()[0] == 'N':
            sys.exit()
        if con.upper()[0] == 'Y':
            return 

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
    pan.set_option("display.max_rows", None)
    pan.set_option("display.max_columns", None)
    columnTable = pan.DataFrame(columns=listOfColumns)
    for i in listOfColumns:
        if(rowLimit != 0):
            rows = cursor.execute(f"SELECT {i} FROM {table} LIMIT {rowLimit}").fetchall()
        else:
            rows = cursor.execute(f"SELECT {i} FROM {table}").fetchall()
        columnTable[i] = [r[0] for r in rows]
    return columnTable
#-----PROGRAM-----
while activeUser != "exit":
    optionList = getTables()
    showOptions(optionList)
    
    print("\n")
    
    activeUser = input("What table would you like to query? (type 'exit' to exit)\n")
    if(activeUser[0].isdigit()):
        activeUser = optionList[int(activeUser)]
    else:
        activeUser = activeUser
    
    checkActive()

    print(f"\nYou are querying {activeUser} in {fileName}")

    optionList = getColumns()
    colSelection = []
    showOptions(optionList)
    selection = input("\nSelect the column(s) and limit you want to work with (using the # on the left side) in the following format:\n"
    "[column_number,column_number,...,(limit)]\n"
    "Input column number as 'A' to view all columns and () as 0 for no limit\n")
    while(contains(selection, '(') == False and contains(selection, ')') == False):
        print("You didn't specify a limit! Please specify a limit by enclosing it in commas.\n")
        selection = input("\nSelect the column(s) and limit you want to work with (using the # on the left side) in the following format:\n"
            "[column_number,column_number,...,l=#]\n"
            "Input column number as 'A' to view all columns and () as 0 for no limit\n")
    charIndex = 0
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
            colSelection.append(optionList)
    print(colSelection)
    action = input(f"What would you like to do with {len(colSelection)} column(s)?\n" \
        "(V)view, (C)calculations, (F)find range, (E)add/remove from my selection")
    
    print("\n")
    
    if action.upper()[0] == 'A':
        userQuery = f'SELECT * FROM {activeUser}'
        cursor.execute(userQuery)
        data = cursor.fetchall()
        for row in data:
            print(row) 
        newQuery()
        continue
    if action.upper()[0] == 'V':
        print(createColumnTable(colSelection, activeUser, limit))

    if action.upper()[0] == 'C':
        calualation = input('What would you like to Calculate?:\n'\
                "(T)Total, (H)Highest, (L)Lowest, (A)Average, (M)Median:\n")
        if calualation.upper()[0] == 'T':
            for column in colSelection:
                cursor.execute(f"SELECT SUM({column}) FROM '{activeUser}'")
                total_stock = cursor.fetchone()[0]
                print(f"Total of {column}: {total_stock}")
        if calualation.upper()[0] == 'H':
            for column in colSelection: 
                cursor.execute(f"SELECT MAX({column})FROM'{activeUser}'")
                maxstock=cursor.fetchone()[0]
                print(f"Max of {column}: {maxstock}")
        if calualation.upper()[0] == 'L':
            for column in colSelection: 
                cursor.execute(f"SELECT MIN({column})FROM'{activeUser}'")
                minstock=cursor.fetchone()[0]
                print(f"Lowest of {column}: {minstock}")
        if calualation.upper()[0] == 'A':
            for column in colSelection: 
                cursor.execute(f"SELECT ROUND(AVG({column}),2) FROM'{activeUser}'")
                avgStock=cursor.fetchone()[0]
                print(f"Average of {column}: {avgStock}")