import _sqlite3 as SQ
#import sqlalchemy
import pandas as pan
import os

tables = []
#indexes of tables:
#table 0 = customers
#table 1 = geolocation
#table 2 = order items
#table 3 = order payments
#table 4 = order reviews
#table 5 = orders
#table 6 = products
#table 7 = sellers
#table 8 = product category name translation
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
    tableName = file[:-4]
    tables.append(tableName)
        
    curs.execute(f" DROP TABLE IF EXISTS {tableName}")
    curs.execute(f"CREATE TABLE {tableName} ({cols})")
    fileRead.to_sql(tableName, dataConnect, if_exists="append", index=False)

def getAmount(table):
    amount = 0
    for entry in curs.execute("SELECT * FROM "+table):
        amount += 1
    return amount

queryProducts = """
    SELECT 
        t.product_category_name_english,
        COUNT(i.product_id) as sales_count
    FROM olist_order_items_dataset i
    JOIN olist_products_dataset p 
        ON i.product_id = p.product_id
    JOIN product_category_name_translation t 
        ON p.product_category_name = t.product_category_name
    GROUP BY p.product_category_name
    ORDER BY sales_count DESC
    LIMIT ?
"""
querySellers = '''SELECT
                    i.seller_id, i.order_id, p.payment_value
                FROM olist_order_items_dataset i
                JOIN olist_order_payments_dataset p
                    ON i.order_id = p.order_id
                GROUP BY p.order_id
                ORDER BY p.payment_value DESC
                LIMIT ?
                '''

def viewQuery(whatQuery):
    rows = curs.execute(whatQuery, (10,)).fetchall()
    headers = [desc[0] for desc in curs.description]

    print(headers)
    for row in rows:
        print(row)

#viewQuery(querySellers)

def getTop10(whatQuery, var1, var2, item1, item2):
    print("Top 10 "+var1+"(s) by "+var2+": ")
    top_10_products = curs.execute(whatQuery, (10,)).fetchall()
    num =0 
    for item in top_10_products:
        num +=1
        print(num,f"{var1}: {item[item1]} | {var2} : {item[item2]}")

print(getTop10(queryProducts, "Product Category", "Sales", 0, 1))
getTop10(querySellers, "Seller ID", "Revenue",0 , 2)

#customerIDS = fileRead.groupby (['customer_id','product_id'])['order_id'].max().reset_index()

#customerIDS.to_sql('customerIDS',dataConnect)

def crossReference(itemToCompare, table, columnID, returnValueID):
    allEntries = list(curs.execute("SELECT * FROM " + table))
    reference = [row[columnID] for row in allEntries]
    for i in reference:
        if(itemToCompare == i):
            match = allEntries[reference.index(i)][returnValueID]
            return match
    return "No matches found"


query = """
    SELECT 
    FROM olist_order_items_dataset i
    JOIN olist_sellers_dataset p 
        ON i.product_id = p.product_id
    JOIN product_category_name_translation t 
        ON p.product_category_name = t.product_category_name
    GROUP BY p.price
    ORDER BY sales_count DESC
    LIMIT ?
"""

#print(df)
#print("Amount of customers in dataset: "+str(getAmount(tables[0])))
#print("Amount of orders placed in dataset: "+str(getAmount(tables[5])))
#print(crossReference("8cab8abac59158715e0d70a36c807415", tables[6], 0, 1))

'''
#get amount of customers in database
peopleInDatabase = 0
for entry in curs.execute("SELECT * FROM "+tables[0]):
    peopleInDatabase += 1
print(peopleInDatabase)

#get amount of orders in database

peopleInDatabase = 0
for entry in curs.execute("SELECT * FROM "+tables[0]):
    peopleInDatabase += 1
print(peopleInDatabase)'''



