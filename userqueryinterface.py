import _sqlite3 as SQ
import sys


fileName = "final_reports"
dataConnect = SQ.connect(f"syn_output_data/{fileName}.db")
cursor = dataConnect.cursor()

print(f"\nYou are querying {fileName}.\n")
print("You may query the following tables: \n")

userQuery = 'SELECT name FROM sqlite_master WHERE type="table"'


def checkActive():
    if activeUser =='exit':
        sys.exit()



activeUser = ''

while activeUser != "exit":
    cursor.execute(userQuery)
    tableList = cursor.fetchall()
    for i in tableList:
        print(i[0])
    
    print("\n")
    activeUser = input("What table would you like to query? (type 'exit' to exit)\n")
    
    checkActive()

    if activeUser == 'syn' or activeUser == 'empty' or activeUser == 's' or activeUser == 'e':
        activeUser = 'empty_synthetic_data'


    if activeUser != "exit":
         
        tableColumns=f"PRAGMA table_info({activeUser});"
        cursor.execute(tableColumns)

        raw_results = cursor.fetchall()
        column_names = [col[1] for col in raw_results]
    
        print(f"\nYou are querying {activeUser} in {fileName}:\n")
        print("Available columns: \n")
        for i in column_names:
            print(i)
    
    print("\n")
    

    action = input("What would you like to do?\n" \
    "(A)all columns, (R)range, (O)order, (C)calculate, (F)filter")

    if action.upper()[0] == 'A':
        userQuery = f'SELECT * FROM {activeUser}'
        cursor.execute(userQuery)
        data = cursor.fetchall()
        for row in data:
            print(row) 
        continue

    column = input('What column would you like to query?:\n')
    print(f"\nYou are querying {column} from {activeUser} in {fileName}\n")


    userQuery = f'SELECT {column} FROM {activeUser}'
    cursor.execute(userQuery)
    data = cursor.fetchall()
    for i in data:
        print(i)

