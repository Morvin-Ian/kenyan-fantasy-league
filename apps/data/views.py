import requests
from bs4 import BeautifulSoup


def scrape():
    URL = "https://footballkenya.org/competitions/fkf-premier-league/fixtures/"
    r = requests.get(URL)
    print(r.content)

if __name__ == '__main__':
    scrape()
