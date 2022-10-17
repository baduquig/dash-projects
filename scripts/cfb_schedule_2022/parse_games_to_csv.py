import csv, requests, pandas as pd
from bs4 import BeautifulSoup

# ESPN web links https://www.espn.com/college-football/game?gameId=401426532
espn_url = 'https://www.espn.com'
schedule_page_prefix = 'https://www.espn.com/college-football/schedule/_/week/'
schedule_page_suffix = '/year/2022/seasontype/2'

weeks = 1#15
games = pd.DataFrame(columns=['WEEK_NUM', 'GAME_DATE', 'GAME_TIME_SCORE', 'AWAY_SCHOOL', 
                            'AWAY_MASCOT', 'AWAY_CONFERENCE', 'HOME_SCHOOL', 'HOME_MASCOT', 
                            'HOME_CONFERENCE', 'GAME_LOCATION', 'LATITUDE', 'LONGITUDE'])

# Web Scraping Functions
def get_gamedays(soup):
    event_div = soup.find('div', class_='event-schedule__season')
    gameday_container = event_div.find_next()
    gamedays = gameday_container.children
    return gamedays

def get_games(gameday):
    games_container = gameday.find('tbody', class_='Table__TBODY')
    game_rows = games_container.children
    return game_rows

def set_game_date(gameday):
    game_date_td = gameday.find('div', class_='Table__Title')
    game_date = game_date_td.text
    return game_date 

def set_game_time_score(game):
    result_time_td = game.find_all('td')[2]
    anchor_tag = result_time_td.a
    result_time = anchor_tag.text
    return result_time

def get_team_id(link):
    idx1 = link.index('id/')
    start = idx1 + len('id/')
    end = link.rfind('/')
    team_id = link[start:end]
    return team_id

def set_away_school(game):
    away_school_td = game.find_all('td')[0]
    anchor_tag = away_school_td.find_all('a')[1]
    away_school_link = anchor_tag['href']
    away_school_id = get_team_id(away_school_link)
    return away_school_id

def set_home_school(game):
    home_school_td = game.find_all('td')[1]
    anchor_tag = home_school_td.find_all('a')[1]
    home_school_link = anchor_tag['href']
    home_school_id = get_team_id(home_school_link)
    return home_school_id

def get_game_url(result_time_td):
    links = result_time_td.find(href=True)
    game_link = links['href']
    full_url = espn_url + game_link
    return full_url

def set_location(game):
    result_time_td = game.find_all('td')[2]
    game_page_url = get_game_url(result_time_td)
    
    rq = requests.get(game_page_url)
    sp = BeautifulSoup(rq.content, 'html.parser')

    game_info = sp.find('div', id='gamepackage-game-information')
    location_details = game_info.find('div', class_='location-details')
    game_location = location_details.find('div', class_='game-location')
    location_text = game_location.text.lstrip().rstrip()
    return location_text

def parse_games(season_len, url_prefix, url_suffix):

    #games_file = open('../../data/cfb_schedule_2022/games.csv', 'w')

    # Iterate through weeks in schedule
    for week in range(season_len):
        game_week = week + 1
        schedule_page = f'{url_prefix}{game_week}{url_suffix}'        
        req = requests.get(schedule_page)
        soup = BeautifulSoup(req.content, 'html.parser')

        # Iterate through gamedays in week
        gamedays = get_gamedays(soup)
        for gameday in gamedays:
            game_date = set_game_date(gameday)
            game_rows = get_games(gameday)
            
            # Iterate through games on a given day
            for game in game_rows:
                game_time_score = set_game_time_score(game)
                away_school = set_away_school(game)
                home_school = set_home_school(game)
                game_location = set_location(game)

                new_game_record = {
                    'WEEK_NUM': game_week,
                    'GAME_DATE': game_date,
                    'GAME_TIME_SCORE': game_time_score,
                    'AWAY_SCHOOL': away_school,
                    # 'AWAY_MASCOT':
                    # 'AWAY_CONFERENCE':
                    'HOME_SCHOOL': home_school,
                    # 'HOME_MASCOT':
                    # 'HOME_CONFERENCE':
                    'GAME_LOCATION': game_location
                    # 'LATITUDE':
                    # 'LONGITUDE':
                }
                print(new_game_record)



# Call function to parse 2022 CFB games
parse_games(weeks, schedule_page_prefix, schedule_page_suffix)