import _sqlite3 as SQ
import pandas as pan
import os

files = os.listdir("b_input_data")

for file in files:
    dataConnect = SQ.connect("b_databases/"+file[:-3]+'.sqlite')
    curs = dataConnect.cursor()
    
    #curs.execute("CREATE TABLE ")

    fileName = "olist_customers_dataset.csv"
    fileRead = pan.read_csv("input_data/"+fileName)

print(fileRead)



