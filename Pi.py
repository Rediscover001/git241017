import csv
import time
from time import sleep
import re
import bs4
import requests
import os
import random
import threading
"""
def creat_file(name):
    if not os.path.exists(name):
        os.mkdir(name)
    else:
        print('The fild named {} already exists'.format(name))
"""
def request_content(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0"}
    response = requests.get(url, headers=headers)
   # print(response.status_code)
    return response.text

def down_info(url):
    with (open(file="Star_Info.csv",mode="w",encoding= "utf-8") as SI):
        writer = csv.writer(SI)
        writer.writerow(['Name','Age','Nation','Video Quantity','Url'])

        for page in range(1,112):
            url = url + str(page)
            pre_soup = bs4.BeautifulSoup(request_content(url), 'html.parser')
            if not pre_soup:
                continue
            else:
                star_list = pre_soup.find_all('a', class_='model-top__img model-top__img--video')
                video_quantity_list = pre_soup.find_all(class_ = 'model-top__scene')

                quantity = []
                for video_quantity in video_quantity_list:
                    b_tag = video_quantity.find('b').text
                    quantity.append(b_tag if b_tag else "N/A")
                print(quantity)
            k = 0
            for star in star_list:
                star_info_url = star.get('href')
                star_info = bs4.BeautifulSoup(request_content(star_info_url),'html.parser')
                star_name = star_info.find('h1',class_ = 'model__title').text
                star_nation = star_info.find('a',class_ = 'text-primary').text
                star_age = star_info.find(class_ = 'fw_bold').text

                writer.writerow([star_name,star_age,star_nation,quantity[k],star_info_url])
                k = k + 1
                time.sleep(random.randint(1,5))

            print(f"Page {page}/111 has finished.\n")

"""
        threads =[]
        while len(threads) < 5:
            try:
                thread = threading.Thread(target=down_p, args=(piclist, filename, picfilename))
            finally:
                thread.start()
            threads.append(thread)
            for thread in threads:
                if not thread.is_alive():
                    threads.remove(thread)

def down_p(picklist, filename, picfilename):
    i = 1
    for pic in picklist:
        src = pic.get('src')
        picture = requests.get(src, stream=True)
        with open('{}/{}/{}.jpg'.format(filename,picfilename, i), 'wb') as f:
            f.write(picture.content)
            sleep(random.randint(1, 5))
            i = i + 1
"""
def main():
#    filename = input("Enter file name: ")
#   creat_file(filename)
    url = 'https://baidu.com/models/page/' #+ input("Enter URL: ")
    down_info(url)

if __name__ == '__main__':
    main()