import pandas as pd
import requests

class OddsAPI:
    def __init__(self, api_key, region, market, sport_key):
        self.api_key = api_key
        self.region = region
        self.market = market
        self.sport_key = sport_key

    def call_api(self):
        url = f'https://api.the-odds-api.com/v4/sports/{self.sport_key}/odds/?apiKey={self.api_key}&regions={self.region}&market={self.market}'
        odds_response = requests.get(url)
        odds_data = odds_response.json()
        print('Remaining requests', odds_response.headers['x-requests-remaining'])
        print('Used requests', odds_response.headers['x-requests-used'])
        return odds_data


class OddsDataProcessor:
    @staticmethod
    def process_data(odds_data):
        rows_list = []
        for game in odds_data:
            for bookmaker in game['bookmakers']:
                for market_ in bookmaker['markets']:
                    for outcome in market_['outcomes']:
                        row = {
                            'game_id': game['id'],
                            'sport_key': game['sport_key'],
                            'sport_title': game['sport_title'],
                            'home_team': game['home_team'],
                            'away_team': game['away_team'],
                            'commence_time': game['commence_time'],
                            'bookmaker_key': bookmaker['key'],
                            'bookmaker_title': bookmaker['title'],
                            'bookmaker_last_update': bookmaker['last_update'],
                            'market_key': market_['key'],
                            'market_last_update': market_['last_update'],
                            'outcome_name': outcome['name'],
                            'outcome_price': outcome['price']
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
        df_higher_than_avg['ROI'] = (((df_higher_than_avg['outcome_price'] - 1) * df_higher_than_avg['sharp_probability']) - (1 - df_higher_than_avg['sharp_probability']))
        
        # Calculate bet size using Kelly Criterion
        df_higher_than_avg['Bankroll%'] = (((df_higher_than_avg['outcome_price'] - 1) * df_higher_than_avg['sharp_probability']) - (1 - df_higher_than_avg['sharp_probability'])) / (df_higher_than_avg['outcome_price'] - 1)
        df_higher_than_avg['Bet Size'] = bankroll * df_higher_than_avg['Bankroll%']
        df_higher_than_avg['Bet Size'] = df_higher_than_avg['Bet Size'].apply(lambda x: round(x, -1))

        df_higher_than_avg['EV'] = df_higher_than_avg['Bet Size'] * df_higher_than_avg['ROI%']

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