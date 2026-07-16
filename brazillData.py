import _sqlite3 as SQ
import csv
import pandas as pan
import os
import matplotlib.pyplot as plt 
import numpy as np
import random

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

#------------------PREP-------------------
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
#------------------QUERIES-------------------
queryCustAmount = '''SELECT
                    COUNT(DISTINCT i.customer_id) as c
                    FROM olist_customers_dataset i'''
queryOrderAmount = '''SELECT
                    COUNT(i.order_id) as c
                    FROM olist_orders_dataset i'''
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
queryOrderAvg = '''SELECT
                    ROUND(AVG(i.price), 2)
                FROM olist_order_items_dataset i
                '''
queryCities = '''SELECT
                    i.customer_city, COUNT(i.customer_id) AS c
                FROM olist_customers_dataset i
                GROUP BY i.customer_city
                ORDER BY c DESC
                LIMIT ?
                '''
queryOrderStatus = '''SELECT
                        i.order_status, COUNT(*) AS c
                    FROM olist_orders_dataset i
                    GROUP BY i.order_status
                    ORDER BY c DESC
                    LIMIT ?'''
queryReviews = '''SELECT
                    i.seller_id, i.order_id, ROUND(AVG(e.review_score)) AS review_avg
                FROM olist_order_items_dataset i
                JOIN olist_order_reviews_dataset e
                    ON i.order_id = e.order_id
                GROUP BY i.seller_id
                LIMIT?
                '''
queryHighSpending = '''SELECT
                        i.customer_id, i.order_id, e.payment_value
                    FROM olist_orders_dataset i
                    JOIN olist_order_payments_dataset e
                        ON i.order_id = e.order_id
                    ORDER BY e.payment_value ASC
                    '''
queryOrderEachMonth = '''SELECT
                            SUBSTR(i.order_purchase_timestamp, 6, 2) AS month, COUNT(i.order_id)
                        FROM olist_orders_dataset i
                        GROUP BY month
                        '''
newtable = ''' SELECT 
    i.customer_state,p.payment_type, 
    p.payment_installments, 
    SUM(a.price) AS product_value, 
    a.freight_value, 
    p.payment_value AS total_payment, 
    r.review_score, 
    o.order_purchase_timestamp AS purchase_date, 
    CAST(julianday(o.order_delivered_customer_date) AS INTEGER) -
    CAST(julianday(o.order_purchase_timestamp)  AS INTEGER) AS delivery_days
    FROM olist_customers_dataset i 
    JOIN olist_orders_dataset o
        ON i.customer_id = o.customer_id
    JOIN olist_order_items_dataset a
        ON o.order_id = a.order_id
    JOIN olist_order_reviews_dataset r
        ON o.order_id = r.order_id
    JOIN olist_order_payments_dataset p
        ON o.order_id = p.order_id
    GROUP BY o.order_id
    LIMIT ?
    '''
queryMostCommonPM = '''SELECT
                        i.payment_type, COUNT(*) AS paymentTCounts
                        FROM olist_order_payments_dataset i
                        GROUP BY i.payment_type
                        ORDER BY paymentTCounts DESC
                        LIMIT ?'''
queryMostCommonStates = '''SELECT
                        i.customer_state, COUNT(*) AS stateCounts
                        FROM olist_customers_dataset i
                        GROUP BY i.customer_state
                        ORDER BY stateCounts DESC
                        '''
queryReviewDist = '''SELECT
                        i.review_score, COUNT(*) AS reviewScoreCount
                        FROM olist_order_reviews_dataset i
                        GROUP BY i.review_score
                        ORDER BY reviewScoreCount DESC'''
queryMeanPV = '''SELECT
                    ROUND(AVG(i.product_value), 2) AS mean_product_value
                    FROM organized_data i
                    '''
queryMeanFV = '''SELECT
                    ROUND(AVG(i.freight_value), 2) AS mean_freight_value
                    FROM organized_data i
                    '''
queryMeanDT = '''SELECT
                    ROUND(AVG(i.delivery_days), 2) AS delivery_days
                    FROM organized_data i
                    '''
queryMedianPV = '''SELECT
                    i.product_value
                    FROM organized_data i
                    ORDER BY i.product_value ASC'''
queryMedianFV = '''SELECT
                    i.freight_value
                    FROM organized_data i
                    ORDER BY i.freight_value ASC'''
queryMedianDT = '''SELECT
                    i.delivery_days
                    FROM organized_data i
                    ORDER BY i.delivery_days ASC'''
synqueryMeanPV = '''SELECT
                    ROUND(AVG(i.product_value), 2) AS mean_product_value
                    FROM empty_synthetic_data i
                    '''
synqueryMeanFV = '''SELECT
                    ROUND(AVG(i.freight_value), 2) AS mean_freight_value
                    FROM empty_synthetic_data i
                    '''
synqueryMeanDT = '''SELECT
                    ROUND(AVG(i.delivery_days), 2) AS delivery_days
                    FROM empty_synthetic_data i
                    '''
synqueryMedianPV = '''SELECT
                    i.product_value
                    FROM empty_synthetic_data i
                    ORDER BY i.product_value ASC'''
synqueryMedianFV = '''SELECT
                    i.freight_value
                    FROM empty_synthetic_data i
                    ORDER BY i.freight_value ASC'''
synqueryMedianDT = '''SELECT
                    i.delivery_days
                    FROM empty_synthetic_data i
                    ORDER BY i.delivery_days ASC'''
queryPaymentTypes = '''SELECT
                        i.payment_type, COUNT (*) AS payment_type_count
                        FROM olist_order_payments_dataset i
                        GROUP BY i.payment_type
                        ORDER BY payment_type_count DESC'''
queryAllOrg = "SELECT * FROM organized_data"
queryMaxInstallmentAmnt = '''SELECT
                                i.payment_installments,
                                COUNT (*) AS countsHaveThisNum
                                FROM organized_data i
                                GROUP BY i.payment_installments
                                ORDER BY countsHaveThisNum DESC'''
queryDeliveryDays = '''SELECT
                        i.delivery_days,
                        COUNT (*) AS countsHaveThisNum
                        FROM organized_data i
                        GROUP BY i.delivery_days
                        ORDER BY countsHaveThisNum DESC'''

syn_table = ''' 
CREATE TABLE IF NOT EXISTS external_db.empty_synthetic_data (
    syn_order_id TEXT PRIMARY KEY,
    customer_state TEXT,
    payment_type TEXT,
    payment_installments INTEGER,
    product_value REAL,
    freight_value REAL,
    total_payment REAL,
    review_score INTEGER,
    purchase_date TEXT,
    delivery_days INTEGER);'''


pp ='''CREATE TABLE IF NOT EXISTS external_db.organized_data AS 
SELECT 
    i.customer_state,p.payment_type, 
    p.payment_installments, 
    ROUND(SUM(a.price),2) AS product_value, 
    ROUND(SUM(a.freight_value), 2) AS freight_value,  
    ROUND(p.payment_value, 2) AS total_payment,
    r.review_score, 
    o.order_purchase_timestamp AS purchase_date, 
    CAST(julianday(o.order_delivered_customer_date) AS INTEGER) -
    CAST(julianday(o.order_purchase_timestamp)  AS INTEGER) AS delivery_days
    FROM olist_customers_dataset i 
    JOIN olist_orders_dataset o
        ON i.customer_id = o.customer_id

    JOIN olist_order_items_dataset a
        ON o.order_id = a.order_id
    JOIN olist_order_reviews_dataset r
        ON o.order_id = r.order_id
    JOIN olist_order_payments_dataset p
        ON o.order_id = p.order_id
    WHERE o.order_status = 'delivered'


        AND a.price >= 0 
        AND a.freight_value >= 0
        AND p.payment_value >= 0
 
        AND (CAST(julianday(o.order_delivered_customer_date) AS INTEGER) - CAST(julianday(o.order_purchase_timestamp) AS INTEGER)) >= 0
 
        AND o.order_delivered_customer_date IS NOT NULL
    GROUP BY 
    o.order_id,
    i.customer_state,
    p.payment_type,
    p.payment_installments,
    p.payment_value,
    r.review_score,
    o.order_purchase_timestamp,
    o.order_delivered_customer_date
    ORDER BY purchase_date ASC
    '''

summary_table= ''' 
CREATE TABLE IF NOT EXISTS external_db.Summary_Statistics (
    Variable TEXT,
    Real_Mean INTERGER,
    Synthetic_Mean INTERGER,
    Real_Median INTERGER,
    Synthetic_Median INTERGER); '''

#------------------FUNCTIONS-------------------
def calcDistributions(query):
    rows = curs.execute(query).fetchall()
    headers = [desc[0] for desc in curs.description]

    total = 0
    percents = []

    for row in rows:
        total += row[1]
    for row in rows:
        percentage = ((row[1] / total) * 100)/100
        percents.append(percentage)
    #print(viewQuery(query, lim))
    #print(percents)
    return percents

def calcMedian(query):
    inOrder = []
    for i in curs.execute(query).fetchall():
        inOrder.append(i)
    median = 0
    print(len(inOrder))
    if(len(inOrder) % 2 == 0): #if list amount is even
        median = inOrder[int(len(inOrder)/2)]
        #middle2 = middle1 + 1
        #median = (middle1+middle2)/2
    elif(not len(inOrder) % 2 == 0): #if list amount is odd
        median = inOrder[int((len(inOrder) + 1)/2)]
    return median

def getAmount(query): #just counts entires
    amount = 0
    for entry in curs.execute(query):
        amount += 1
    return amount

def noTuple(whatQuery): #makes the query not a tuple for easy use
    tupless = [item for row in whatQuery for item in row]
    return tupless

#-1 = no limit
def viewQuery(whatQuery, lim): #prints the query for easy viewing/debugging
    if(lim != -1):
        rows = curs.execute(whatQuery, (lim,)).fetchall()
    else:
        rows = curs.execute(whatQuery).fetchall()

    
    for row in rows:
        return(row)
    
def getMostAmountInCategory(whatQuery, val1ID, val2ID): #query must be ordered in ascending
    qu = curs.execute(whatQuery)
    qu = noTuple(qu)
    return str(qu[len(qu)-1][val1ID])+", "+str(qu[len(qu)-1][val2ID])

def getTop(whatQuery, var1, var2, item1, item2, topNum):
    print("Top 10 "+var1+"(s) by "+var2+": ")
    top = curs.execute(whatQuery, (topNum,)).fetchall()
    num =0 
    for item in top:
        num +=1
        print(num,f"{var1}: {item[item1]} | {var2} : {item[item2]}")

def barGraph(whatQuery, var1, var2, item1, item2):
    top_10_products = curs.execute(whatQuery, (10,)).fetchall()
    x = []
    y = []
    for item in top_10_products:
        if len(item[item1])>5:
            x.append(item[item1][0:5]+"...")
            y.append(item[item2])
        else:
            x.append(item[item1])
            y.append(item[item2])
    plt.bar(x,y)
    plt.xlabel(var1)
    plt.ylabel(var2)
    plt.title("Top 10 "+var1+"(s) by "+var2)
    plt.show()

def lineGraph(whatQuery, var1, var2, item1, item2):
    top_10_products = curs.execute(whatQuery).fetchall()
    x = []
    y = []
    for item in top_10_products:
        x.append(item[item1])
        y.append(item[item2])
    plt.plot(x,y)
    plt.xlabel(var1)
    plt.ylabel(var2)
    plt.title("Top 10 "+var1+"(s) by "+var2)
    plt.show()

def pieChart(whatQuery, var1, var2, item1, item2):
    top_10_products = curs.execute(whatQuery, (10,)).fetchall()
    x = []
    y = []
    for item in top_10_products:
        x.append(item[item1])
        y.append(item[item2])
    plt.pie(y)
    plt.legend(x,title='status', loc="upper left")
    plt.title("Top 10 "+var1+"(s) by "+var2)
    plt.show()

def generateSyntheticNumericalData(realTable, column, fakeTable, maxModifier, dataLimit):
    raw_rows = curs.execute(f"SELECT {column} FROM {realTable}").fetchall()
    datas = [row[0] for row in raw_rows if row[0] is not None]
    checkSynR = list(curs.execute("SELECT * FROM "+fakeTable))
    rowID = 1
    limitHit = 1

    for entry in datas:
        op = random.randint(0, 1)
        randMod = random.randint(0, maxModifier)

        if op == 0:
            if entry - randMod >= 0:
                entry -= randMod
            else:
                entry += randMod
        elif op == 1:
            entry += randMod

        if entry < 0:
            entry = 0

        if isinstance(entry, float):
            entry = round(entry, 2)

        if(len(checkSynR) != 0):
            curs.execute(f"UPDATE {fakeTable} SET {column} = ? WHERE rowid = ?", (entry, rowID))
        else:
            curs.execute(f"INSERT INTO {fakeTable} ({column}) VALUES (?)", (entry,))
        rowID += 1
        if(limitHit == dataLimit):
            break
        else:
            limitHit += 1

    dataConnect.commit()

def insertIntoTable(tableName, columnNames, values):
    
    for x in values:
        query = f"INSERT INTO {tableName} ({columnNames}) VALUES (?)"
        curs.execute(query,(x,))
    dataConnect.commit()

def generateSyntheticID(column,fakeTable,amount):
    syn = 'SYN'
    id = 1
    rowID = 1
    synData = []
    for i in range(amount):
        id = str(id)
        if len(id) == 1 :
            id = '000'+id
        elif len(id) == 2 :
            id = '00'+id
        elif len(id) == 3 :
            id = '0'+id
        elif len(id) == 4 :
            id = id

        synID = syn + id
        synData.append(synID)
        id = int(id)
        id +=1 

    checkSynR = list(curs.execute("SELECT * FROM "+fakeTable))

    for sid in synData:
        if(len(checkSynR) != 0):  
            curs.execute(f"UPDATE {fakeTable} SET {column} = ? WHERE rowid = ?", (sid, rowID))
        else:
            curs.execute(f"INSERT INTO {fakeTable} ({column}) VALUES (?)", (sid,))
        rowID += 1

    dataConnect.commit()

def generateSyntheticCategoricalData(column, fakeTable, possibleVals, query, dataLimit):
    synthetic = list(np.random.choice(possibleVals, size=getAmount(queryAllOrg), p=calcDistributions(query)))
    checkSynR = list(curs.execute("SELECT * FROM "+fakeTable))
    rowID = 1
    limitHit = 1
    for synData in synthetic:
        if(len(checkSynR) != 0):  
            curs.execute(f"UPDATE {fakeTable} SET {column} = ? WHERE rowid = ?", (synData, rowID))
        else:
            curs.execute(f"INSERT INTO {fakeTable} ({column}) VALUES (?)", (synData,))
        rowID += 1
        if(limitHit == dataLimit):
            break
        else:
            limitHit += 1

    dataConnect.commit()

def generateResultingSyntheticData(column1, column2, targetColumn, fakeTable):
    checkSynR = list(curs.execute("SELECT * FROM "+fakeTable))
    tableToGetFrom = list(curs.execute(f"SELECT {column1}, {column2} FROM "+fakeTable))
    rowID = 1
    for i in tableToGetFrom:
        resultantData = i[0] + i[1]
        if(len(checkSynR) != 0):  
            curs.execute(f"UPDATE {fakeTable} SET {targetColumn} = ? WHERE rowid = ?", (resultantData, rowID))
        else:
            curs.execute(f"INSERT INTO {fakeTable} ({targetColumn}) VALUES (?)", (resultantData,))
        rowID += 1
    dataConnect.commit()


def generateRangedSyntheticData(query, column, fakeTable, dataLimit): #QUERY MUST ORDER DATA BY ASCENDING FOR ACCURATE RANGE
    raw_rows = curs.execute(query).fetchall()
    datas = [row for row in raw_rows if row is not None]
    checkSynR = list(curs.execute("SELECT * FROM "+fakeTable))
    rowID = 1
    limitHit = 1
    possibleVals = [val[0] for val in datas if val is not None]
    
    synthetic = list(np.random.choice(possibleVals, size=getAmount(queryAllOrg), p= calcDistributions(query)))

    for entry in synthetic:
        entry = int(entry)

        if(len(checkSynR) != 0):
            curs.execute(f"UPDATE {fakeTable} SET {column} = ? WHERE rowid = ?", (entry, rowID))
        else:
            curs.execute(f"INSERT INTO {fakeTable} ({column}) VALUES (?)", (entry,))
        rowID += 1
        if(limitHit == dataLimit):
            break
        else:
            limitHit += 1

    dataConnect.commit()

def generateSyntheticDates(fakeTable,column,start,end,amount): # seperated by t example: year-month-dayThour:minute:second
    timeList= []
    rowID=1
    for x in range(amount):
        start_dt = np.datetime64(start)
        end_dt = np.datetime64(end)

# Calculate total seconds between the limits
        total_seconds = (end_dt - start_dt).astype(int)

# Pick a random second offset
        random_seconds_offset = np.random.randint(0, total_seconds)


# Add the offset back to the start date
        random_datetime = start_dt + np.timedelta64(random_seconds_offset, 's')
        date = str(random_datetime)
        date=date.replace('T',' ')
        timeList.append(date)

    checkSynR = list(curs.execute("SELECT * FROM "+fakeTable))

    for time in timeList:
        if(len(checkSynR) != 0):  
            curs.execute(f"UPDATE {fakeTable} SET {column} = ? WHERE rowid = ?", (time, rowID))
        else:
            curs.execute(f"INSERT INTO {fakeTable} ({column}) VALUES (?)", (time,))
        rowID += 1

    dataConnect.commit()
    


#------------------CALLS-------------------
print(viewQuery(queryMostCommonPM, 5))
#print(viewQuery(queryReviewDist, -1))

print(viewQuery(queryOrderEachMonth, -1))
#print(df)
'''
print("Amount of customers in dataset: "+ str(curs.execute(queryCustAmount).fetchone()[0]))
print("Amount of orders in dataset: "+ str(curs.execute(queryOrderAmount).fetchone()[0]))
print(getTop(queryProducts, "Product Category", "Sales", 0, 1, 10))
print(getTop(querySellers, "Seller ID", "Revenue",0 , 2, 10))
print("Average Order Value: "+str(curs.execute(queryOrderAvg).fetchone()[0]))
print("City with most customers:"+ str(getTop(queryCities, "City", "Customers", 0, 1, 10)))
print("Seller Reviews Average:" +str(viewQuery(queryReviews, 50)))
print("Orders in Statuses: \n" +str(viewQuery(queryOrderStatus, 8)))
print("Highest Spending Customer + Money Spent: \n"+str(getMostAmountInCategory(queryHighSpending, 0, 2)))
print(viewQuery(queryOrderEachMonth, -1))

barGraph(queryCities, "City", "Customers", 0, 1)
barGraph(querySellers,"Seller ID", "Revenue",0,2)
barGraph(queryProducts, "ProductCategory", "Sales", 0, 1)


lineGraph(queryOrderEachMonth, "Month", "Orders", 0, 1)

pieChart(queryOrderStatus, "Order Status", "Amount of Orders", 0, 1)'''



dest_folder = "syn_output_data" 
new_db_path = os.path.join(dest_folder, "final_reports.db")
curs.execute(f"ATTACH DATABASE '{new_db_path}' AS external_db;")
os.makedirs(dest_folder, exist_ok=True)
curs.executescript(pp)
dataConnect.commit()





#print("median product value: "+calcMedian("product_value"))
#print("median freight value: "+calcMedian("freight_value"))
#print("median freight value: "+calcMedian("delivery_days"))


dest_folder = "syn_output_data" 
new_db_path = os.path.join(dest_folder, "final_reports.db")
curs.execute(f"ATTACH DATABASE '{new_db_path}' AS syn_db;")
os.makedirs(dest_folder, exist_ok=True)
curs.executescript(syn_table)
curs.executescript(summary_table)
dataConnect.commit()

generateSyntheticNumericalData("organized_data", "product_value", "empty_synthetic_data", 50, 1000)
generateSyntheticNumericalData("organized_data", "freight_value", "empty_synthetic_data", 50, 1000)
generateSyntheticNumericalData("organized_data", "total_payment", "empty_synthetic_data", 50, 1000)
generateSyntheticCategoricalData("review_score", "empty_synthetic_data", ["5","4","3","2","1"], queryReviewDist, 1000)
generateSyntheticCategoricalData("customer_state", "empty_synthetic_data", ["SP","RJ","MG","RS","PR",
                                                                            "SC","BA","DF","ES","GO",
                                                                            "PE","CE","PA","MT","MA",
                                                                            "MS","PB","PI","RN","AL",
                                                                            "SE","TO","RO","AM","AC",
                                                                            "AP","RR"], queryMostCommonStates, 1000)
generateSyntheticCategoricalData("payment_type", "empty_synthetic_data", ["boleto","credit_card",
                                                                          "debit_card","not_defined",
                                                                          "voucher"], queryPaymentTypes, 1000)
generateSyntheticID('syn_order_id','empty_synthetic_data',1000)
generateSyntheticDates('empty_synthetic_data','purchase_date','2016-10-03T00:00:00','2018-08-30T00:00:00',1000)

generateRangedSyntheticData(queryMaxInstallmentAmnt,"payment_installments", "empty_synthetic_data", 1000)
generateRangedSyntheticData(queryDeliveryDays, "delivery_days", "empty_synthetic_data", 1000)
generateResultingSyntheticData("product_value", "freight_value", "total_payment", "empty_synthetic_data")


OmeanPV=(viewQuery(queryMeanPV, -1))
OmeanFV=(viewQuery(queryMeanFV, -1))
OmeanDT=(viewQuery(queryMeanDT, -1))

SmeanPV=(viewQuery(synqueryMeanPV, -1))
SmeanFV=(viewQuery(synqueryMeanFV, -1))
SmeanDT=(viewQuery(synqueryMeanDT, -1))

Vars =['Product_Value', 'Freight_Value', 'Total_Payment', 'Delivery_Days']


insertIntoTable('Summary_Statistics','Variable',Vars)

dataConnect.close()

print("Code finished executing")