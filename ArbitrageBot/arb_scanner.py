import pandas as pd
import sys
import os
from dotenv import load_dotenv
sys.path.append(r'C:\Users\Joel\Desktop\SurebetBot')
from utils import OddsAPI, OddsDataProcessor, ArbitrageCalculator

load_dotenv()
api_key = os.getenv("KEY")

def main():
    api_key = ''
    region = 'uk'
    market = 'h2h'
    sport_keys = [
                  'soccer_australia_aleague',
                  'soccer_austria_bundesliga',
                  'soccer_belgium_first_div',
                  'soccer_brazil_campeonato',
                  'soccer_brazil_serie_b',
                  'soccer_chile_campeonato',
                  'soccer_china_superleague',
                  'soccer_denmark_superliga',
                  'soccer_efl_champ',
                  'soccer_england_league1',
                  'soccer_england_league2',
                  'soccer_epl',
                  'soccer_finland_veikkausliiga',
                  'soccer_france_ligue_one',
                  'soccer_france_ligue_two',
                  'soccer_germany_bundesliga',
                  'soccer_germany_bundesliga2',
                  'soccer_germany_liga3',
                  'soccer_greece_super_league',
                  'soccer_italy_serie_a',
                  'soccer_italy_serie_b',
                  'soccer_japan_j_league',
                  'soccer_korea_kleague1',
                  'soccer_league_of_ireland',
                  'soccer_mexico_ligamx',
                  'soccer_netherlands_eredivisie',
                  'soccer_norway_eliteserien',
                  'soccer_poland_ekstraklasa',
                  'soccer_portugal_primeira_liga',
                  'soccer_spain_la_liga',
                  'soccer_spain_segunda_division',
                  'soccer_spl',
                  'soccer_sweden_allsvenskan',
                  'soccer_sweden_superettan',
                  'soccer_turkey_super_league',
                  'soccer_uefa_europa_conference_league',
                  'soccer_uefa_champs_league',
                  'soccer_uefa_europa_league',
                  'soccer_conmebol_copa_libertadores',
                  'soccer_usa_mls'
                  ]
    
    valid_bookmakers = ['sport888',
                        'betfair_sb_uk',
                        'betvictor',
                        'betway',
                        'boylesports',
                        'casumo',
                        'coral',
                        'grosvenor',
                        'ladbrokes_uk',
                        'leovegas',
                        'livescorebet',
                        'mrgreen',
                        'paddypower',
                        'skybet',
                        'unibet_uk',
                        'virginbet',
                        'williamhill']
    
    stake = 1000

    arb_opportunities = []
    
    for sport_key in sport_keys:
        odds_api = OddsAPI(api_key, region, market, sport_key)
        odds_data = odds_api.call_api()
    
        df = OddsDataProcessor.process_data(odds_data)
    
        df_arb = ArbitrageCalculator.calculate_arbitrage(df, valid_bookmakers, stake)
        arb_opportunities.append(df_arb)

    arb_opportunities = pd.concat(arb_opportunities)
    arb_opportunities.to_csv(f"All Arbitrage Opportunities.csv")

if __name__ == "__main__":
    main()