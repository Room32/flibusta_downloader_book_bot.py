from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
from bs4 import BeautifulSoup
import zipfile
import telebot

token = '''TOKEN'''
bot = telebot.TeleBot(token)

url = 'https://flibusta.club'
book_dict = {}
book_list = []

headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
}


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет. Введи название книги, которую ищешь")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    print(message.text)
    try:
        book_dict.clear()
        book_list.clear()

        options = webdriver.FirefoxOptions()
        options.set_preference('dom.webdriver.enabled', False)
        options.set_preference('dom.webnotifications.enabled', False)
        options.headless = True
        browser = webdriver.Firefox(options=options)

        browser.get(url)
        time.sleep(0.5)
        xpath = '/html/body/div[1]/div[2]/div[1]/div/div[4]/div[1]/div/div/form/input[1]'
        browser.find_element(By.XPATH, xpath).send_keys(f'{message.text}')
        time.sleep(0.5)
        browser.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[1]/div/div[4]/div[1]/div/div/form/input[2]').click()
        time.sleep(0.5)
        current_url = browser.current_url
        browser.quit()

        response = requests.get(current_url, headers=headers).text
        soup = BeautifulSoup(response, 'lxml')
        body = soup.find('h3', text=' Найденные книги:')
        all_next = body.find_all_next('li')
        del all_next[-11:-1]
        count = 1

        for i in all_next:
            url_book = i.find_next('a').get('href')
            name = i.find_next('a').text
            pre_author = i.find_all_next('a')
            author = pre_author[1].text
            if name == 'Фильтр-список':
                break
            else:
                book_dict[f'{count}. {name} - {author}'] = url+url_book
                count += 1
                book_list.append(url+url_book)

        for key, value in book_dict.items():
            # print(f'{key}')
            bot.send_message(chat_id=message.from_user.id, text=key)

        bot.send_message(chat_id=message.from_user.id, text='-'*53+'\nВведите номер нужной книги: \n'+'-'*53)
        bot.register_next_step_handler(message, choise_book)

    except Exception as ex:
        print(f'Произошла ошибка в блоке handle_message: {ex}')
        bot.send_message(chat_id=message.from_user.id, text=f'Произошла ошибка: {ex}\nНажмите /start')


def choise_book(message):
    try:
        mes = message.text
        if mes.isdigit() == True:
            download_page = '/download/?format=fb2.zip'
            book_number = int(message.text)
            response_download_page = requests.get(book_list[book_number - 1] + download_page, headers=headers).text
            soup_download_page = BeautifulSoup(response_download_page, 'lxml')
            download_link_block = soup_download_page.find('div', class_='p_load_progress_txt')
            # print(download_link_block)
            download_link = download_link_block.find_next('a').get('href')
            # print(download_link)
            if download_link[0] == '/':
                download_book = requests.get(url+download_link, headers=headers).content
            else:
                download_book = requests.get(download_link, headers=headers).content

            time.sleep(2)
            with open('content/book.zip', 'wb') as f:
                f.write(download_book)

            archive = 'content/book.zip'
            zip_file = zipfile.ZipFile(archive)
            a = [text_file.filename for text_file in zip_file.infolist()]
            title = a[0]

            with zipfile.ZipFile('content/book.zip', 'r') as zip_book:
                zip_book.extractall('content/')

            file = open(f'content/{title}', 'rb')
            bot.send_document(chat_id=message.from_user.id, document=file)
            bot.send_message(chat_id=message.from_user.id, text='Теперь нажми /start')
        else:
            bot.send_message(chat_id=message.from_user.id, text='Нужно ввести номер книги, которую хочешь скачать. '
                                                                'Нажми /start и попробуй заново')
    except Exception as ex:
        print(f'Произошла ошибка в блоке choise_book: {ex}')
        bot.send_message(chat_id=message.from_user.id, text=f'Произошла ошибка: {ex}\nНажмите /start')

bot.infinity_polling(skip_pending=True)