import _sqlite3 as SQ

dataConnect = SQ.connect("syn_output_data/final_reports_db.sqlite")
cursor = dataConnect.cursor()

