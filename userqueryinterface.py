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


def showColumns():
        tableColumns=f"PRAGMA table_info({activeUser});"
        cursor.execute(tableColumns)

        raw_results = cursor.fetchall()
        column_names = [col[1] for col in raw_results]
    
        print(f"\nYou are querying {activeUser} in {fileName}:\n")
        print("Available columns: \n")
        for i in column_names:
            print (i)

activeUser = ''

def checkExists(input, checkAgainst):
    if(input == 'exit'):
        return True
    for i in checkAgainst:
        if(i == input):
            return True
    return False

while activeUser != "exit":
    cursor.execute(userQuery)
    tableList = cursor.fetchall()
    for i in tableList:
        print(i[0])
    
    print("\n")
    
    activeUser = input("What table would you like to query? (type 'exit' to exit)\n")
    if activeUser == 'empty_synthetic_data' or activeUser == 'syn' or activeUser == 'empty' or activeUser == 's' or activeUser == 'e':
        activeUser = 'empty_synthetic_data'

    elif activeUser == 'organized_data' or activeUser == 'org' or activeUser == 'o' or activeUser == 'original' or activeUser == 'organized':
        activeUser = 'organized_data'
    else:
        print('Invalid table. Check spelling.')
        activeUser = input("What table would you like to query? (type 'exit' to exit)\n")
    
    checkActive()

    if activeUser == 'syn' or activeUser == 'empty' or activeUser == 's' or activeUser == 'e':
        activeUser = 'empty_synthetic_data'

    if activeUser == 'org' or activeUser == 'o' or activeUser == 'original' or activeUser == 'organized':
        activeUser = 'organized_data'

    

    action = input("What would you like to do?\n" \
    "(A)all columns, (R)range, (O)order, (C)calculate, (F)filter, (V)view")



    if action.upper()[0] == 'A':
        userQuery = f'SELECT * FROM {activeUser}'
        cursor.execute(userQuery)
        data = cursor.fetchall()
        for row in data:
            print(row) 
        continue

    if action.upper()[0] == 'V':
        amount = int(input('How many columns would you like to view'))
        colSelection= []
        for col in range(amount-1):
            showColumns()
            userCol = input('What column would you like to query?:\n')
            colSelection.append(userCol)
        column_string = ", ".join(colSelection)       
        colQuery = f'SELECT {column_string} FROM "{activeUser}"'


        cursor.execute(colQuery)

            





    column = input('What column would you like to query?:\n')
    print(f"\nYou are querying {column} from {activeUser} in {fileName}\n")


    userQuery = f'SELECT {column} FROM {activeUser}'
    cursor.execute(userQuery)
    data = cursor.fetchall()
    for i in data:
        print(i)



