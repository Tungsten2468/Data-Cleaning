import _sqlite3 as SQ

fileName = "final_reports"
dataConnect = SQ.connect(f"syn_output_data/{fileName}.db")
cursor = dataConnect.cursor()

keywordList = []



userQuery = 'SELECT name FROM sqlite_master WHERE type="table"'

activeUser = ''

while activeUser != "exit":
    cursor.execute(userQuery)
    tableList = cursor.fetchall()
    print("Available tables:")
    for i in tableList:
        print(i[0])
    activeUser = input("What table would you like to query? (type 'exit' to exit) ")
    
    tableColumns=f"PRAGMA table_info({activeUser});"
    cursor.execute(tableColumns)

    raw_results = cursor.fetchall()
    column_names = [col[1] for col in raw_results]
    
    print("Available columns:")
    for i in column_names:
        print(i)
    column = input('What column would you like to query?:')

    if activeUser != "exit":
        
        userQuery = f'SELECT {column} FROM {activeUser}'
        cursor.execute(userQuery)
        data = cursor.fetchall()
        for i in data:
            print(i)
