import os
import _sqlite3 as SQ

from pipeline import beginQueryCreation as begin

#-----SETUP-----

fileName = "final_reports"

# The data folder was git-ignored, so the .db now lives at the repo root.
# Look in a few sensible spots so this works no matter where it's launched from.
_here = os.path.dirname(os.path.abspath(__file__))
_repo_root = os.path.dirname(_here)
_candidates = [
    f"syn_output_data/{fileName}.db",
    os.path.join(_repo_root, f"{fileName}.db"),
    os.path.join(_repo_root, "syn_output_data", f"{fileName}.db"),
]
_dbPath = next((p for p in _candidates if os.path.exists(p)), _candidates[0])

dataConnect = SQ.connect(_dbPath)
cursor = dataConnect.cursor()

print(f"\nYou are querying {fileName}.\n")
print("You may query the following tables (name or #): \n")

uQuery = 'SELECT name FROM sqlite_master WHERE type="table"'

if __name__ == "__main__":
    begin()