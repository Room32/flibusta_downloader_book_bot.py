from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
from bs4 import BeautifulSoup
import zipfile

input_find_book = input('Введите название книги: ')

options = webdriver.FirefoxOptions()
options.set_preference('dom.webdriver.enabled', False)
options.set_preference('dom.webnotifications.enabled', False)
options.headless = True
browser = webdriver.Firefox(options=options)

url = 'https://flibusta.club'
browser.get(url)
time.sleep(0.5)
xpath = '/html/body/div[1]/div[2]/div[1]/div/div[4]/div[1]/div/div/form/input[1]'
browser.find_element(By.XPATH, xpath).send_keys(f'{input_find_book}')
time.sleep(0.5)
browser.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[1]/div/div[4]/div[1]/div/div/form/input[2]').click()
time.sleep(0.5)
current_url = browser.current_url
browser.quit()

headers = {
    "Accept" : "*/*",
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
}

response = requests.get(current_url, headers=headers).text
soup = BeautifulSoup(response, 'lxml')
body = soup.find('h3', text=' Найденные книги:')
all_next = body.find_all_next('li')
del all_next[-11:-1]
book_dict = {}
book_list = []
count = 1

for i in all_next:
    url_book = i.find_next('a').get('href')
    name = i.find_next('a').text
    book_dict[f'{count}. '+name] = url+url_book
    count += 1
    book_list.append(url+url_book)

for key, value in book_dict.items():
    print(f'{key}')

number_of_book = int(input('Выберите номер нужной книги: '))

download_page = '/download/?format=fb2.zip'
response_download_page = requests.get(book_list[number_of_book-1]+download_page, headers=headers).text
soup_download_page = BeautifulSoup(response_download_page, 'lxml')
download_link_block = soup_download_page.find('div', class_='p_load_progress_txt')
# print(download_link_block)
download_link = download_link_block.find_next('a').get('href')
# print(download_link)
if download_link[0] == '/':
    download_book = requests.get(url+download_link, headers=headers).content
else:
    download_book = requests.get(download_link, headers=headers).content

with open('content/book.zip', 'wb') as f:
    f.write(download_book)

with zipfile.ZipFile('content/book.zip', 'r') as zip_book:
    zip_book.extractall('content/')