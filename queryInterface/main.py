import _sqlite3 as SQ

from pipeline import beginQueryCreation as begin

#-----SETUP-----

fileName = "final_reports"
dataConnect = SQ.connect(f"syn_output_data/{fileName}.db")
cursor = dataConnect.cursor()

print(f"\nYou are querying {fileName}.\n")
print("You may query the following tables (name or #): \n")

uQuery = 'SELECT name FROM sqlite_master WHERE type="table"'

if __name__ == "__main__":
    begin()