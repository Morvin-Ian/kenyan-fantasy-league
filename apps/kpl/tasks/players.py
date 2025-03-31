from celery import shared_task
import requests
import os
from bs4 import BeautifulSoup
from util.views import headers
from apps.kpl.models import Team, Player
from datetime import datetime


TEAM_URLS = {
    "afc leopards": "AFC_LEOPARDS_URL",
    "bandari mtwara": "BANDARI_URL",
    "bidco united": "BIDCO_UNITED_URL",
    "gor mahia": "GOR_MAHIA_URL",
    "kcb": "KCB_URL",
    "kakamega homeboyz": "KAKAMEGA_HOMEBOYZ_URL",
    "kariobangi sharks": "KARIOBANGI_SHARKS_URL",
    "mara sugar": "MARA_SUGAR_URL",
    "mathare united": "MATHARE_UNITED_URL",
    "murang'a seal fc": "MURANGA_SEAL_URL",
    "nairobi city stars": "NAIROBI_CITY_URL",
    "police": "POLICE_URL",
    "posta rangers": "POSTA_RANGERS_URL",
    "shabana": "SHABANA_URL",
    "sofapaka": "SOFAPAKA_URL",
    "talanta": "TALANTA_URL",
    "tusker": "TUSKER_URL",
    "ulinzi stars": "ULINZI_URL"
}


def get_players(team_name):
    env_var_name = TEAM_URLS.get(team_name.lower()) 
    
    if not env_var_name:
        print(f"Team '{team_name}' not found in mapping.")
        return

    team_url = os.getenv(env_var_name)
    
    if not team_url:
        print(f"URL for team '{team_name}' is not set in environment variables.")
        return

    web_content = requests.get(team_url, headers=headers)
    
    if web_content.status_code == 200:
        soup = BeautifulSoup(web_content.text, 'lxml')
        
        table_body = soup.find_all('tbody')[1]  
        
        players = table_body.find_all('tr', class_=['odd', 'even'])
        playerlist = []

        for player in players:
            name_tag = player.find('td', class_='hauptlink')
            age_tag = player.find_all('td', class_='zentriert')
            position_tag = player.find_all('tr')[-1].find('td')

            if name_tag and age_tag and position_tag:
                name = name_tag.text.strip()
                age = age_tag[1].text.strip() if len(age_tag) > 1 else "N/A"
                position = position_tag.text.strip()

                playerlist.append((name, position, age))

        print(playerlist)
    else:
        print(f"Failed to retrieve the web page. Status code: {web_content.status_code}")

@shared_task
def get_all_players():
    teams = Team.objects.all()
    for team in teams:
        get_players(team.name)