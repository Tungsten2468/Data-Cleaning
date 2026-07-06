import _sqlite3 as SQ
import pandas as pan
import os

files = os.listdir("b_input_data")
dataConnect = SQ.connect("b_output_data/brazilian_data_db.sqlite")
curs = dataConnect.cursor()
for file in files:
    fileRead = pan.read_csv("b_input_data/"+file)
    cols = ""
    for header in fileRead.columns: #only add commas if the header is not the last one
        if(fileRead.columns.get_loc(header) != len(fileRead.columns)-1):
            cols = cols+header+", "
        else:
            cols = cols+header
    curs.execute("CREATE TABLE "+file[:-4]+"("+cols+")")


#fileRead = pan.read_csv("input_data/"+fileName)