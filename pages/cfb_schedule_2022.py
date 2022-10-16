import dash, datetime, plotly.graph_objects as go, requests, pandas as pd
from bs4 import BeautifulSoup
from dash import callback, html, dcc, Input, Output


"""dash.register_page(
    __name__,
    path='/cfb-schedule-2022',
    title='2022 College Football Schedule',
    name='2022 College Football Schedule'
)"""


# ESPN web links
schedule_page_prefix = 'https://www.espn.com/college-football/schedule/_/week/'
schedule_page_suffix = '/year/2022/seasontype/2'

weeks = 1#5
df = pd.DataFrame(columns=['WEEK_NUM', 'GAME_DATE', 'GAME_TIME', 'AWAY_SCHOOL', 
                            'AWAY_MASCOT', 'AWAY_CONFERENCE', 'HOME_SCHOOL', 'HOME_MASCOT', 
                            'HOME_CONFERENCE', 'GAME_LOCATION', 'LATITUDE', 'LONGITUDE'])

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
    game_date = gameday.find('div', class_='Table__Title')
    return game_date



def parse_games(season_len, url_prefix, url_suffix):

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
                new_record = {
                    'WEEK_NUM': game_week,
                    'GAME_DATE': game_date
                    # 'GAME_TIME':
                    # 'AWAY_SCHOOL':
                    # 'AWAY_MASCOT':
                    # 'AWAY_CONFERENCE':
                    # 'HOME_SCHOOL':
                    # 'HOME_MASCOT':
                    # 'HOME_CONFERENCE':
                    # 'GAME_LOCATION':
                    # 'LATITUDE':
                    # 'LONGITUDE':
                }
                

        

parse_games(weeks, schedule_page_prefix, schedule_page_suffix)
"""
# TODO:
# - Scrape schedule data from ESPN
# - Write data to csv file
# - Read csv to pandas data frame

# Instantiate initial dropdown values
weeks = df['WEEK_NUM'].unique()
conferences = df['HOME_CONFERENCE'].unique()

# Get current week
today = datetime.datetime.now()
first_week = datetime.datetime(2022, 9, 5)
default_week = 1
while today >= first_week:
    first_week += first_week + datetime.timedelta(days=7)
    default_week += 1

# Filter schedule
def filter_df(selected_week, selected_conferences, selected_days, selected_teams):
    games = df
    games = games`[games['WEEK_NUM'] == selected_week]

    # only week chosen
    if((selected_conferences is None or selected_conferences == [])
    and (selected_days is None or selected_days == [])
    and (selected_teams is None or selected_teams == [])):
        pass
    # only week and day chosen
    elif ((selected_conferences is None or selected_conferences == [])
    and (selected_teams is None or selected_teams == [])):
        games = games[games['GAME_DAY'].isin(selected_days)]
    # only week and conference chosen
    elif ((selected_days is None or selected_days == [])
    and (selected_teams is None or selected_teams == [])):
        games = games[games['AWAY_CONFERENCE'].isin(selected_conferences) | games['HOME_CONFERENCE'].isin(selected_conferences)]
    # only team blank
    elif (selected_teams is None or selected_teams == []):
        games = games[games['GAME_DAY'].isin(selected_days)]
        games = games[games['AWAY_CONFERENCE'].isin(selected_conferences) | games['HOME_CONFERENCE'].isin(selected_conferences)]
    # only day blank
    elif (selected_days is None or selected_days == []):
        games = games[games['AWAY_CONFERENCE'].isin(selected_conferences) | games['HOME_CONFERENCE'].isin(selected_conferences)]
        games = games[games['AWAY_SCHOOL'].isin(selected_teams) | games['HOME_SCHOOL'].isin(selected_teams)]
    else:
        games = games[games['GAME_DAY'].isin(selected_days)]
        games = games[games['AWAY_CONFERENCE'].isin(selected_conferences) | games['HOME_CONFERENCE'].isin(selected_conferences)]
        games = games[games['AWAY_SCHOOL'].isin(selected_teams) | games['HOME_SCHOOL'].isin(selected_teams)]
    
    return games


layout = html.Div(
    className='app-container',
    children=[

        # Header
        html.H1('College football schedule 2022'),

        # Inputs
        html.Div(
            className='inputs-div',
            children=[

                # Left DIVs
                html.Div(
                    className='time-entries',
                    children=[
                        # Week
                        html.Div(
                            className='week-div',
                            children=[
                                html.Label('Week'),
                                dcc.Dropdown(
                                    weeks,
                                    value=default_week,
                                    id='week'
                                )
                            ]
                        ),# end 'week-div' div

                        # Day
                        html.Div(
                            className='day-div',
                            children=[
                                html.Label('Day'),
                                dcc.Dropdown(
                                    id='day',
                                    multi=True
                                )
                            ]
                        )# end 'day-div' div
                    ]
                ), # end Left DIVs

                # Right DIVs
                html.Div(
                    className='school-entries',
                    children=[
                        # Conference
                        html.Div(
                            className='conf-div',
                            children=[
                                html.Label('Conference'),
                                dcc.Dropdown(
                                    conferences,
                                    id='conf',
                                    multi=True
                                )
                            ]
                        ),# end 'conf-div' div

                        # Day
                        html.Div(
                            className='team-div',
                            children=[
                                html.Label('Team'),
                                dcc.Dropdown(
                                    id='team',
                                    multi=True
                                )
                            ]
                        )# end 'team-div' div
                    ]
                ) # end Right DIVs

            ]
        ),

        # Map
        dcc.Graph(id='map'),

        # Games grid table
        html.Div(id='grid')

    ]# end 'app-container' div
)# end app.layout


#~~~ Callbacks ~~~#

# Game dates dropdown list
@callback(
    Output('day', 'options'),
    Input('week', 'value')
)
def set_gamedate_options(selected_week):
    weeks = df[df['WEEK_NUM'] == selected_week]
    dates = weeks['GAME_DAY'].unique()
    return dates


# Teams dropdown list
@callback(
    Output('team', 'options'),
    Input('conf', 'value'),
    prevent_initial_call=True
)
def set_gamedate_options(selected_conferences):
    conferences = df[df['HOME_CONFERENCE'].isin(selected_conferences)]
    teams = conferences['HOME_SCHOOL'].unique()
    return teams


# Render map
@callback(
    Output('map', 'figure'),
    Input('week', 'value'),
    Input('conf', 'value'),
    Input('day', 'value'),
    Input('team', 'value')
)
def plot_games(selected_week, selected_conferences, selected_days, selected_teams):
    games = filter_df(selected_week, selected_conferences, selected_days, selected_teams)
    
    game_info = games['AWAY_SCHOOL'] + ' at ' + games['HOME_SCHOOL'] + ' | ' + games['GAME_TIME'] + ', ' + games['GAME_LOCATION']
    
    fig = go.Figure(data=go.Scattergeo(
        locationmode='USA-states',
        lat=games['LATITUDE'],
        lon=games['LONGITUDE'],
        marker = {'color': 'black'},
        text=game_info
    ))
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        geo = dict(
            scope='usa'
        )
    )
    return fig


# Render grid
@callback(
    Output('grid', 'children'),
    Input('week', 'value'),
    Input('conf', 'value'),
    Input('day', 'value'),
    Input('team', 'value')
)
def generate_grid(selected_week, selected_conferences, selected_days, selected_teams):
    games = filter_df(selected_week, selected_conferences, selected_days, selected_teams)

    games.sort_values(by=['GAME_DAY', 'GAME_TIME'], inplace=True)
    games['AWAY'] = games['AWAY_SCHOOL'] + ' ' + games['AWAY_MASCOT']
    games['HOME'] = games['HOME_SCHOOL'] + ' ' + games['HOME_MASCOT']

    games = games.drop(['WEEK_NUM', 'AWAY_SCHOOL', 'AWAY_MASCOT', 'AWAY_CONFERENCE', 'HOME_SCHOOL', 
                        'HOME_MASCOT', 'HOME_CONFERENCE', 'LATITUDE', 'LONGITUDE'], axis=1)

    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in games.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(games.iloc[i][col]) for col in games.columns
            ]) for i in range(len(games))
        ])
    ])


#~~~ Callbacks ~~~#
"""