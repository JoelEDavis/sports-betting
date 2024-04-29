import pandas as pd
import requests

class OddsAPI:
    def __init__(self, api_key, region, market, sport_key, date=None, historical=False):
        self.api_key = api_key
        self.region = region
        self.market = market
        self.sport_key = sport_key
        self.date = date
        self.historical = historical

    def call_api(self):
        if self.historical:
            url = f'https://api.the-odds-api.com/v4/historical/sports/{self.sport_key}/odds/?apiKey={self.api_key}&regions={self.region}&market={self.market}&date={self.date}'
        else:
            url = f'https://api.the-odds-api.com/v4/sports/{self.sport_key}/odds/?apiKey={self.api_key}&regions={self.region}&market={self.market}'
        
        odds_response = requests.get(url)
        odds_data = odds_response.json()
        print('Remaining requests', odds_response.headers['x-requests-remaining'])
        print('Used requests', odds_response.headers['x-requests-used'])
        return odds_data

# class OddsDataProcessor:
#     @staticmethod
#     def process_current_data(odds_data):
#         rows_list = []
#         for game in odds_data:
#             for bookmaker in game['bookmakers']:
#                 for market_ in bookmaker['markets']:
#                     for outcome in market_['outcomes']:
#                         row = {
#                             'game_id': game['id'],
#                             'sport_key': game['sport_key'],
#                             'sport_title': game['sport_title'],
#                             'home_team': game['home_team'],
#                             'away_team': game['away_team'],
#                             'commence_time': game['commence_time'],
#                             'bookmaker_key': bookmaker['key'],
#                             'bookmaker_title': bookmaker['title'],
#                             'bookmaker_last_update': bookmaker['last_update'],
#                             'market_key': market_['key'],
#                             'market_last_update': market_['last_update'],
#                             'outcome_name': outcome['name'],
#                             'outcome_price': outcome['price']
#                         }
#                         rows_list.append(row)
#         return pd.DataFrame(rows_list)

#     @staticmethod
#     def process_historical_data(odds_data):
#         rows_list = []
#         for game in odds_data:
#             for bookmaker in game['sites']:
#                 for outcome in bookmaker['odds']['h2h']:
#                     row = {
#                         'game_id': game['id'],
#                         'sport_key': game['sport_key'],
#                         'sport_title': game['sport_title'],
#                         'home_team': game['home_team'],
#                         'away_team': game['away_team'],
#                         'commence_time': game['commence_time'],
#                         'bookmaker_key': bookmaker['site_key'],
#                         'bookmaker_title': bookmaker['site_nice'],
#                         'bookmaker_last_update': bookmaker['last_update'],
#                         'outcome_name': outcome['team'],
#                         'outcome_price': outcome['odds']
#                     }
#                     rows_list.append(row)
#         return pd.DataFrame(rows_list)

#     @staticmethod
#     def process_data(odds_data, historical=False):
#         """
#         Process data from either the current or historical endpoint.
#         """
#         if historical:
#             return OddsDataProcessor.process_historical_data(odds_data)
#         else:
#             return OddsDataProcessor.process_current_data(odds_data)

# class OddsDataProcessor:
#     @staticmethod
#     def process_data(odds_data):
#         rows_list = []
#         for game in odds_data:
#             for bookmaker in game['bookmakers']:
#                 for market_ in bookmaker['markets']:
#                     for outcome in market_['outcomes']:
#                         row = {
#                             'game_id': game['id'],
#                             'sport_key': game['sport_key'],
#                             'sport_title': game['sport_title'],
#                             'home_team': game['home_team'],
#                             'away_team': game['away_team'],
#                             'commence_time': game['commence_time'],
#                             'bookmaker_key': bookmaker['key'],
#                             'bookmaker_title': bookmaker['title'],
#                             'bookmaker_last_update': bookmaker['last_update'],
#                             'market_key': market_['key'],
#                             'market_last_update': market_['last_update'],
#                             'outcome_name': outcome['name'],
#                             'outcome_price': outcome['price']
#                         }
#                         rows_list.append(row)
#         return pd.DataFrame(rows_list)
    
class OddsDataProcessor:
    @staticmethod
    def process_data(odds_data):
        if isinstance(odds_data, list):  # Check if it's the current version
            data = odds_data
        elif isinstance(odds_data, dict) and 'data' in odds_data:  # Check if it's the historical version
            data = odds_data['data']
        else:
            raise ValueError("Invalid odds_data format")

        rows_list = []
        for game in data:
            if 'bookmakers' in game:  # Ensure the structure is consistent
                for bookmaker in game['bookmakers']:
                    for market_ in bookmaker.get('markets', []):  # Use .get() to handle missing 'markets'
                        for outcome in market_.get('outcomes', []):  # Use .get() to handle missing 'outcomes'
                            row = {
                                'game_id': game.get('id', ''),
                                'sport_key': game.get('sport_key', ''),
                                'sport_title': game.get('sport_title', ''),
                                'home_team': game.get('home_team', ''),
                                'away_team': game.get('away_team', ''),
                                'commence_time': game.get('commence_time', ''),
                                'bookmaker_key': bookmaker.get('key', ''),
                                'bookmaker_title': bookmaker.get('title', ''),
                                'bookmaker_last_update': bookmaker.get('last_update', ''),
                                'market_key': market_.get('key', ''),
                                'market_last_update': market_.get('last_update', ''),
                                'outcome_name': outcome.get('name', ''),
                                'outcome_price': outcome.get('price', '')
                            }
                            rows_list.append(row)
        return pd.DataFrame(rows_list)

class ValueCalculator:
    @staticmethod
    def calculate_value(df, bankroll, sharp_bookmakers, valid_bookmakers):
        # Filter DataFrame to include only sharp bookmakers
        df_sharp = df[df['bookmaker_key'].isin(sharp_bookmakers)]
        
        # Calculate the average odds for each outcome from sharp bookmakers
        avg_sharp_odds = df_sharp.groupby(['game_id', 'outcome_name'])['outcome_price'].mean()
        avg_sharp_odds = avg_sharp_odds.reset_index().rename(columns={'outcome_price': 'avg_sharp_price'})
        
        # Filter out exchange markets
        df_valid = df[df['bookmaker_key'].isin(valid_bookmakers)]
        
        # Find the odds from all bookmakers higher than the average sharp odds
        df_higher_than_avg = df_valid.merge(avg_sharp_odds, on=['game_id', 'outcome_name'])
        df_higher_than_avg = df_higher_than_avg[df_higher_than_avg['outcome_price'] > df_higher_than_avg['avg_sharp_price']]
        
        # Calculate win probability based on odds provided and establish the price difference between sharp and soft bookmakers
        df_higher_than_avg['win_probability'] = 1 / df_higher_than_avg['outcome_price']
        df_higher_than_avg['sharp_probability'] = 1 / df_higher_than_avg['avg_sharp_price']
        df_higher_than_avg['price_difference'] = df_higher_than_avg['outcome_price'] - df_higher_than_avg['avg_sharp_price']
        
        # Calculate ROI for each outcome
        df_higher_than_avg['ROI%'] = (((df_higher_than_avg['outcome_price'] - 1) * df_higher_than_avg['sharp_probability']) - (1 - df_higher_than_avg['sharp_probability']))
        
        # Calculate bet size using Kelly Criterion
        df_higher_than_avg['Bankroll%'] = (((df_higher_than_avg['outcome_price'] - 1) * df_higher_than_avg['sharp_probability']) - (1 - df_higher_than_avg['sharp_probability'])) / (df_higher_than_avg['outcome_price'] - 1)
        df_higher_than_avg['Bet Size'] = bankroll * df_higher_than_avg['Bankroll%']
        df_higher_than_avg['Bet Size'] = df_higher_than_avg['Bet Size'].apply(lambda x: round(x, -1))

        df_higher_than_avg['Positive EV'] = df_higher_than_avg['Bet Size'] * df_higher_than_avg['ROI%']
        df_higher_than_avg['Total Bet EV'] = df_higher_than_avg['Bet Size'] * df_higher_than_avg['sharp_probability'] * df_higher_than_avg['outcome_price']

        return df_higher_than_avg

    
class ArbitrageCalculator:
    @staticmethod
    def calculate_arbitrage(df, valid_bookmakers, stake):
        df = df[df['bookmaker_key'].isin(valid_bookmakers)]
        idx = df.groupby(['game_id', 'outcome_name'])['outcome_price'].idxmax()
        df_arb = df.loc[idx].copy()
        df_arb['impl_prob'] = 1 / df_arb['outcome_price']
        df_arb['sum_impl_prob'] = df_arb.groupby('game_id')['impl_prob'].transform('sum')
        df_arb = df_arb[df_arb['sum_impl_prob'] < 1]
        df_arb['stake'] = stake / df_arb['sum_impl_prob'] * df_arb['impl_prob']
        df_arb['ror'] = (1 - df_arb['sum_impl_prob'])
        df_arb['profit'] = stake * df_arb['ror']
        return df_arb