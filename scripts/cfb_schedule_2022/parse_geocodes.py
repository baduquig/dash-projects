import csv, pandas as pd
import requests


class ParseGeocodes:
    def __init__(self):
        self.geocode_url_prefix = 'https://geocode.maps.co/search?'
        self.file_header = ['LOCATION', 'LATITUDE', 'LONGITUDE']
        self.us_states = {
            'AK': 'Alaska', 'AL': 'Alabama', 'AR': 'Arkansas',
            'AS': 'American Samoa', 'AZ': 'Arizona', 'CA': 'California',
            'CO': 'Colorado', 'CT': 'Connecticut', 'DC': 'District of Columbia',
            'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
            'GU': 'Guam', 'HI': 'Hawaii', 'IA': 'Iowa', 'ID': 'Idaho', 
            'IL': 'Illinois', 'IN': 'Indiana', 'KS': 'Kansas', 
            'KY': 'Kentucky', 'LA': 'Louisiana', 'MA': 'Massachusetts', 
            'MD': 'Maryland', 'ME': 'Maine', 'MI': 'Michigan', 
            'MN': 'Minnesota', 'MO': 'Missouri', 
            'MP': 'Northern Mariana Islands', 'MS': 'Mississippi',
            'MT': 'Montana', 'NA': 'National', 'NC': 'North Carolina',
            'ND': 'North Dakota', 'NE': 'Nebraska', 'NH': 'New Hampshire',
            'NJ': 'New Jersey', 'NM': 'New Mexico', 'NV': 'Nevada',
            'NY': 'New York', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 
            'PA': 'Pennsylvania', 'PR': 'Puerto Rico', 'RI': 'Rhode Island', 
            'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 
            'TX': 'Texas', 'UT': 'Utah', 'VA': 'Virginia', 'VI': 'Virgin Islands', 
            'VT': 'Vermont', 'WA': 'Washington', 'WI': 'Wisconsin', 
            'WV': 'West Virginia', 'WY': 'Wyoming'
        }
        self.parse_geocodes()
    
    def get_all_locations(self):
        games_csv_path = '../../data/cfb_schedule_2022/games.csv'
        games_df = pd.read_csv(games_csv_path)
        all_locations = games_df['GAME_LOCATION'].unique()
        return all_locations

    def parse_geocodes(self):

        # CSV File Creation
        locations_file = open('../../data/cfb_schedule_2022/locations.csv', 'w', newline='')
        writer = csv.writer(locations_file)
        writer.writerow(self.file_header)

        print('\nGeocodes parsing starting...')

        # Iterate through all game locations
        locations = self.get_all_locations()
        for location in locations:

            # API call for Forward Geocode of given location
            forward_geocode = self.geocode_url_prefix + 'q={' + location + '}'
            req = requests.get(forward_geocode)
            location_data = req.json()[0]            
            country = location_data['display_name'].split(', ')[-1]

            if country == 'United States':
                latitude = location_data['lat']
                longitude = location_data['lon']
                new_location_row = [location, latitude, longitude]
                writer.writerow(new_location_row)

        locations_file.close()
        print('Geocodes parsing complete...\n')



# Call Forward Geocoding function
ParseGeocodes()