import sys
from threading import Thread
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as exp_c
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException, InvalidArgumentException

from mysql.connector import Error

from _property_specs import property_specs
from _item import item

WAIT_SECS = 20


def years_old(my_cursor, conn, go_to, item_id):

    driver2 = webdriver.Chrome("C:\\Users\\User\\Documents\\training day\\python\\scraping\\chromedriver")
    driver2.implicitly_wait(1)
    driver2.get( go_to )
    wait = WebDriverWait(driver2, 20)
    y_old = None

    # get years old
    try:
        elms = WebDriverWait( driver2, WAIT_SECS ).until( exp_c.presence_of_all_elements_located( (By.XPATH, '//*[@id="article-container"]/hgroup/ul/li') ) )
    except StaleElementReferenceException:
        pass
    except TimeoutException:
        pass
    else:
        for li_node in elms:

            if 'Antig' in li_node.text:
                try:
                    y_old = int( li_node.text.split()[0] )
                except IndexError:
                    pass
                except ValueError:
                    pass
                else:
                    break
            elif 'A estrenar' in li_node.text:
                y_old = 0
                break
            
        driver2.quit()
        
        try:
            my_cursor.execute('INSERT INTO prop_years_old VALUES(%s, %s);', (item_id, y_old) )
            conn.commit()
        except Error as e:
            print("error in query while inserting years_old", e)
            return False
        else:
            print("")
            print(">>> [property_data] >>> years_old: {} corresponding to item id: {}, was saved".format( y_old, item_id ) )
            return True
                

    



def property_data(driver, div, div_num, cursor, conn):

    item_info = item()
    prop_specs = property_specs()
    startup_elms = [ div, driver ]
    st_elms_index = 0

    title_xpath           = [ './div[1]/div[4]/div[1]/div[4]/h2',
                              '//*[@id="react-posting-cards"]/div/div[{}]/div[1]/div[4]/div[1]/div[4]/h2'.format( div_num ) ]
    
    price_xpath           = [ './div[1]/div[4]/div[1]/div[2]/div[1]/div/span[1]',
                              '//*[@id="react-posting-cards"]/div/div[{}]/div[1]/div[4]/div[1]/div[2]/div[1]/div/span[1]'.format( div_num ) ]
    
    expenses_xpath        = [ './div[1]/div[4]/div[1]/div[2]/div[1]/div/span[2]',
                              '//*[@id="react-posting-cards"]/div/div[{}]/div[1]/div[4]/div[1]/div[2]/div[1]/div/span[2]'.format( div_num ) ]

    
    city_xpath            = [ './div[1]/div[4]/div[1]/div[2]/div[2]/span[2]',
                              '//*[@id="react-posting-cards"]/div/div[{}]/div[1]/div[4]/div[1]/div[2]/div[2]/span[2]/span'.format( div_num ) ]

    location_xpath        = [ './div[1]/div[4]/div[1]/div[2]/div[2]/span[1]',
                              '//*[@id="react-posting-cards"]/div/div[{}]/div[1]/div[4]/div[1]/div[2]/div[2]/span[1]'.format( div_num ) ]

    numerical_specs_xpath = [ './div[1]/div[4]/div[1]/div[3]/ul/li',
                              '//*[@id="react-posting-cards"]/div/div[{}]/div[1]/div[4]/div[1]/div[3]/ul/li'.format( div_num ) ] # li text

    description_xpath     = [ './div[1]/div[4]/div[1]/div[5]',
                              '//*[@id="react-posting-cards"]/div/div[{}]/div[1]/div[4]/div[1]/div[5]'.format( div_num ) ]

    broker_xpath          = [ './div[1]/div[4]/div[2]/div[1]/div/a',
                              '//*[@id="react-posting-cards"]/div/div[{}]/div[1]/div[4]/div[2]/div[1]/div/a'.format( div_num ) ] #href



    for xpath in location_xpath:
        
        try:
            elm = WebDriverWait( startup_elms[ st_elms_index ], WAIT_SECS ).until( exp_c.presence_of_element_located( (By.XPATH, xpath) ) )
            item_info.location = elm.text
        
            #prop_specs.location = div.find_element( By.XPATH, location_xpath ).text 
        except NoSuchElementException:
            pass
        except StaleElementReferenceException:
            pass
        except TimeoutException:
            pass
        else:
            query = "SELECT id FROM items WHERE location='{}';".format( item_info.location )
            
            try:
                cursor.execute(query)
                row = cursor.fetchone()
    
            except Error as e:
                print("[property_data] >>> error in query while selection property id ", e)
                return None, None
            else:
                if row is not None:
                    print("[property_data] >>> {} is already INTO DATABASE".format( item_info.location ) )
                    return None, None

            break
        st_elms_index += 1
  

    print("[property_data] >>> location:", item_info.location)


    prop_specs.sale_or_rent = 'sale'
    print("[property_data] >>> sale or rent:", prop_specs.sale_or_rent)

    st_elms_index = 0
    
    for xpath in title_xpath:

        try:
            elm = WebDriverWait( startup_elms[ st_elms_index ], WAIT_SECS ).until( exp_c.presence_of_element_located( (By.XPATH, xpath) ) )
            item_info.title = elm.text
        
            #item_info.title = div.find_element( By.XPATH, title_xpath  ).text 
        except NoSuchElementException:
            pass
        except StaleElementReferenceException:
            pass
        except TimeoutException:
            pass
        else:
            break
        st_elms_index += 1

    print("[property_data] >>> title:", item_info.title)

    st_elms_index = 0
    
    for xpath in price_xpath:

        try:
            elm = WebDriverWait( startup_elms[ st_elms_index ], WAIT_SECS ).until( exp_c.presence_of_element_located( (By.XPATH, xpath) ) )
            item_info.price = elm.text
        
            #item_info.price = div.find_element( By.XPATH, price_xpath  ).text 
        except NoSuchElementException:
            pass
        except StaleElementReferenceException:
            pass
        except TimeoutException:
            pass
        else:
            # split currency and price
            if 'USD' in item_info.price:
                item_info.currency = 'USD'

                try:
                    item_info.price = item_info.price.replace('USD', '')
                    item_info.price = int( item_info.price.replace('.', '') )
                except ValueError:
                    pass
            
            elif '$' in item_info.price:
                item_info.currency = 'ARS'

                try:
                    item_info.price = item_info.price.replace('$', '') 
                    item_info.price = int( item_info.price.replace('.', '') )
                except ValueError:
                    pass

            break
        st_elms_index += 1

    if item_info.price is None or item_info.price == '':
        return None, None

        
    print("[property_data] >>> price currency:", item_info.currency)    
    print("[property_data] >>> price:", item_info.price)

    st_elms_index = 0
    
    for xpath in expenses_xpath:

        try:
            elm = WebDriverWait( startup_elms[ st_elms_index ], WAIT_SECS ).until( exp_c.presence_of_element_located( (By.XPATH, xpath) ) )
            prop_specs.expenses = elm.text
        
            #prop_specs.expenses = div.find_element( By.XPATH, expenses_xpath  ).text 
        except NoSuchElementException:
            pass
        except StaleElementReferenceException:
            pass
        except TimeoutException:
            pass
        else:
            # currency and expenses

            if 'USD' in prop_specs.expenses:
                prop_specs.exp_currency = 'USD'

                prop_specs.expenses = prop_specs.expenses.replace('+', '')
                prop_specs.expenses = prop_specs.expenses.replace('USD', '')
                prop_specs.expenses = prop_specs.expenses.replace('Expensas', '')

                try:
                    prop_specs.expenses = int( prop_specs.expenses.replace('.', '') )
                except ValueError:
                    pass
            
            elif '$' in prop_specs.expenses:
                prop_specs.exp_currency = 'ARS'
            
                prop_specs.expenses = prop_specs.expenses.replace('+', '')
                prop_specs.expenses = prop_specs.expenses.replace('$', '')
                prop_specs.expenses = prop_specs.expenses.replace('Expensas', '')
            
                try:        
                    prop_specs.expenses = int( prop_specs.expenses.replace('.', '') )
                except ValueError:
                    pass
            break
        st_elms_index += 1
        
            
    print("[property_data] >>> exp currency:", prop_specs.exp_currency)
    print("[property_data] >>> expenses:", prop_specs.expenses)

    st_elms_index = 0
    
    for xpath in city_xpath:

        try:
            elm = WebDriverWait( startup_elms[ st_elms_index ], WAIT_SECS ).until( exp_c.presence_of_element_located( (By.XPATH, xpath) ) )
            prop_specs.city = elm.text
        
            #prop_specs.city = div.find_element( By.XPATH, city_xpath  ).text 
        except NoSuchElementException:
            pass
        except StaleElementReferenceException:
            pass
        except TimeoutException:
            pass
        else:
            # hood and city

            ci_ho_splited = prop_specs.city.split(',')

            try:
                prop_specs.hood = ci_ho_splited[0]
                prop_specs.city = ci_ho_splited[1]
            except IndexError:
                pass

            break
        st_elms_index += 1

    print("[property_data] >>> city:", prop_specs.city)
    print("[property_data] >>> hood:", prop_specs.hood)

    st_elms_index = 0
    
    for xpath in numerical_specs_xpath:
    

        try:
            numerical_specs = WebDriverWait( startup_elms[ st_elms_index ], WAIT_SECS ).until( exp_c.presence_of_all_elements_located( (By.XPATH, xpath) ) )
        
            #numerical_specs = div.find_elements( By.XPATH, numerical_specs_xpath )
        except NoSuchElementException:
            pass
        except StaleElementReferenceException:
            pass
        except TimeoutException:
            pass
        else:
            # get li nodes text

            for li in numerical_specs:
                try:
                
                    if 'amb.' in li.text:
                        prop_specs.total_amb = int(li.text.split()[0])
                    elif 'dorm.' in li.text:
                        prop_specs.total_bedroom = int(li.text.split()[0])
                    elif 'baños' in li.text:
                        prop_specs.total_bathroom = int(li.text.split()[0])
                    elif 'coch.' in li.text:
                        prop_specs.total_garage = int(li.text.split()[0])
                    else:
                        prop_specs.total_surface = int(li.text.split()[0])
                      
                except ValueError:
                    pass
                except IndexError:
                    pass
            break
        st_elms_index += 1

    if prop_specs.total_surface is None and prop_specs.total_amb is None and prop_specs.total_bedroom is None and prop_specs.total_bathroom is None and prop_specs.total_garage is None:
        print("")
        print("[property_data] >>> CRITICAL ERROR: no numerical specs found")
        return None, None
            

    print("[property_data] >>> surface:", prop_specs.total_surface)
    print("[property_data] >>> amb:", prop_specs.total_amb)
    print("[property_data] >>> dorm:", prop_specs.total_bedroom)
    print("[property_data] >>> baños:", prop_specs.total_bathroom)
    print("[property_data] >>> coch:", prop_specs.total_garage)

    st_elms_index = 0
    
    for xpath in description_xpath:

        try:
            elm = WebDriverWait( startup_elms[ st_elms_index ], WAIT_SECS ).until( exp_c.presence_of_element_located( (By.XPATH, xpath) ) )
            prop_specs.description = elm.text
        
            #prop_specs.description = div.find_element( By.XPATH, description_xpath  ).text 
        except NoSuchElementException:
            pass
        except StaleElementReferenceException:
            pass
        except TimeoutException:
            pass
        else:
            break
        st_elms_index += 1


    if len( prop_specs.description ) > 3000:
        prop_specs.description = prop_specs.description[0:2999]
        

    if len( prop_specs.description ) > 100:
         print("[property_data] >>> description: {}...".format( prop_specs.description[0:100] ) )
    else:
         print("[property_data] >>> description:")


    st_elms_index = 0
    
    for xpath in broker_xpath:

        try:
            elm = WebDriverWait( startup_elms[ st_elms_index ], WAIT_SECS ).until( exp_c.presence_of_element_located( (By.XPATH, xpath) ) )
            prop_specs.broker = elm.get_attribute('href')
        
            #prop_specs.broker = div.find_element( By.XPATH, broker_xpath  ).get_attribute('href')
        except NoSuchElementException:
            pass
        except StaleElementReferenceException:
            pass
        except TimeoutException:
            pass
        else:
            break
        st_elms_index += 1

    print("[property_data] >>> broker:", prop_specs.broker)

    item_info.set_id(cursor)

    print("[property_data] >>> id:", item_info.id)

    # go to prop page
    try:
        a_node = WebDriverWait( div, WAIT_SECS ).until( exp_c.presence_of_element_located( (By.XPATH, './div[1]/div[4]/div[1]/div[4]/h2/a') ) )
    except StaleElementReferenceException:
        pass
    except TimeoutException:
        pass
    else:
        print( "[property_data] >>> going to:", a_node.get_attribute('href') )

        thread = Thread(target = years_old, args = ( cursor, conn, a_node.get_attribute( 'href' ), item_info.id, ))
        thread.start()
        thread.join()
    
    

    return item_info, prop_specs

