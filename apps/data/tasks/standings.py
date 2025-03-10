import requests
import os

from bs4 import BeautifulSoup
from celery import shared_task

from .utils import headers 
from apps.kpl.models import Standing, Team


def extract_table_standings_data(headers) -> str:
    url = os.getenv('TABLE_STANDINGS_URL')  
    web_content = requests.get(url, headers=headers)

    if web_content.status_code == 200:
        soup = BeautifulSoup(web_content.text, 'lxml')
        tables = soup.find_all('tbody', class_='Table__TBODY')

        if tables and len(tables) > 1:
            first_table = tables[0].find_all("tr")  
            second_table = tables[1].find_all("tr")  

            Team.objects.all().delete()

            team_stats = []
            for row in second_table:
                data_rows = row.find_all('td')
                if len(data_rows) >= 8: 
                    team_stats.append([
                        data_rows[0].text.strip(),  # Played
                        data_rows[1].text.strip(),  # Won
                        data_rows[2].text.strip(),  # Drawn
                        data_rows[3].text.strip(),  # Lost
                        data_rows[4].text.strip(),  # Goals For
                        data_rows[5].text.strip(),  # Goals Against
                        data_rows[6].text.strip(),  # Goal Difference
                        data_rows[7].text.strip()   # Points
                    ])

            for idx, row in enumerate(first_table):
                position = row.find('span', class_='team-position').text if row.find('span', class_='team-position') else 'N/A'
                team_name = row.find('abbr')['title'] if row.find('abbr') else 'N/A'
                logo = row.find('img')['src'] if row.find('img') else 'N/A'

                team = Team.objects.create(
                    name=team_name,
                    logo_url=logo
                )

                if idx < len(team_stats):
                    stats = team_stats[idx]
                    Standing.objects.create(
                        position=int(position),
                        team=team,
                        played=int(stats[0]),
                        wins=int(stats[1]),
                        draws=int(stats[2]),
                        losses=int(stats[3]),
                        goals_for=int(stats[4]),
                        goals_against=int(stats[5]),
                        goal_differential=int(stats[6]),
                        points=int(stats[7]),
                        period="2024-2025"
                    )

            return "Successfully updated the table standings."

        else:
            return "Table not found"
    
    return f"Failed to retrieve the web page. Status code: {web_content.status_code}"
def edit_team_logo(headers) -> str:
    url = os.getenv('TEAM_LOGOS_URL')  
    web_content = requests.get(url, headers=headers, verify=False)

    if web_content.status_code == 200:
        soup = BeautifulSoup(web_content.text, 'lxml')
        table = soup.find('tbody')

        if not table:
            return "Table not found on the page."

        teams = table.find_all('tr')

        updated_count = 0
        for team in teams:
            full_name = team.find('td', class_='data-name').text.strip()
            logo = team.find('img')['src'] if team.find('img') else ''

            if full_name:
                first_word = full_name.split()[0]  
                if full_name.startswith('FC') or full_name.startswith('Kenya'):
                    first_word = full_name.split()[1]
                team_obj = Team.objects.filter(name__istartswith=first_word).first()

                if team_obj and logo:
                    team_obj.logo_url = logo
                    team_obj.save()
                    updated_count += 1

        return f"Successfully updated {updated_count} team logos."

    return f"Failed to retrieve the web page. Status code: {web_content.status_code}"


@shared_task
def get_kpl_table():
    try:
        first_response = extract_table_standings_data(headers)
    except Exception as e:
        first_response = f"Error in extracting standings: {str(e)}"
    
    try:
        second_response = edit_team_logo(headers)
    except Exception as e:
        second_response = f"Error in editing team logos: {str(e)}"
    
    return f"{first_response} - {second_response}"
