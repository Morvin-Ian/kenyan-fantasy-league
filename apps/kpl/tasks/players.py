import logging
import logging.config
import os
import re

import requests
from bs4 import BeautifulSoup
from celery import shared_task
from django.db.models import Q

from apps.kpl.models import Player, Team
from config.settings import base
from util.views import headers

logging.config.dictConfig(base.DEFAULT_LOGGING)
logger = logging.getLogger(__name__)

TEAM_URLS = {
    "afc leopards": "AFC_LEOPARDS_URL",
    "bandari mtwara": "BANDARI_URL",
    "gor mahia": "GOR_MAHIA_URL",
    "kcb": "KCB_URL",
    "kakamega homeboyz": "KAKAMEGA_HOMEBOYZ_URL",
    "kariobangi sharks": "KARIOBANGI_SHARKS_URL",
    "mara sugar": "MARA_SUGAR_URL",
    "mathare united": "MATHARE_UNITED_URL",
    "murang'a seal fc": "MURANGA_SEAL_URL",
    "police": "POLICE_URL",
    "posta rangers": "POSTA_RANGERS_URL",
    "shabana": "SHABANA_URL",
    "sofapaka": "SOFAPAKA_URL",
    "talanta": "TALANTA_URL",
    "tusker": "TUSKER_URL",
    "ulinzi stars": "ULINZI_URL",
    "nairobi united": "NAIROBI_UNITED_URL",
}


def get_position_from_string(position_string):
    position_string = position_string.lower()

    if "goalkeeper" in position_string or "gk" in position_string:
        return "GKP"

    if (
        "defender" in position_string
        or "back" in position_string
        or "centre-back" in position_string
        or "fullback" in position_string
    ):
        return "DEF"

    if (
        "forward" in position_string
        or "striker" in position_string
        or "winger" in position_string
        or "centre-forward" in position_string
    ):
        return "FWD"

    if "midfield" in position_string or "mid" in position_string:
        return "MID"

    return None


def get_players(team_name):
    env_var_name = TEAM_URLS.get(team_name.lower())
    logger.error(f"Fetching players for team: {team_name}")
    if not env_var_name:
        logger.info(f"Team '{team_name}' not found in mapping.")
        return False

    team_url = os.getenv(env_var_name)

    logger.info(f"Fetching players for team: {team_name} from URL: {team_url}")
    if not team_url:
        logger.info(f"URL for team '{team_name}' is not set in environment variables.")
        return False

    web_content = requests.get(team_url, headers=headers)

    if web_content.status_code == 200:
        soup = BeautifulSoup(web_content.text, "lxml")
        table_body = soup.find_all("tbody")[1]
        players = table_body.find_all("tr", class_=["odd", "even"])

        team = Team.objects.filter(name=team_name).first()
        if not team:
            logger.info(f"Team '{team_name}' not found in the database.")
            return False

        for player in players:
            name_tag = player.find("td", class_="hauptlink")
            age_tag = player.find_all("td", class_="zentriert")
            position_tag = player.find_all("tr")[-1].find("td")

            if name_tag and age_tag and position_tag:
                name = name_tag.text.strip()
                age = age_tag[1].text.strip()
                position = position_tag.text.strip()

                if age in ["-", "(-)", "- (-)"]:
                    age_value = None
                else:
                    match = re.search(r"\((\d+)\)", age)
                    age_value = match.group(1) if match else age

                position_code = get_position_from_string(position)
                if not position_code:
                    position_code = "MID"

                player_obj, created = Player.objects.update_or_create(
                    name=name,
                    team=team,
                    defaults={"position": position_code, "age": age_value},
                )

                if created:
                    logger.info(f"Created new player: {name} ({team_name})")
                else:
                    logger.info(f"Updated player: {name} ({team_name})")

        valid_teams = Team.objects.filter(is_relegated=False).values_list(
            "pkid", flat=True
        )
        removed_count, _ = Player.objects.filter(~Q(team_id__in=valid_teams)).delete()
        if removed_count:
            logger.info(
                f"Deleted {removed_count} players not linked to any existing team."
            )
        return True

    else:
        logger.error(
            f"Failed to retrieve the web page. Status code: {web_content.status_code}"
        )


@shared_task
def get_all_players():
    teams = Team.objects.all()
    results = {}

    for team in teams:
        success = get_players(team.name)
        results[team.name] = success

    return results
