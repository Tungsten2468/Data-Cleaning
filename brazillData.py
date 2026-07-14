import _sqlite3 as SQ
import pandas as pan
import os
import matplotlib.pyplot as plt 

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

#------------------FUNCTIONS-------------------
def fixDeliveryDays(wrongValue, row):
    return
def getAmount(query): #just counts entires
    amount = 0
    for entry in curs.execute(query):
        amount += 1
    return amount

def noTuple(whatQuery): #makes the query not a tuple for easy use
    tupless = [row for row in whatQuery]
    return tupless

#-1 = no limit
def viewQuery(whatQuery, lim): #prints the query for easy viewing/debugging
    if(lim != -1):
        rows = curs.execute(whatQuery, (lim,)).fetchall()
    else:
        rows = curs.execute(whatQuery).fetchall()
    headers = [desc[0] for desc in curs.description]

    print(headers)
    for row in rows:
        print(row)
    
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

#------------------CALLS-------------------

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


pp ='''CREATE TABLE IF NOT EXISTS external_db.new_table AS 
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

dest_folder = "syn_output_data" 
new_db_path = os.path.join(dest_folder, "final_reports.db")
curs.execute(f"ATTACH DATABASE '{new_db_path}' AS external_db;")
os.makedirs(dest_folder, exist_ok=True)
curs.executescript(pp)
dataConnect.commit()

curs.execute("DETACH DATABASE external_db;")
dataConnect.close()