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
        if(not rowLimit == 0):
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
            "[column_number,column_number,...,(limit)]\n"
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
            colSelection = optionList
    action = input(f"What would you like to do with {len(colSelection)} column(s)?\n" \
        "(V)view, (C)calculations, (F)find range, (E)add/remove from my selection, (Q)quit\n")

    while action.upper() != 'Q':
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

        action = input(f"What would you like to do with {len(colSelection)} column(s)?\n" \
        "(V)view, (C)calculations, (F)find range, (E)add/remove from my selection, (Q)quit\n")
    activeUser = 'exit'
print("You have quit.")

      



