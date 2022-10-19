import csv, requests, pandas as pd
from bs4 import BeautifulSoup


class ParseSchools:
    def __init__(self):
        self.espn_url = 'https://www.espn.com/'
        self.school_page_prefix = 'college-football/team/_/id/'
        self.file_header = ['SCHOOL_ID', 'SCHOOL_NAME', 'SCHOOL_MASCOT', 'SCHOOL_CONFERENCE']
        self.schools = pd.DataFrame(columns=self.file_header)
        self.conferences = {
            # FBS
            'ACC': '1',
            'American': '151',
            'Big 12': '4',
            'Big Ten': '5',
            'C-USA': '12',
            'FBS Indep.': '18',
            'MAC': '15',
            'Mountain West': '17',
            'Pac-12': '9',
            'SEC': '8',
            'Sun Belt': '37'
            }
        self.parse_schools()
    
    def get_all_schools(self):
        games_csv_path = '../../data/cfb_schedule_2022/games.csv'
        games_df = pd.read_csv(games_csv_path)
        all_home_teams = games_df['HOME_SCHOOL'].unique()
        return all_home_teams

    def get_school_name_mascot(self, page):
        school_full_name_h1 = page.find('h1', class_='ClubhouseHeader__Name')
        school_name_mascot = school_full_name_h1.find_all('span', class_='db')
        return school_name_mascot
    
    def set_school_name(self, page):
        school_name_mascot = self.get_school_name_mascot(page)
        school_name = school_name_mascot[0].text
        return school_name
    
    def set_school_mascot(self, page):
        school_name_mascot = self.get_school_name_mascot(page)
        school_mascot = school_name_mascot[1].text
        return school_mascot
    
    def set_conference(self, page):
        team_standings_section = page.find('section', 'TeamStandings')
        standings_header = team_standings_section.find('h3').text
        conference_name = standings_header.replace('2022 ', '').replace(' Standings', '')
        return conference_name

    def parse_schools(self):
        
        # CSV File Creation
        schools_file = open('../../data/cfb_schedule_2022/schools.csv', 'w')
        writer = csv.writer(schools_file)
        writer.writerow(self.file_header)

        # Iterate through each unique school
        schools = self.get_all_schools()
        for school_id in schools:

            # Scrape web page of given school
            school_page = self.espn_url + self.school_page_prefix + str(school_id)
            req = requests.get(school_page)
            soup = BeautifulSoup(req.content, 'html.parser')

            school_name = self.set_school_name(soup)
            school_mascot = self.set_school_mascot(soup)
            conference = self.set_conference(soup)

            new_school_row = [school_id, school_name, school_mascot, conference]
            writer.writerow(new_school_row)

        schools_file.close()
        print('School parsing complete...\n')
            

# Call function to parse school information
ParseSchools()