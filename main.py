from http import server
from dash import Dash

app = Dash(__name__, use_pages=True)
server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)