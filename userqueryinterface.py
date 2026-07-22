import _sqlite3 as SQ
import sys
import pandas as pan

fileName = "final_reports"
dataConnect = SQ.connect(f"syn_output_data/{fileName}.db")
cursor = dataConnect.cursor()

print(f"\nYou are querying {fileName}.\n")
print("You may query the following tables (name or #): \n")

userQuery = 'SELECT name FROM sqlite_master WHERE type="table"'


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

def createColumnTable(listOfColumns, table):
    pan.set_option("display.max_rows", None)
    pan.set_option("display.max_columns", None)
    columnTable = pan.DataFrame(columns=listOfColumns)
    for i in listOfColumns:
        columnTable[i] = cursor.execute(f"SELECT {i} FROM {table}").fetchall()[0]
    return columnTable

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

    action = input("What would you like to do?\n" \
    "(A)all columns, (R)range, (O)order, (C)calculate, (F)filter, (V)view")

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
        optionList = getColumns()
        colSelection = []
        ind =1
        
        amount = int(input('\nHow many columns would you like to view: \n'))
        showOptions(optionList)
        selection = input("\nSelect the column(s) you want to view (name or #, 'A' for all, input 'D' when done)")
        while selection.upper() != 'D'and ind != amount:
            ind+=1
            if(selection.isdigit):
                colSelection.append(optionList.pop(int(selection)))
            elif(selection.upper() != 'A'):
                colSelection.append(selection)
            else:
                for i in optionList:
                    colSelection.append(i)
                break
            showOptions(optionList)
            selection = input("Select the column(s) you want to view (name or #, 'A' for all, input 'D' when done)")







        print("\nPlease wait, fetching data...\n")
        print(createColumnTable(colSelection, activeUser))
        
        #amount = int(input('How many columns would you like to view'))
        #userCol = input('What column would you like to query?:\n')
        #colSelection.append(userCol)
        column_string = ", ".join(colSelection)       
        colQuery = f'SELECT {column_string} FROM "{activeUser}"'

        cursor.execute(colQuery)



