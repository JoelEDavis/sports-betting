import http.client, json

conn = http.client.HTTPSConnection("api.sofascore.com")

headers = {
    'accept': "*/*",
    'accept-language': "en-GB,en-US;q=0.9,en;q=0.8",
    'cache-control': "max-age=0",
    'if-none-match': "W/3355c4e6fb",
    'origin': "https://www.sofascore.com",
    'referer': "https://www.sofascore.com/",
    'sec-ch-ua': "Google",
    'sec-ch-ua-mobile': "?0",
    'sec-ch-ua-platform': "Windows",
    'sec-fetch-dest': "empty",
    'sec-fetch-mode': "cors",
    'sec-fetch-site': "same-site",
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    }

conn.request("GET", "/api/v1/sport/football/events/live")

res = conn.getresponse()

data = json.loads(res.read())

for game in data['events']:
    league = game['tournament']['name']
    hometeam = game['homeTeam']['name']
    homescore = game['homeScore']['current']
    awayteam = game['awayTeam']['name']
    awayscore = game['awayScore']['current']

    print(league, "|", hometeam, homescore, " - ", awayscore, awayteam)