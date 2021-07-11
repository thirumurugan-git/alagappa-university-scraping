import requests
from bs4 import BeautifulSoup as bs
from csv import writer
import os
import sys


base_url = "http://162.241.27.72"

url = "http://162.241.27.72/modules/DDE/book_materials.php"

headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Accept-Encoding": "gzip, deflate, br", "Accept-Language": "en-US,en;q=0.5", "Upgrade-Insecure-Requests": "1", "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"}

# each_book design 

# 0 index - degree type 
# 1 index - degree name
# 2 index - course name
# 3 index - topic name
# 4 index - link to download


def csv_upload(sem, book):
    csv_file = "info.csv"
    if not os.path.isfile(csv_file):
        li = ("identifier", "title", "publisher", "creator", "file", "collection", "mediatype", "source", "description")
        with open(csv_file, 'w') as f:
            obj = writer(f)
            obj.writerow(li)
 
    identifier = book[3].lower().replace(',','')
    title = book[3].replace(',','')
    publisher = ""
    creator = ""
    file = title+".pdf"
    collection = "ServantsOfKnowledge"
    mediatype = "text"
    source = "Alagappa University"
    description = "semester - %d;"%sem +book[0].replace(',','') + ";" + book[1].replace(',','') + ";" + book[2].replace(',','')
    
    data = [identifier, title, publisher, creator, file, collection, mediatype, source, description]
    

    with open(csv_file, 'a') as f:
        obj = writer(f)
        obj.writerow(data)

def make_last_file(book):
    with open('last_file_visited.txt', 'w') as f:
        f.write(book[3])

def each_book_downloader(each_book, start = None):
    starter = start
    if start == None :
        starter = each_book[0][0][3] # 3 denotes topic name of the book
    
    last_visited = False
    
    for ind, semester in enumerate(each_book):
        for book in semester:
            
            # start from last visited
            if not last_visited:
                if starter == book[3]:
                    last_visited = True
                else:
                    continue
                
            try:
                book_url = book[4].replace('../..',base_url)
                resp = requests.get(book_url, headers = headers)
                filename = book[3].replace(',','')
                with open(filename+".pdf", 'wb') as f:
                    f.write(resp.content)
                csv_upload(ind + 1, book)
                print('completed ------------------' + book[3])
    
            except:
                print("error book:", book[3])
                print('quiting.....')
                make_last_file(book)
                sys.exit()

def download_book(each_book):
    user_input = str(input("want to continue from last file[y/n]: "))
    if user_input == "n":
        each_book_downloader(each_book)
    elif user_input == "y":
        last_book_name = str(input("enter the last book downloaded: "))
        each_book_downloader(each_book, last_book_name)
    else:
        print("please provide valid option")
    

def get_each_book(all_semester):
    each_book = []
    for semester in all_semester:
        temp = []
        all_tr = semester.find_all('tr')
        for tr in all_tr:
            all_td = tr.find_all('td')
            appending_data = [ td.text for td in all_td]
            appending_data[-1] = all_td[-1].find('a')['href']
            temp.append(appending_data)
        each_book.append(temp)
    return each_book
    

def find_semester(html):
    
    temp = html.find_all("tbody")
    
    # length of temp is 6, so each there are 6 semester
    
    return temp

with requests.Session() as s:

    resp = s.get(url, headers = headers)

    html = bs(resp.content, 'html.parser')

    # all semester book
    all_semester = find_semester(html)
    
    each_book = get_each_book(all_semester)

    download_book(each_book)
