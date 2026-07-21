import _sqlite3 as SQ

fileName = "final_reports"
dataConnect = SQ.connect(f"syn_output_data/{fileName}.db")
cursor = dataConnect.cursor()

print(f"\nYou are querying {fileName}.\n")
print("You may query the following tables: \n")

userQuery = 'SELECT name FROM sqlite_master WHERE type="table"'

activeUser = ''

while activeUser != "exit":
    cursor.execute(userQuery)
    tableList = cursor.fetchall()
    for i in tableList:
        print(i[0])
    
    print("\n")
    activeUser = input("What table would you like to query? (type 'exit' to exit)\n")
    
    tableColumns=f"PRAGMA table_info({activeUser});"
    cursor.execute(tableColumns)

    raw_results = cursor.fetchall()
    column_names = [col[1] for col in raw_results]
    
    print(f"\nYou are querying {activeUser} in {fileName}:\n")
    print("Available columns: \n")
    for i in column_names:
        print(i)
    
    print("\n")
    print("Please enter your query in the following format:" \
    "\n[column_name] [operation] [target value]\n" \
    "\nEX: total_payment > 100\n")
    column = input('What column would you like to query?:\n')

    if activeUser != "exit":
        
        userQuery = f'SELECT {column} FROM {activeUser}'
        cursor.execute(userQuery)
        data = cursor.fetchall()
        for i in data:
            print(i)

 