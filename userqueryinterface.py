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
    for i in tableList:
        print(i[0])
    activeUser = input("What table would you like to query? (type 'exit' to exit) ")
    if activeUser != "exit":
        userQuery = f'SELECT * FROM {activeUser}'
        cursor.execute(userQuery)
        data = cursor.fetchall()
        for i in data:
            print(i)
