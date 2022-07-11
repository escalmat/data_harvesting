import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as exp_c
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException, InvalidArgumentException
from time import sleep
sys.path.append( "C:\\mysql-connector-python-8.0.26" )
import mysql.connector as myc
from mysql.connector import Error
sys.path.append("c:\\users\\user\\anaconda3\\lib\\site-packages")
from unidecode import unidecode

from _property_data import property_data
from _save_item import save_item_into_db
from _save_specs import save_specs_into_db

WAIT_SECS = 40


try:
    connection = myc.connect(host="localhost",
                             database="scraping",
                             user="root",
                             password="")
    
    if connection.is_connected():
        server_info = connection.get_server_info()
        print(">>> connected to mysql server ", server_info)
        
        mycursor = connection.cursor(buffered=True)

        paths_info = mycursor.execute("SELECT path, id FROM ml")

        if paths_info:
            search_dict = { var : index for index, var in enumerate(paths_info) }
        
except Error as e:
    
    print("error while connecting to mysql ", e)
    
else:
    
    counter=0 # change the index of the page 
    reload_counter = 0
    
    while True:

        url = 'https://www.zonaprop.com.ar/departamentos-venta-villa-crespo-pagina-{}.html'.format( counter ) # put specific neighbourhood here
        counter += 1

        driver = webdriver.Chrome("") # your chromedriver exe path here
        driver.implicitly_wait(1)
        
        driver.get( url )

        try:

            driver.maximize_window()

        except TimeoutException:
            print(">>> time out while trying to get:", url)
            break
        
        wait = WebDriverWait(driver, 20)

        #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        try:
            error_button = WebDriverWait( driver, 60 ).until( exp_c.presence_of_element_located( (By.CLASS_NAME, 'mdl-close-btn') ) )
        except TimeoutException:
            print(">>> ERROR: couldn't find javascript's popup close button")

            if reload_counter == 5:
                break

            reload_counter += 1

            driver.quit()
        
            sleep(240)
        
            continue
        else:

            try:
                driver.execute_script("document.querySelector('#modalContent > div > button').click()")
            except:
                print(">>> ERROR: while trying to click javascript's popup close button")
                break
        
        try:
            
            property_divs = WebDriverWait( driver, WAIT_SECS ).until( exp_c.presence_of_all_elements_located( (By.XPATH, '//*[@id="react-posting-cards"]/div/div') ) )
            print(">>> number of div found: ", len(property_divs) )

        except TimeoutException:
            print(">>> no properties found")
            pass
        else:
            
            prop_data_saved_counter = 0
            div_num = 0
            
            for div in property_divs:

                prop_data_saved = False

                print("")

                item, item_specs = property_data( driver,
                                                  div,
                                                  div_num,
                                                  mycursor,
                                                  connection )

                div_num += 1

                if item is None or item_specs is None:
                    continue
            
                prop_data_saved = save_item_into_db( conn=connection,
                                                     my_cursor=mycursor,
                                                     itinfo=item,
                                                     item_type='property' )

                if not prop_data_saved:
                    continue

                prop_data_saved = save_specs_into_db( conn=connection,
                                                      my_cursor=mycursor,
                                                      specs=item_specs,
                                                      item_id=item.id )

                if prop_data_saved:
                    prop_data_saved_counter += 1
                    
                    
        print("")
        print(">>> TOTAL PROPERTIES SAVED -----------------------------------------> {}".format( prop_data_saved_counter ) )
        
        
        driver.quit()
        
        sleep(180)
        
        
