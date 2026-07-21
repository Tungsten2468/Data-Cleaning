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
    activeUser = input("What table would you like to query? (type 'exit' to exit) ")
    if activeUser != "exit":
        userQuery = f'SELECT * FROM {activeUser}'
        cursor.execute(userQuery)
        data = cursor.fetchall()
        for i in data:
            print(i)

    print(f"You can query the following keywords: \n")
    for i in cursor.execute("PRAGMA table_info(empty_synthetic_data)").fetchall():
        print((i[1]))

    print("\n")

    userQuery = input("Enter your query using the following format: ")