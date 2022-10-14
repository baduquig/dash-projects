import dash
import plotly.express as px
import pandas as pd
from dash import callback, html, dcc, Input, Output


dash.register_page(
    __name__,
    path='/home-value-index-analysis',
    title='Zillow Home Value Index Analysis',
    name='Zillow Home Value Index Analysis'
)


_3bed = pd.read_csv('./data/home_value_index_analysis/3bed.csv')
_4bed = pd.read_csv('./data/home_value_index_analysis/4bed.csv')
rent = pd.read_csv('./data/home_value_index_analysis/rent.csv')

_3bed['Country'] = 'United States'
_4bed['Country'] = 'United States'
rent['Country'] = 'United States'

state_dropdown_values = _3bed['State'].unique()


def get_df(selected_data_source):
    if selected_data_source == '3bed':
        df = _3bed
        #chart_title = 'Typical home value of 3 bedroom houses'
    elif selected_data_source == '4bed':
        df = _4bed
        #chart_title = 'Typical home value of 4 bedroom houses'
    else:
        df = rent
        #chart_title = 'Typical rental rates'
    return df


layout = html.Div(
    className='parent-div', 
    children=[
        html.H1('Zillow Home Value Index API Analysis'),

        html.Div(
            className='source-div',
            children=[
                dcc.RadioItems(
                    options=[
                        {'label': '3-Bedroom Home Values', 'value': '3bed'},
                        {'label': '4-Bedroom Home Values', 'value': '4bed'},
                        {'label': 'Rental Rates', 'value': 'rent'}
                    ],
                    value='3bed',
                    id='data'
                )
            ]
        ),

        html.Div(
            className='inputs-div',
            
            children=[

                html.Div(
                    className='state-div',
                    children=[
                        html.Label('State'),
                        dcc.Dropdown(
                            state_dropdown_values,
                            id='state',
                            multi=True
                        )
                    ]
                ),

                html.Div(
                    className='city-div',
                    children=[
                        html.Label('City'),
                        dcc.Dropdown(
                            id='city',
                            multi=True
                        )
                    ]
                ),

                html.Div(
                    className='zipcode-div',
                    children=[
                        html.Label('Zipcode'),
                        dcc.Dropdown(
                            id='zipcode',
                            multi=True
                        )
                    ]
                )

            ]
        ),

        dcc.Graph(
            id='hpi-line-graph',
            style={'border-radius': '50px'}
        ),

        html.Div(
            className='disclaimer-div',
            children=[
                html.P('Data available at and retrieved from '),
                html.A('Zillow Research', href='https://www.zillow.com/research/data/')
            ]
        )
        
    ] #end parent-div children
)
#~~~ End layout ~~~#


#~~~ Callbacks ~~~#
@callback(
    Output('city', 'options'),
    Input('data', 'value'),
    Input('state', 'value'),
    prevent_initial_call=True
)
def set_city_options(selected_data_source, selected_states):
    if (selected_states == [] or selected_states is None):
        cities = []        
    else:
        df = get_df(selected_data_source)
        cities = df[df['State'].isin(list(selected_states))]
        cities = cities['City'].unique()
    return cities


@callback(
    Output('zipcode', 'options'),
    Input('data', 'value'),
    Input('state', 'value'),
    Input('city', 'value'),
    prevent_initial_call=True
)
def set_zip_options(selected_data_source, selected_states, selected_cities):
    df = get_df(selected_data_source)
    if (selected_cities is None or selected_cities == []):
        zip_codes = []
    else:
        zip_codes = df[df['State'].isin(list(selected_states))]
        zip_codes = zip_codes[zip_codes['City'].isin(list(selected_cities))]
        zip_codes = zip_codes['RegionName'].unique()
    return zip_codes


@callback(
    Output('hpi-line-graph', 'figure'),
    Input('data', 'value'),
    Input('state', 'value'),
    Input('city', 'value'),
    Input('zipcode', 'value')
)
def set_plot(selected_data_source, selected_states, selected_cities, selected_zipcodes):
    data_frame = get_df(selected_data_source)

    if selected_data_source == '3bed':
        chart_title = 'Typical home value of a 3-bedroom home'
    elif selected_data_source == '4bed':
        chart_title = 'Typical home value of a 4-bedroom home'
    else:
        chart_title = 'Typical rental rates'
    
    if ((selected_states is None or selected_states == []) 
    and (selected_cities is None or selected_cities == []) 
    and (selected_zipcodes is None or selected_zipcodes == [])):
        data_frame = data_frame.drop(['RegionID', 'SizeRank', 'RegionName', 'RegionType', 'StateName', 'State', 'City', 'Metro', 'CountyName'], axis=1)
        data_frame = data_frame.groupby('Country')
        location = ' in the United States'
    elif((selected_cities is None or selected_cities == []) and (selected_zipcodes is None or selected_zipcodes == [])):
        data_frame = data_frame[data_frame['State'].isin(selected_states)]
        data_frame = data_frame.drop(['RegionID', 'SizeRank', 'RegionName', 'RegionType', 'StateName', 'City', 'Metro', 'CountyName'], axis=1)
        data_frame = data_frame.groupby('State')
        location = f' in {selected_states}'
    elif(selected_zipcodes is None or selected_zipcodes == []):
        data_frame = data_frame[data_frame['State'].isin(selected_states)]
        data_frame = data_frame[data_frame['City'].isin(selected_cities)]
        data_frame = data_frame.drop(['RegionID', 'SizeRank', 'RegionName', 'RegionType', 'StateName', 'State', 'Metro', 'CountyName'], axis=1)
        data_frame = data_frame.groupby('City')
        location = f' in {selected_cities}, {selected_states}'
    else:
        data_frame = data_frame[data_frame['State'].isin(selected_states)]
        data_frame = data_frame[data_frame['City'].isin(selected_cities)]
        data_frame = data_frame[data_frame['RegionName'].isin(selected_zipcodes)]
        data_frame = data_frame.groupby('RegionName')
        location = f' in {selected_zipcodes}'

    data_frame = data_frame.mean()
    data_frame = data_frame.transpose()

    fig = px.line(data_frame, labels={'index': 'Year', 'value': 'Price'}, title=chart_title+location)
    fig.update_layout(title_x=.5)
    for i in range(int(data_frame.iloc[-1].shape[0])):
        x_coord = data_frame.iloc[-1].name
        y_coord = data_frame.iloc[-1].values[i]        
        fig.add_scatter(x=[x_coord], y=[y_coord], marker={'color': 'black'}, mode='markers + text', showlegend=False, text='$' + str(round(y_coord / 1000, 1)) + 'K', textposition='middle left')
    
    return fig

#~~~ Callbacks ~~~#