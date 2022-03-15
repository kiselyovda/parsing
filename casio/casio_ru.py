import csv
from datetime import datetime
import json
import os
import shutil
import time
from tqdm import tqdm
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent


def get_user_agent_headers() -> dict:
    """
    Get a random user agent from the UserAgent class
    :return: A dictionary with a random user-agent.
    """
    ua = UserAgent()
    return {'user-agent': ua.random}


def get_all_pages() -> int:
    """
    The function gets all pages from casio.ru and saves them to the folder 'data' as separate files
    :return: Count of pages.
    """
    url = 'https://shop.casio.ru/catalog/filter/price-base-from-10448/gender-is-male/apply/'
    headers = get_user_agent_headers()

    r = requests.get(url, headers)

    src = r.text
    soup = BeautifulSoup(src, 'lxml')
    pages_count = int(soup.find('div', class_='bx-pagination-container').find_all('a')[-2].text)

    for count in range(1, pages_count + 1):
        url = f'https://shop.casio.ru/catalog/filter/gender-is-male/apply/?PAGEN_1={count}'
        r = requests.get(url=url, headers=headers)
        with open(f'./data/page_{count}.html', mode='w', encoding='utf-8') as f:
            f.write(r.text)
        time.sleep(0.5)

    return pages_count + 1


def collect_data(pages_count:int, cur_date):
    """
    Collect data from the given number of pages and save it to a csv and json file
    
    :param pages_count: int — the number of pages to scrape
    :type pages_count: int
    """
    with open(f'./data_{cur_date}.csv', mode='w', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(
            (
                'Артикул',
                'Цена',
                'Ссылка'
            )
        )

    data = []
    pbar = tqdm(total=pages_count - 1)
    for page in range(1, pages_count):
        with open(f'./data/page_{page}.html', mode='r', encoding='utf-8') as f:
            src = f.read()

        soup = BeautifulSoup(src, 'lxml')
        items_cards = soup.find_all('a', class_='product-item__link')
        
        for item in items_cards:
            product_article = item.find('p', class_='product-item__articul').text.strip()
            product_price = item.find('p', class_='product-item__price').text.lstrip('руб.')
            product_url = f'https://shop.casio.ru{item.get("href")}'

            data.append(
                {
                    'product_article': product_article,
                    'product_price': product_price,
                    'product_url': product_url
                }
            )

            with open(f'./data_{cur_date}.csv', mode='a', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(
                    (
                        product_article,
                        product_price,
                        product_url
                    )
                )
        pbar.update(1)

    pbar.close()

    with open(f'./data_{cur_date}.json', mode='a', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print('\nFiles are ready!')


def clear_terminal():
    """
    It clears the terminal
    """
    try:
        os.system('cls')
    except:
        os.system('clear')


if __name__ == '__main__':
    clear_terminal()
    cur_date = datetime.now().strftime('%d_%m_%Y')
    json_file_name = f'data_{cur_date}.json'
    os.mkdir('./data') if not os.path.exists('./data') else ...
    os.remove(f'./{json_file_name}') if json_file_name in os.listdir() else ...
    print('Start working...')
    pages_count = get_all_pages()
    clear_terminal()
    collect_data(pages_count, cur_date)
    try:
        shutil.rmtree('./data')
        shutil.rmtree('./__pycache__')
    except:
        print('Some system folders already deleted.')
