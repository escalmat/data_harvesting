import sys
sys.path.append( "C:\\mysql-connector-python-8.0.26" )
import mysql.connector as myc
from mysql.connector import Error


def save_item_into_db(conn, my_cursor, itinfo, item_type):

    if itinfo is None:
        return False

    query = """INSERT INTO items (  state,
                                    nsales,
                                    title,
                                    brand,
                                    ml_category_rank,
                                    price,
                                    model,
                                    id,
                                    seller,
                                    location,
                                    mpx_frontal_cam,
                                    mpx_rear_cam,
                                    screen_size,
                                    internal_memo,
                                    battery_span,
                                    resolution_type,
                                    with_touch_screen,
                                    extra_specs,
                                    parent,
                                    currency,
                                    ad_date,
                                    item_type )
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    
    vals = ( itinfo.state,            
             itinfo.nsales,         
             itinfo.title,           
             itinfo.brand,          
             itinfo.ml_category_rank, 
             itinfo.price,        
             itinfo.model,           
             itinfo.id,           
             itinfo.seller,          
             itinfo.location,                  

             itinfo.mpx_frontal_cam,  
             itinfo.mpx_rear_cam,     
        
             itinfo.screen_size,      
             itinfo.internal_memo,   
        
             itinfo.batery_span,       
             itinfo.resolution_type,   
             itinfo.with_touch_screen,
             itinfo.get_extra_specs(),
             None,
             itinfo.currency,
             itinfo.ad_date,
             item_type ) 
    
    

    try:
        my_cursor.execute(query, vals)
        conn.commit()
    except Error as e:
        print("error in query while inserting a product", e)
        return False
    else:
        print(">>> [item saved]")
        return True
