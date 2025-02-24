from celery import shared_task
import requests
from bs4 import BeautifulSoup
from .utils import headers 
from apps.kpl.models import Standing, Team


def extract_table_standings_data(headers) -> str:

    web_content = requests.get('https://footballkenya.org/competitions/fkf-premier-league/standings/', headers=headers, verify=False)

    if web_content.status_code == 200:
        soup = BeautifulSoup(web_content.text, 'lxml')
        kpl_table = soup.find('tbody')
        teams = kpl_table.find_all('tr')

        Standing.objects.all().delete()

        for team in teams:
            rank = team.find('td', class_='data-rank').text
            name = team.find('td', class_='data-name').text
            logo = team.find('img')['src'] if team.find('img') else ''
            played = team.find('td', class_='data-p').text
            wins = team.find('td', class_='data-w').text
            draws = team.find('td', class_='data-d').text
            losses = team.find('td', class_='data-l').text
            goals_for = team.find('td', class_='data-f').text
            goals_against = team.find('td', class_='data-a').text
            goal_differential = team.find('td', class_='data-gd').text
            points = team.find('td', class_='data-pts').text

            team = Team.objects.create(
                name=name,
                logo_url=logo
            )

            Standing.objects.create(
                position=int(rank),
                team=team,
                played=int(played),
                wins=int(wins),
                draws=int(draws),
                losses=int(losses),
                goals_for=int(goals_for),
                goals_against=int(goals_against),
                goal_differential=int(goal_differential),
                points=int(points)
            )

        return "Successfully updated KPL standings"

    else:
        return f"Failed to retrieve the web page. Status code: {web_content.status_code}"


@shared_task
def get_kpl_table():
    response = extract_table_standings_data(headers)
    return response
