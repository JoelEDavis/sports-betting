import pandas as pd
import os
from utils import OddsAPI, OddsDataProcessor, ValueCalculator, DevigCalculator
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
api_key = os.getenv("KEY")

def main():
    region = 'eu'
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
                  'soccer_switzerland_superleague',
                  'soccer_turkey_super_league',
                  'soccer_uefa_europa_conference_league',
                  'soccer_uefa_champs_league',
                  'soccer_uefa_europa_league',
                  'soccer_conmebol_copa_libertadores',
                  'soccer_usa_mls'
                  ]
                        
    historical = False

    if historical:
        scan_start_date = '2024-01-16'
        scan_end_date = '2024-02-28'
    else:
        scan_start_date = scan_end_date = datetime.now().strftime('%Y-%m-%d')

    bookie_odds = []

    for single_date in pd.date_range(scan_start_date, scan_end_date):
        date = single_date.strftime('%Y-%m-%dT00:00:00Z')
        for sport_key in sport_keys:
            try:
                odds_api = OddsAPI(api_key, region, market, sport_key, date=date, historical=historical)
                odds_data = odds_api.call_api()

                df = OddsDataProcessor.process_data(odds_data)
                df = df[df['bookmaker_key'] == 'pinnacle']

                # DevigCalc here for margin-per-market
                # df = DevigCalculator.calculate_vig(df)

                bookie_odds.append(df)

            except Exception as e:
                print(f"Skipping {sport_key} due to error: {str(e)}")
                continue

    if bookie_odds:
        all_bookie_odds = pd.concat(bookie_odds)
        #DevigCalc here for margin-per-bookie
        all_bookie_odds = DevigCalculator.calculate_vig(all_bookie_odds)
        all_bookie_odds.to_csv("All_Odds_From_Bookie.csv", index=False)

if __name__ == "__main__":
    main()
