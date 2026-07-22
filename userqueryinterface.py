import _sqlite3 as SQ
import sys
import pandas as pan
import csv


fileName = "final_reports"

dataConnect = SQ.connect(f"syn_output_data/{fileName}.db")
cursor = dataConnect.cursor()

print(f"\nYou are querying {fileName}.\n")
print("You may query the following tables (name or #): \n")

def csvMaker(tableName):
    folderpath ="/Users/uc25261/Desktop/Data-Cleaning/queryfolder/"+tableName+".csv"
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

    optionList = getColumns()
    
    colSelection = []
    ind =1
    showOptions(optionList)  
    amount = int(input('\nHow many columns would you like to view: \n'))
    showOptions(optionList) 
    selection = input("\nSelect the column(s) you want to view (name or #, 'A' for all, input 'D' when done)")
    while selection.upper() != 'D' and ind != amount:
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
        tablename= input ('Name your table: \n')
        column_string = ", ".join(colSelection)  
        print(column_string)     
        colQuery = f'''CREATE TABLE {tablename} AS
        SELECT {column_string} 
        FROM "{activeUser}"'''
        cursor.execute(f'DROP TABLE IF EXISTS {tablename}')
        cursor.execute(colQuery)
        
        dataConnect.commit()
        csvMaker(tablename)
        viewCSV(tablename)

    





      



