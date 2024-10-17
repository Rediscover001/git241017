from time import sleep
import re

import bs4
import requests
import os
import random
import threading

def creat_file(name):
    if not os.path.exists(name):
        os.mkdir(name)
    else:
        print('The fild named {} already exists'.format(name))

def request_content(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0"}
    response = requests.get(url, headers=headers)
    return response.text

def down_pic(url, filename):
    presoup = bs4.BeautifulSoup(request_content(url), 'html.parser')
    pagelist = presoup.find_all('a', class_='td-image-wrap')
    for page in pagelist:
        href = page.get('href')
        prepicfilename = page.get('title')
        pattern = '\|'  # 替换title非法字符
        picfilename = re.sub(pattern, '', prepicfilename)
        creat_file('{}/{}'.format(filename, picfilename))
        soup = bs4.BeautifulSoup(request_content(href), 'html.parser')
        piclist = soup.find_all('img')

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

def main():
    filename = input("Enter file name: ")
    creat_file(filename)
    url = 'https://spacemiss.com/' #+ input("Enter URL: ")
    down_pic(url, filename)

if __name__ == '__main__':
    main()