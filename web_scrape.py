import requests
import os
import pandas as pd

def import_data():
    API_KEY = 'cfbd0505443704067b3f02181ccffcde'
    SPORT = 'soccer_epl'
    REGIONS = 'uk'
    MARKETS = 'h2h'
    ODDS_FORMAT = 'decimal'
    DATE_FORMAT = 'iso'

    odds_response = requests.get(
        f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds',
        params={
            'api_key': API_KEY,
            'regions': REGIONS,
            'markets': MARKETS,
            'oddsFormat': ODDS_FORMAT,
            'dateFormat': DATE_FORMAT,
        }
    )

    if odds_response.status_code == 200:
        odds_json = odds_response.json()
        print('Number of upcoming matches:', len(odds_json))
        print(odds_json) 
        print('Remaining requests', odds_response.headers['x-requests-remaining'])
        print('Used requests', odds_response.headers['x-requests-used'])
        return odds_json  # Return odds_json here
    else:
        print(f'Failed to get odds: status_code {odds_response.status_code}, response body {odds_response.text}')
        return None  # Return None if failed to fetch odds

def visualise(odds):  # Pass odds as an argument
    if odds is None:
        print("No odds data available.")
        return None

    events = []
    for event in odds:
        event_id = event['id']
        sport_key = event['sport_key']
        sport_title = event['sport_title']
        commence_time = event['commence_time']
        home_team = event['home_team']
        away_team = event['away_team']

        for bookmaker in event['bookmakers']:
            bookmaker_key = bookmaker['key']
            bookmaker_title = bookmaker['title']

        for market in bookmaker['markets']:
            if market['key'] == 'spreads':
                for outcome in market['outcomes']:
                    team = outcome['name']
                    price = outcome['price']
                    point = outcome['point']

                    events.append([event_id, sport_key, sport_title, commence_time, home_team, away_team, 
                                   bookmaker_key, bookmaker_title, team, price, point])

    columns = ['Event ID', 'Sport Key', 'Sport Title', 'Commence Time', 'Home Team', 'Away Team', 
            'Bookmaker Key', 'Bookmaker Title', 'Team', 'Price', 'Point Spread']
    df = pd.DataFrame(events, columns=columns)

    df.to_csv('PL_Odds.csv', index=False)  # Remove df argument here
    
# Now call the functions
odds_data = import_data()
visualise(odds_data)  # Pass odds_data to visualise function