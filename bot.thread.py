import requests
import re
import os
import threading
from queue import Queue
from bs4 import BeautifulSoup
gqueue = []
title_list = []
UNI = []
with open('UK Universities', 'r') as f:
    for line in f:
        UNI.append(line.strip())

# Create a new folder
def create_folder(folder_path):
    os.makedirs(folder_path)

# Save the file
def save_file(folder_path, filename, content):
    # Create the full file path
    file_path = os.path.join(folder_path, filename)

    with open(file_path, 'a', encoding="utf-8") as file:
        file.write(content+"\n")    

class bot:
    title = 'University'
    pge_url = ''
    def __init__(self, page_url):
        pge_url = page_url
        bot.Gather_links(page_url)
        create_folder(bot.title)
        
        with open(bot.title+'/'+bot.title+'_queue', 'a') as f:
            for link in gqueue:
                f.write(link + '\n')
            
    
    #resolving broken links
    def Resolve(url):
        if re.match(r"^//www\..+", url):
            i = pge_url.split(':')
            new_url = i[0] +':' + url
            return new_url
        elif re.match(r"^/\w+.+",url):
            new_url = pge_url + url
            return new_url            
        else:
            return url

    #Domain check
    def Domain_check(url):
        url = bot.Resolve(url)
        domain = pge_url.split('/')[2]
        url_split = url.split('/')
        if domain in url_split:
            return url
        else:
            return ''
            
    #Crawl Page   
    def Crawl_webpage(thread_name, url):
        
        
        try:
            response = requests.get(url)
        except: 
            print(f"Couldn't connect to: {url}")
            return None  
        print(thread_name + ' crawling ' + url)
        gqueue.remove(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        if soup.title:
            title = soup.title.text
            title_list.append(title)
        else:
            title_list.append('')
        text_content = soup.get_text()
        html_content = response.text
        save_file(bot.title, bot.title+'_html', html_content)
        save_file(bot.title, bot.title+'_text', text_content) 
        save_file(bot.title, bot.title+'_crawled', url)
        save_file(bot.title, bot.title+'_title', title)
    #Opening links to get Links within
    def Sub_gather_links(): 
            for link in gqueue:
                if len(gqueue) <= 300:
                    response = requests.get(link)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    a_tags = soup.find_all('a')
                
                    for a in a_tags:
                        href = a.get('href')
                        if href is not None: 
                            if href.startswith('#') or href=='/':
                                continue
                            url = bot.Domain_check(href)
                            if len(gqueue) <= 300:
                                if url != '' and url not in gqueue:
                                    if url.endswith('.pdf'):
                                        continue
                                    else:
                                        print(f'queuing:  {url}')
                                        gqueue.append(url)
                                else:
                                    continue
                            else:
                                print(f"Queue is full: {len(gqueue)}")
                                return ''
                          
                else:
                    print(f"Queue is full: {len(gqueue)}")
                    return ''       
            
    #Initial Gathering of links on homepage
    def Gather_links(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        if soup.title:
            bot.title = soup.title.text
            
        a_tags = soup.find_all('a')
            
        for a in a_tags:
            href = a.get('href')
            if href is not None: 
                if href.startswith('#') or href=='/':
                        continue
                url = bot.Domain_check(href)
                if url != '' and url not in gqueue:
                    if url.endswith('.pdf'):
                        continue
                    else:
                        print(f'queuing:  {url}')
                        gqueue.append(url)
            
        bot.Sub_gather_links()
        


NUMBER_OF_THREADS = 350
QUEUE_FILE = bot.title+'queue'

queue = Queue()

#ceating worker threads. dies after main exits
def create_threads():
    for _ in range(NUMBER_OF_THREADS):
            t = threading.Thread(target= job)
            t.daemon = True
            t.start()

#do the next job in queue and informs when it is done
def job():
    url = queue.get()
    bot.Crawl_webpage(threading.current_thread().name, url)
    queue.task_done()           
    

#creating jobs. turning Each Queue link into a new job
def create_jobs():
    #passing queue file to thread queue
    for link in gqueue:
        queue.put(link)
    #eliminaing bot traffic jam by ensuring they all wait their turn
    queue.join()
    #updating state and making job creation continuous
    crawler()

#check if there are items in queue, if so, crawl the queue
def  crawler():
    if len(gqueue) >0:
       create_jobs()
    else:
        print('Crawling done') 
            
         
            

for link in UNI:
    pge_url = link
    bot(link)                
    create_threads()
    crawler()   
    