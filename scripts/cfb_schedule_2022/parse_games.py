import csv, requests, pandas as pd
from bs4 import BeautifulSoup


class ParseGames:
    def __init__(self):
        # ESPN web links
        self.espn_url = 'https://www.espn.com'
        self.schedule_page_prefix = 'https://www.espn.com/college-football/schedule/_/week/'
        self.schedule_page_suffix = '/year/2022/seasontype/2'
        self.weeks = 15
        self.file_header = ['WEEK_NUM', 'GAME_DATE', 'GAME_TIME_SCORE', 'AWAY_SCHOOL', 'HOME_SCHOOL', 'GAME_LOCATION']
        self.games = pd.DataFrame(columns=self.file_header)
        self.parse_games()

    # Web Scraping Functions
    def get_gamedays(self, soup):
        event_div = soup.find('div', class_='event-schedule__season')
        gameday_container = event_div.find_next()
        gamedays = gameday_container.children
        return gamedays

    def get_games(self, gameday):
        games_container = gameday.find('tbody', class_='Table__TBODY')
        game_rows = games_container.children
        return game_rows

    def set_game_date(self, gameday):
        game_date_td = gameday.find('div', class_='Table__Title')
        game_date = game_date_td.text
        return game_date 

    def set_game_time_score(self, game):
        result_time_td = game.find_all('td')[2]
        anchor_tag = result_time_td.a
        result_time = anchor_tag.text
        return result_time

    def get_team_id(self, link):
        idx1 = link.index('id/')
        start = idx1 + len('id/')
        end = link.rfind('/')
        team_id = link[start:end]
        return team_id

    def set_away_school(self, game):
        away_school_td = game.find_all('td')[0]
        anchor_tag = away_school_td.find_all('a')[1]
        away_school_link = anchor_tag['href']
        away_school_id = self.get_team_id(away_school_link)
        return away_school_id

    def set_home_school(self, game):
        home_school_td = game.find_all('td')[1]
        anchor_tag = home_school_td.find_all('a')[1]
        home_school_link = anchor_tag['href']
        home_school_id = self.get_team_id(home_school_link)
        return home_school_id

    def get_game_url(self, result_time_td):
        links = result_time_td.find(href=True)
        game_link = links['href']
        full_url = self.espn_url + game_link
        return full_url

    def set_location(self, game):
        result_time_td = game.find_all('td')[2]
        game_page_url = self.get_game_url(result_time_td)
        
        rq = requests.get(game_page_url)
        sp = BeautifulSoup(rq.content, 'html.parser')

        game_info = sp.find('section', class_='GameInfo')
        game_location = game_info.find('span', class_='Location__Text')
        location_text = game_location.text.lstrip().rstrip()
        return location_text

    def parse_games(self):
        
        # CSV File Creation
        games_file = open('../../data/cfb_schedule_2022/games.csv', 'w', newline='')
        writer = csv.writer(games_file)
        writer.writerow(self.file_header)

        print('\nGame parsing starting...')

        # Iterate through weeks in schedule
        for week in range(self.weeks):
            
            # Scrape web page of given week in season
            game_week = week + 1
            schedule_page = self.schedule_page_prefix + str(game_week) + self.schedule_page_suffix
            req = requests.get(schedule_page)
            soup = BeautifulSoup(req.content, 'html.parser')

            print(f'Parsing week {game_week} games:')

            # Iterate through gamedays in week
            gamedays = self.get_gamedays(soup)
            for gameday in gamedays:
                game_date = self.set_game_date(gameday)
                game_rows = self.get_games(gameday)
                
                # Iterate through games on a given day
                for game in game_rows:
                    try:
                        game_time_score = self.set_game_time_score(game)
                        away_school = self.set_away_school(game)
                        home_school = self.set_home_school(game)
                        game_location = self.set_location(game)

                        new_game_row = [game_week, game_date, game_time_score, away_school, home_school, game_location]
                        # print(f'Writing game "{new_game_row}" to file')
                        writer.writerow(new_game_row)
                    except:
                        print(f'\nGame {game} information not retrieved...')
                        print(game_time_score)
                        print(away_school)
                        print(home_school)
                        print(game_location)
                        print()

        games_file.close()
        print('Game parsing complete...\n')



# Call function to parse 2022 CFB games
ParseGames()