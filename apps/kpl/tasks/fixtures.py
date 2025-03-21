from celery import shared_task
import requests
from bs4 import BeautifulSoup
from util.views import headers 
from apps.kpl.models import Standing, Team


def extract_fixtures_data(headers) -> str:

    web_content = requests.get('https://footballkenya.org/competitions/fkf-premier-league/fixtures/', headers=headers, verify=False)

    if web_content.status_code == 200:
        soup = BeautifulSoup(web_content.text, 'lxml')
        print(soup)

        return "Successfully updated KPL standings"

    else:
        return f"Failed to retrieve the web page. Status code: {web_content.status_code}"


@shared_task
def get_kpl_fixtures():
    response = extract_fixtures_data(headers)
    return response
