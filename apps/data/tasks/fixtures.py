from celery import shared_task
import requests
from bs4 import BeautifulSoup
import random
import csv

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
]

HEADERS = {'User-Agent': random.choice(USER_AGENTS)}

URL = "https://thenextweb.com/future-of-work"

CSV_FILE = 'articles.csv'


def extract_data(headers:dict) -> str:
    web_content = requests.get('https://thenextweb.com/future-of-work', headers=headers)

    if web_content.status_code == 200:
        soup = BeautifulSoup(web_content.text, 'lxml')
        articles = soup.find_all('article', class_='c-listArticle')

        with open("tnx_articles.csv", 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Title', 'Image Link', 'Published Date', 'More Information'])

            for index, article in enumerate(articles):
                article_title = article.find('a', class_='title_link').text.strip()
                article_image_link = article.find('img')['data-src']
                published_date = article.find_all('li', class_='c-meta__item')[-1].text.strip()
                more_information = "https://thenextweb.com" + article.find('a', class_='title_link')['href']

                writer.writerow([article_title, article_image_link, published_date, more_information])

        return ("Data saved to articles.csv")
    else:
        return (f"Failed to retrieve the page. Status code: {web_content.status_code}")

@shared_task
def my_task(arg1, arg2):
    result = arg1 + arg2
    response = extract_data(HEADERS)
    return f"{response}: {result}"
