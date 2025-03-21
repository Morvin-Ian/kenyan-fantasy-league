from celery import shared_task
import requests
import os
from bs4 import BeautifulSoup
from util.views import headers
from apps.kpl.models import Team, Fixture
from datetime import datetime


def find_team(team_name: str) -> Team|None:
        words = team_name.split()
        words_sorted_by_length = sorted(words, key=len, reverse=True)
        
        for word in words_sorted_by_length:
            team = Team.objects.filter(name__icontains=word).first()
            if team:
                return team
        return None

def extract_fixtures_data(headers) -> str:
    url = os.getenv('TEAM_FIXTURES_URL')
    
    web_content = requests.get(url, headers=headers, verify=False)
    
    if web_content.status_code == 200:
        soup = BeautifulSoup(web_content.text, 'lxml')
        table = soup.find('table', class_="sp-event-blocks")
        table_rows = table.find_all('tr')[1:]
        
        fixtures_created = 0
        fixtures_updated = 0
        
        for row in table_rows:
            table_data = row.find('td')
            links = table_data.find_all('a')
            date = links[0].text
            time = links[1].text
            
            match_datetime_str = f"{date} {time}"
            try:
                match_datetime = datetime.strptime(match_datetime_str, '%B %d, %Y %H:%M')
            except ValueError:
                try:
                    match_datetime = datetime.strptime(match_datetime_str, '%b %d, %Y %H:%M')
                except ValueError:
                    continue
                    
            home_team_name = links[2].text.split('vs')[0].strip()
            away_team_name = links[2].text.split('vs')[1].strip()
            venue = table_data.find('div', class_='sp-event-venue').text       
    
            home_team = find_team(home_team_name)
            away_team = find_team(away_team_name)
            
            if not home_team or not away_team:
                print(f"Skipping fixture: No team found for home='{home_team_name}' or away='{away_team_name}'")
                continue
                
            fixture, created = Fixture.objects.update_or_create(
                home_team=home_team,
                away_team=away_team,
                match_date=match_datetime,
                defaults={
                    'venue': venue,
                    'status': 'upcoming' 
                }
            )
            
            if created:
                fixtures_created += 1
            else:
                fixtures_updated += 1
                
        return f"Successfully updated KPL fixtures. Created: {fixtures_created}, Updated: {fixtures_updated}"
    else:
        return f"Failed to retrieve the web page. Status code: {web_content.status_code}"
    

@shared_task
def get_kpl_fixtures():
    response = extract_fixtures_data(headers)
    return response