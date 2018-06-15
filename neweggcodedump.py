'''
Project scope: page 1: GPU analytics data
page 2: cryto data?

'''
#Legacy table

#Create the newegg table
c1 = """
CREATE TABLE newegg(
    item_id TEXT,
    scrape_time FLOAT,
    GPU TEXT,
    price FLOAT,
    rating TEXT,
    brand TEXT,
    description TEXT,
    core_clock TEXT,
    max_resolution TEXT,
    display_ports TEXT,
    DVI TEXT,
    model TEXT,
    PRIMARY KEY(item_id, scrape_time)
); 
"""


#newegg gpu data scraper
def scrape_newegg(DB='gpudata.db', sleep_min=9, sleep_max=18):    
    start_time = time.time()
    
    insert_query = '''
    INSERT OR IGNORE INTO newegg(
        item_id,
        scrape_time,
        GPU,
        price,
        brand,
        rating,
        description,
        core_clock,
        max_resolution,
        display_ports,
        DVI,
        model
        ) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    
    url_1080 = 'https://www.newegg.com/Product/ProductList.aspx?Submit=Property&N=100007709%20601194948&IsNodeId=1&bop=And&Page=1&PageSize=96&order=BESTMATCH'
    url_1080ti = 'https://www.newegg.com/Product/ProductList.aspx?Submit=Property&N=100007709%20601294835&IsNodeId=1&bop=And&PageSize=96&order=BESTMATCH'
    url_1060 = 'https://www.newegg.com/Product/ProductList.aspx?Submit=Property&N=100007709%20601205646&IsNodeId=1&bop=And&PageSize=96&order=BESTMATCH'
    url_1070 = 'https://www.newegg.com/Product/ProductList.aspx?Submit=Property&N=100007709%20601202919&IsNodeId=1&bop=And&PageSize=96&order=BESTMATCH'
    url_1070ti = 'https://www.newegg.com/Product/ProductList.aspx?Submit=Property&N=100007709%20601305993&IsNodeId=1&bop=And&PageSize=96&order=BESTMATCH'
    url_1050 = 'https://www.newegg.com/Product/ProductList.aspx?Submit=Property&N=100007709%20601273511&IsNodeId=1&bop=And&PageSize=96&order=BESTMATCH'
    url_1050ti = 'https://www.newegg.com/Product/ProductList.aspx?Submit=Property&N=100007709%20601273503&IsNodeId=1&bop=And&PageSize=96&order=BESTMATCH'
    urls = [url_1050, url_1050ti, url_1060, url_1070, url_1070ti, url_1080, url_1080ti]    
    gpus = ['GTX_1050', 'GTX_1050_Ti', 'GTX_1060', 'GTX_1070', 'GTX_1070_Ti', 'GTX_1080', 'GTX_1080_Ti']
    
    headers = {"User-Agent": "gpu price data scraper for research."}
    
    for counter, url in enumerate(urls):
        print('Scraping: {}'.format(url))
        
        
        #Handle timeouts
        try:
            response = get(url, headers=headers, timeout = 10)
        except:
            print('Request timeout')
            pass

        if response.status_code != 200:
            print('Request: {}; Status code: {}'.format(requests, response.status_code))
            pass

        #Creates the soup object    
        html_soup = BeautifulSoup(response.text, 'html.parser')
        containers = html_soup.find_all('div', class_ = 'item-container')

        #Loops through the containers on a page
        for container in containers:
            
            #Item Id (Primary Key)
            item_id = container.find('a', class_='item-img').attrs['href'].split('Item=')[1]
            GPU = gpus[counter]
            scrape_time = start_time
            #Product Info
            try:
                price = container.find('li', class_='price-current').text.split('$')[1].split('\xa0')[0].replace(',', '')
            except:
                pass
            try:
                brand = container.find_all('img')[1].attrs['title']
            except:
                brand = 'NaN' 
            try:
                description = container.find('a', class_='item-title').text
            except:
                description = 'NaN'
            try: 
                rating = container.find('a', class_='item-rating').text[1]
            except:
                rating = 'NaN'           
            
            #Features
            features = container.find('ul', class_='item-features')            
            try:
                core_clock = features.find(text='Core Clock:').find_parent('li').text.replace('\n' ,' ').split(': ')[1]
            except:
                core_clock = 'NaN'
            try:
                max_resolution = features.find(text='Max Resolution:').find_parent('li').text.replace('\n' ,' ').split(': ')[1]
            except:
                max_resolution = 'NaN'
            try:
                display_ports = features.find(text='DisplayPort:').find_parent('li').text.replace('\n' ,' ').split(': ')[1]
            except:
                display_ports = 'NaN'
            try:
                DVI = features.find(text='DVI:').find_parent('li').text.replace('\n' ,' ').split(': ')[1]
            except:
                DVI = 'NaN'
            try:
                model = features.find(text='Model #: ').find_parent('li').text.replace('\n' ,' ').split(': ')[1]
            except:
                model = 'NaN'
            
            #Write into SQL database
            try:
                run_inserts(DB, insert_query,(
                    item_id, scrape_time, GPU, float(price), brand, rating, \
                    description, core_clock, \
                    max_resolution, display_ports, DVI, model)
                )
            except Exception as e:
                print('Failed to add into DB for item_id: {0}, {1}'.format(item_id, e))
                pass

        #Provide stats for monitoring
        current_time = time.time()
        elapsed_time = current_time - start_time
        requests = counter

        print('Requests Completed: {}; Frequency: {} requests/s'.format(requests, requests/elapsed_time))
        print('Elapased Time: {} minutes'.format(elapsed_time/60))
        if requests == len(urls)-1:
            clear_output(wait = True)
            print('Scrape Complete')
            break
        print('Pausing...')    
        time.sleep(random.uniform(sleep_min, sleep_max))   
        clear_output(wait = True)