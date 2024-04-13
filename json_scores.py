import json

with open('scores.json') as f:
    jsondata = json.load(f)

for game in jsondata['events']:
    league = game['tournament']['name']
    hometeam = game['homeTeam']['name']
    homescore = game['homeScore']['current']
    awayteam = game['awayTeam']['name']
    awayscore = game['awayScore']['current']

    print(league, "|", hometeam, homescore, " - ", awayscore, awayteam)