import _sqlite3 as SQ

fileName = "final_reports.db"
dataConnect = SQ.connect(f"syn_output_data/{fileName}")
cursor = dataConnect.cursor()

print(f"You are querying {fileName}. You can query the following keywords: \n")
for i in cursor.execute("PRAGMA table_info(empty_synthetic_data)").fetchall():
    print((i[1]))

print("\n")

userQuery = input("Enter your query using the following format: ")