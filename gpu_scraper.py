import sqlite3
from requests import get
from bs4 import BeautifulSoup
import time
import random
import pandas as pd
import re
import math
from json import loads
from PCPartPicker_API import pcpartpicker

#Interface with SQL
def run_query(DB, q):
    with sqlite3.connect(DB) as conn:
        return pd.read_sql(q,conn)

def run_command(DB, c):
    with sqlite3.connect(DB) as conn:
        conn.execute('PRAGMA foreign_keys = ON;')
        conn.isolation_level = None
        conn.execute(c)
        
def run_inserts(DB, c, values):
    with sqlite3.connect(DB) as conn:
        conn.execute('PRAGMA foreign_keys = ON;')
        conn.isolation_level = None
        conn.execute(c, values) 
        
def scrape_card_list(DB = 'gpudata.db', sleep_min = 5, sleep_max = 15):
    start_time = time.time()
    pages = pcpartpicker.lists.total_pages("video-card")
    
    insert_query = '''
    INSERT OR IGNORE INTO card_specs(
        card_id,
        card_name,
        series,
        chipset_id,
        memory_in_GB,
        core_clock_in_GHz,
        ratings
    ) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
    '''

    insert_query_chipsets = '''
    INSERT OR IGNORE INTO chipsets(
        chipset_name
    ) 
    VALUES (?)
    '''
    
    #Pulls chipsets table from the database
    select_query_chipsets = 'SELECT * FROM chipsets'
    temp_chipsets_table = run_query(DB, select_query_chipsets)
    
    for i in range(1, pages+1):
        card_info = pcpartpicker.lists.get_list("video-card", i)

        for card in card_info:
            
            #Create the primary key
            card_id = card['id']
            
            #Skip any cards without a price tag
            if card['price'] == '':
                print('No price found for card_id: {0}'.format(card_id))
                continue
            
            
            #Cleans the chipset_name data
            chipset_name = card['chipset']

                    
            #Creates a row in the table 'chipsets' if chipset_name doesn't exist
            if chipset_name not in temp_chipsets_table['chipset_name'].values:
                try:
                    run_inserts(DB, insert_query_chipsets,[(chipset_name)])
                except Exception as e:
                    print('Failed to add into DB for {0}, {1}'.format(chipset_name, e))
                    pass
                    
                #Updates the temp_table
                temp_chipsets_table = run_query(DB, select_query_chipsets)
                    
            #Extracts the rest of the data
            chipset_id = temp_chipsets_table[temp_chipsets_table['chipset_name'] == chipset_name]['chipset_id'].values[0]
            card_name = card['name']
            series = card['series']
            memory = card['memory']
            core_clock = card['core-clock']
            ratings = card['ratings']
            
            #Unit conversions for 'memory' and 'core_clock'
            if 'MB' in memory:
                memory_in_GB = float(memory.split('MB')[0])/1000.00
            else: 
                memory_in_GB = memory.split('GB')[0]                
            
            if 'MHz' in core_clock:
                core_clock_in_GHz = float(core_clock.split('MHz')[0])/1000.00
            else: 
                core_clock_in_GHz = core_clock.split('GHz')[0] 
                  
            #Insert into the the table 'card_specs'
            try:
                run_inserts(DB, insert_query,(
                    card_id, card_name, series, int(chipset_id), float(memory_in_GB), float(core_clock_in_GHz), \
                    int(ratings), 
                    )
                )
            except Exception as e:
                print('Failed to add into DB for card_id: {0}, {1}'.format(card_id, e))
                pass
            
        #Provide stats for monitoring
        current_time = time.time()
        elapsed_time = current_time - start_time
        requests = i
        print('-------------------')
        print('Requests Completed: {}; Frequency: {} requests/s'.format(requests, requests/elapsed_time))
        print('Elapased Time: {} minutes'.format(elapsed_time/60))
        if requests == pages:
            print('Scrape Complete')
            break
        print('Pausing...')    
        time.sleep(random.uniform(sleep_min, sleep_max))
        
def scrape_card_page(DB = 'gpudata.db', prefix = '', history_days = 730, sleep_min = 5, sleep_max = 15):
    start_time = time.time()
    
    insert_query_prices = '''
    INSERT OR IGNORE INTO card_prices(
        card_id,
        merchant_id,
        datetime,
        price
    ) 
    VALUES (?, ?, ?, ?)
    '''

    insert_query_merchants = '''
    INSERT OR IGNORE INTO merchants(
        merchant_name
    ) 
    VALUES (?)
    '''
    
    update_query_card_specs = '''
    UPDATE card_specs
        SET 
            manufacturer=?,
            part_number=?,
            interface=?,
            memory_type=?,
            tdp_in_watts=?,
            fan=?,
            sli_support=?,
            crossfire_support=?,
            hdmi=?
        WHERE
            card_id=?
    '''
                 
    #Pulls merchants table from the database
    select_query_merchants = 'SELECT * FROM merchants'
    temp_merchants_table = run_query(DB, select_query_merchants)
    
    #Pulls card_ids table from the table gpu_specs
    pull_ids = 'SELECT card_id FROM card_specs'
    card_ids = run_query(DB, pull_ids)['card_id']
    
    for counter, card_id in enumerate(card_ids):
        
        #Makes a connection to the item webpage
        url = 'http://{0}pcpartpicker.com/product/{1}?history_days={2}'.format(prefix, card_id, history_days)
        headers ={"User-Agent": "gpudata web scraper for research, contact me at https://codingdisciple.com"}
        successful_connection = False
        connection_attempts = 0
        while not successful_connection:
            try:
                response = get(url=url, headers=headers)
                print('Connection successful.')
                successful_connection = True
            except:
                print('Connection unsuccessful, reconnecting...')
                connection_attempts += 1
                time.sleep(random.uniform(sleep_min, sleep_max))
                if connection_attempts == 10:
                    raise
                    
        html_soup = BeautifulSoup(response.text, 'html.parser')
        
        #Search for the raw data
        scripts = html_soup.findAll('script')
        for script in scripts:
            if 'phistmulti' in script.text:
                data = script.prettify().split('\n')
                for line in data:
                    if 'phistmulti' in line:
                        idx = line.index('[')
                        price_history = line[idx:-1]
                        price_data = loads(price_history)
                        break
        
        #Extracts price/merchant data
        for merchant in price_data:
            
            #Creates a row in the table 'merchants' if merchant_name doesn't exist
            merchant_name = merchant['label']
            if merchant_name != 'No price history is available for this time period.':
                if merchant_name not in temp_merchants_table['merchant_name'].values:
                    try:
                        run_inserts(DB, insert_query_merchants,[(merchant_name)])
                    except Exception as e:
                        print('Failed to add into DB for {0}, {1}'.format(merchant_name, e))
                        pass
                    
                    #Updates the temp_table
                    temp_merchants_table = run_query(DB, select_query_merchants)
                
            for date_points in merchant['data']:
                datetime = date_points[0]
                price = date_points[1]
                merchant_id = temp_merchants_table[temp_merchants_table['merchant_name'] == merchant_name]['merchant_id'].values[0]

                try:
                    run_inserts(DB, insert_query_prices,(
                        card_id, int(merchant_id), float(datetime/1000.00), float(price/100.00) 
                        )
                    )
                except Exception as e:
                    print('Failed to add into DB for card_id: {0}, datetime: {1}, merchant: {2}, {3}'.format(card_id, datetime, merchant_id, e))
                    pass
                
        #Updates the specs_table
        specs_block = html_soup.find('div', class_='specs block')
        
        #Shortens try/except loop code
        def find_specs(specs_block, keyword, failure_value):
            try:
                return specs_block.find(text=keyword).find_parent('h4').next_sibling.strip()
            except Exception as e:
                print(e)
                return failure_value
        
        manufacturer = find_specs(specs_block, 'Manufacturer', 'null')
        part_number = find_specs(specs_block, 'Part #', 'null')
        interface = find_specs(specs_block, 'Interface', 'null')
        memory_type = find_specs(specs_block, 'Memory Type', 'null')
        fan = find_specs(specs_block, 'Fan', 'null')
        sli_support = find_specs(specs_block, 'SLI Support', 'null')
        crossfire_support = find_specs(specs_block, 'CrossFire Support', 'null')
        hdmi = find_specs(specs_block, 'HDMI', 0)
        tdp = find_specs(specs_block, 'TDP', 0)
        if ' Watts' in tdp:
            tdp_in_watts = tdp.replace(' Watts', '')
            
        try:
            run_inserts(DB, update_query_card_specs,(
                manufacturer, part_number, interface, memory_type, \
                int(tdp_in_watts), fan, sli_support, \
                crossfire_support, int(hdmi) ,card_id
                )
            )
        except Exception as e:
            print('Failed to update card_specs for card_id: {0}, {1}'.format(card_id, e))
            pass        

        #Provide stats for monitoring
        current_time = time.time()
        elapsed_time = current_time - start_time
        requests = counter + 1
        print('-------------------')
        print('Requests Completed: {}; Frequency: {} requests/s'.format(requests, requests/elapsed_time))
        print('Elapased Time: {} minutes'.format(elapsed_time/60))
        if requests == len(card_ids):
            print('Scrape Complete')
            break
        print('Pausing...')    
        time.sleep(random.uniform(sleep_min, sleep_max))

def scrape_benchmarks(DB = 'gpudata.db', sleep_min = 5, sleep_max = 15):
    start_time = time.time()
    
    insert_query_benchmarks = '''
    INSERT OR IGNORE INTO benchmarks(
        chipset_id,
        passmark_g3d,
        passmark_direct_compute
    ) 
    VALUES (?, ?, ?)
    '''
    
    #Get chipset_names from the database
    chipsets = run_query(DB, 'SELECT * FROM chipsets')
    db_names = chipsets['chipset_name']
    
    #Request information
    url_1 = 'https://www.videocardbenchmark.net/directCompute.html'
    url_2 = 'https://www.videocardbenchmark.net/GPU_mega_page.html'
    headers ={"User-Agent": "gpudata web scraper for research, contact me at https://codingdisciple.com"}
    successful_connection = False
    connection_attempts = 0
    
    #Makes a connection to the passmark webpage
    while not successful_connection:
        try:
            print ('Connecting to {}'.format(url_1))
            response_1 = get(url=url_1, headers=headers) 
            time.sleep(random.uniform(sleep_min, sleep_max))
            print('Pausing...')
            print ('Connecting to {}'.format(url_2))
            response_2 = get(url=url_2, headers=headers)
            print('Connection successful.')
            successful_connection = True    
        except:
            print('Connection unsuccessful, reconnecting...')
            connection_attempts += 1
            time.sleep(random.uniform(sleep_min, sleep_max))
            if connection_attempts == 10:
                raise
    
    #Create the soup objects
    html_soup1 = BeautifulSoup(response_1.text, 'html.parser')
    html_soup2 = BeautifulSoup(response_2.text, 'html.parser')    
    
    #Create a list of chipset names from passmark
    banlist = ('TITAN Xp COLLECTORS EDITION', 'GeForce GTX 1060 with Max-Q Design')
    html_soup2_body = html_soup2.find('tbody')
    passmark_names = [i.text for i in html_soup2_body.select('a[href^="video_lookup.php"]') if i.text not in banlist]
    
    #Log of names that could not be found in passmark_names or required regex searches
    no_names = []
    searched_names = []
    
    #Loop through the database chipset_names
    for db_id, chipset_name in enumerate(db_names):
        db_id += 1
        print('-'*len(chipset_name))
        print(chipset_name)
        print('-'*len(chipset_name))

        #Search for exact chipset_name matches:        
        name_found = False
        try:
            passmark_g3d = html_soup2.find(text=chipset_name).find_parent('tr').find_all('td')[2].text.replace(',', '').replace(' ', '')
            passmark_direct_compute = html_soup1.find(text=chipset_name).find_parent('tr').find('div').text.replace(',', '')
            name_found = True
            print('Adding to table "benchmarks", passmark_g3d: {}'.format(passmark_g3d))
            print('Adding to table "benchmarks", passmark_direct_compute: {}'.format(passmark_direct_compute))        
        except Exception as e:
            problematic_name = chipset_name
            print('Exact search failed, finding closest match')
        
        #Regex search chipset name in passmark_names
        if name_found == False:
            problematic_name = problematic_name.lower().split(' - ')[0]
            for actual_name in passmark_names:
                if re.findall(r'{}'.format(problematic_name), actual_name.lower()) != []:
                    print('Next match found: {}'.format(actual_name))
                    try:
                        passmark_g3d = html_soup2.find(text=actual_name).find_parent('tr').find_all('td')[2].text.replace(',', '').replace(' ', '')
                        passmark_direct_compute = html_soup1.find(text=actual_name).find_parent('tr').find('div').text.replace(',', '')
                        print('Adding to table "benchmarks", passmark_g3d: {}'.format(passmark_g3d))
                        print('Adding to table "benchmarks", passmark_direct_compute: {}'.format(passmark_direct_compute))                    
                        name_found = True
                        searched_names.append([chipset_name, actual_name])
                    except:
                        passmark_g3d = 'null'
                        passmark_direct_compute = 'null'
                    break
                    
        #Manual inserts for PassMark typo
        if chipset_name == 'GeForce GTX 1060 6GB':
            actual_name = 'GeForce GTX 1060 5GB'
            print('Manually inserting {}'.format(actual_name))            
            try:
                passmark_g3d = html_soup2.find(text=actual_name).find_parent('tr').find_all('td')[2].text.replace(',', '').replace(' ', '')
                passmark_direct_compute = html_soup1.find(text=actual_name).find_parent('tr').find('div').text.replace(',', '')            
                print('Adding to table "benchmarks", passmark_g3d: {}'.format(passmark_g3d))
                print('Adding to table "benchmarks", passmark_direct_compute: {}'.format(passmark_direct_compute))                    
                name_found = True
                searched_names.append([chipset_name, actual_name])
            except:
                passmark_g3d = 'null'
                passmark_direct_compute = 'null'  
                
        #Add to the database            
        if name_found == True:
            try:
                run_inserts(DB, insert_query_benchmarks,(
                    int(db_id), int(passmark_g3d), int(passmark_direct_compute)
                    )
                )
                print('Successfully added to database')
            except Exception as e:
                print('Failed to add to benchmarks for chipset_id: {0}, {1}'.format(db_id, e))
                no_names.append(chipset_name)
                continue        
        else:
            print('Failed to add to benchmarks for chipset_id: {0}, {1}'.format(db_id, chipset_name))
            no_names.append(chipset_name)
    
    print('Scrape Summary:')
    print('---- Closest matches (chipset_name, passmark_name) ----')
    print(searched_names)
    print('---- No matches found (chipset_name) ----')
    print(no_names)  


def run_all():
    scrape_card_list()
    scrape_card_page()
    scrape_benchmarks()        
    
if __name__ == '__main__':
    scrape_card_list()
    scrape_card_page()
    scrape_benchmarks()
    