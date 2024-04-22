import pandas as pd
import sys
import os
from dotenv import load_dotenv
sys.path.append(r'C:\Users\Joel\Desktop\SurebetBot')
from utils import OddsAPI, OddsDataProcessor, ArbitrageCalculator

load_dotenv()
api_key = os.getenv("KEY")

def main():
    region = 'uk'
    # Markets available are h2h, spreads, totals, outrights, h2h_lay, outrights_lay
    market = 'h2h'
    # List of all sports leagues included in arb search
    sport_keys = [
        ## Football ##
                # #   'soccer_argentina_primera_division',
                #   'soccer_australia_aleague',
                #   'soccer_austria_bundesliga',
                #   'soccer_belgium_first_div',
                #   'soccer_brazil_campeonato',
                #   'soccer_brazil_serie_b',
                #   'soccer_chile_campeonato',
                #   'soccer_china_superleague',
                #   'soccer_denmark_superliga',
                #   'soccer_efl_champ',
                #   'soccer_england_league1',
                #   'soccer_england_league2',
                #   'soccer_epl',
                #   'soccer_finland_veikkausliiga',
                #   'soccer_france_ligue_one',
                #   'soccer_france_ligue_two',
                #   'soccer_germany_bundesliga',
                #   'soccer_germany_bundesliga2',
                #   'soccer_germany_liga3',
                # #   'soccer_greece_super_league',
                #   'soccer_italy_serie_a',
                #   'soccer_italy_serie_b',
                #   'soccer_japan_j_league',
                #   'soccer_korea_kleague1',
                #   'soccer_league_of_ireland',
                #   'soccer_mexico_ligamx',
                #   'soccer_netherlands_eredivisie',
                #   'soccer_norway_eliteserien',
                #   'soccer_poland_ekstraklasa',
                #   'soccer_portugal_primeira_liga',
                #   'soccer_spain_la_liga',
                #   'soccer_spain_segunda_division',
                #   'soccer_spl',
                #   'soccer_sweden_allsvenskan',
                # #  'soccer_sweden_superettan',
                #   'soccer_switzerland_superleague',
                #   'soccer_turkey_super_league',
                #   'soccer_uefa_europa_conference_league',
                #   'soccer_uefa_champs_league',
                #   'soccer_uefa_europa_league',
                #   'soccer_conmebol_copa_libertadores',
                #   'soccer_usa_mls',

        ## Other Sports ##
                # # 'americanfootball_cfl',
                # 'americanfootball_ncaaf',
                # 'americanfootball_nfl',
                # # 'americanfootball_ufl',
                # 'aussierules_afl',
                # 'baseball_mlb',
                # 'baseball_ncaa',
                # 'basketball_euroleague',
                # 'basketball_nba',
                # 'basketball_wnba',
                # # 'basketball_ncaab',
                # 'boxing_boxing',
                # 'cricket_ipl',
            

        ## Outrights ##
                'americanfootball_ncaaf_championship_winner',
                'americanfootball_nfl_super_bowl_winner',
                'baseball_mlb_world_series_winner',
                'basketball_nba_championship_winner',
                'basketball_ncaab_championship_winner',
                'golf_masters_tournament_winner',
                'golf_pga_championship_winner',
                'golf_the_open_championship_winner',
                'golf_us_open_winner',
                'icehockey_nhl_championship_winner',
                'politics_us_presidential_election_winner',
                'soccer_fifa_world_cup_winner',
                ]
    
    valid_bookmakers = [
                        'sport888',
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
                        'williamhill',
                        ]
    
    stake = 1000

    arb_opportunities = []
    full_market = []
    
    for sport_key in sport_keys:
        try:
            odds_api = OddsAPI(api_key, region, market, sport_key)
            odds_data = odds_api.call_api()
        
            df = OddsDataProcessor.process_data(odds_data)
            full_market.append(df)
        
            df_arb = ArbitrageCalculator.calculate_arbitrage(df, valid_bookmakers, stake)
            arb_opportunities.append(df_arb)
        except Exception as e:
            print(f"Skipping {sport_key} due to error: {str(e)}")
            continue

    if arb_opportunities:
        arb_opportunities = pd.concat(arb_opportunities)
        arb_opportunities.to_csv(f"All Arbitrage Opportunities.csv")

if __name__ == "__main__":
    main()