import sys
sys.path.append( "C:\\mysql-connector-python-8.0.26" )
import mysql.connector as myc
from mysql.connector import Error


def save_specs_into_db(conn, my_cursor, specs, item_id):

    if specs is None:
        return False

    query = """INSERT INTO property_specs 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    vals = (specs.sale_or_rent,            
            specs.city,         
            specs.hood,           
            specs.expenses,          
            specs.total_surface, 
            specs.total_amb,        
            specs.total_bedroom,           
            specs.total_garage,           
            specs.description,
            specs.broker,
            item_id,
            specs.exp_currency,
            specs.total_bathroom,
            specs.years_old )

    try:
        my_cursor.execute(query, vals)
        conn.commit()
    except Error as e:
        print("error in query while inserting vpescs", e)
        return False
    else:
        print(">>> [specs saved]")
        return True
        
