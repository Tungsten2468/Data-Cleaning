import _sqlite3 as SQ

fileName = "final_reports_db"
dataConnect = SQ.connect(f"syn_output_data/{fileName}.sqlite")
cursor = dataConnect.cursor()

keywordList = []


print(f"You are querying {fileName}. You can query the following keywords: ")

userQuery = input("Enter your query using the following format: ")