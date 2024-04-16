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

class ArbitrageCalculator:
    @staticmethod
    def calculate_arbitrage(df, stake):
        df = df[~df['bookmaker_key'].isin(['betfair_ex_uk', 'betfair_ex_eu', 'matchbook'])]
        idx = df.groupby(['game_id', 'outcome_name'])['outcome_price'].idxmax()
        df_arb = df.loc[idx].copy()
        df_arb['impl_prob'] = 1 / df_arb['outcome_price']
        df_arb['sum_impl_prob'] = df_arb.groupby('game_id')['impl_prob'].transform('sum')
        df_arb = df_arb[df_arb['sum_impl_prob'] < 0.99]
        df_arb['stake'] = stake / df_arb['sum_impl_prob'] * df_arb['impl_prob']
        df_arb['ror'] = (1 - df_arb['sum_impl_prob'])
        df_arb['profit'] = stake * df_arb['ror']
        return df_arb

def main():
    api_key = 'cfbd0505443704067b3f02181ccffcde'
    region = 'eu,uk'
    market = 'h2h'
    sport_key = 'soccer_epl'
    stake = 1000

    odds_api = OddsAPI(api_key, region, market, sport_key)
    odds_data = odds_api.call_api()

    df = OddsDataProcessor.process_data(odds_data)

    df_arb = ArbitrageCalculator.calculate_arbitrage(df, stake)

    df_arb.to_csv("Arb_Opportunities.csv")

if __name__ == "__main__":
    main()