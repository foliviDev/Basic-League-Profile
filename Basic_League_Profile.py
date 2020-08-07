import requests, json, itertools
from getpass import getpass

def getDDragonData():

    # Extracting champion data from ddragon file and making the dict more accessible
    with open('Resources/champion.json', 'r') as ddragon_data:

        ddragon_champs_raw = json.load(ddragon_data)
        ddragon_champs = ddragon_champs_raw['data']
    
    champ_keys = {}

    # Making a dict with all the champions and their key id
    for champ, data in ddragon_champs.items():

        champ_keys.update({champ: data['key']})

    # Check if the dict is filling correctly, displays 5 entries
    # print(f'\nSome champions and keys: {str(dict(itertools.islice(champ_keys.items(), 50)))}')

    return champ_keys


def requestBySummName(api_key, region, summoner_name):

    summoner_data = requests.get(f'https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={api_key}')

    return summoner_data.json()


def requestByID(api_key, region, summoner_id):

    summoner_ranked = requests.get(f'https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}?api_key={api_key}')

    return summoner_ranked.json()


def summonerProfile(summoner_name, summoner_data_json, summoner_ranked_json):

    # Normal data
    summoner_level = summoner_data_json["summonerLevel"]

    # Ranked data
    if summoner_ranked_json[0]["queueType"] == "RANKED_SOLO_5x5":

        soloq_tier = summoner_ranked_json[0]["tier"]
        soloq_rank = summoner_ranked_json[0]["rank"]
        soloq_points = summoner_ranked_json[0]["leaguePoints"]
        soloq_wins = summoner_ranked_json[0]["wins"]
        soloq_losses = summoner_ranked_json[0]["losses"]

    elif summoner_ranked_json[0]["queueType"] == "RANKED_FLEX_SR":
       
        soloq_tier = summoner_ranked_json[1]["tier"]
        soloq_rank = summoner_ranked_json[1]["rank"]
        soloq_points = summoner_ranked_json[1]["leaguePoints"]
        soloq_wins = summoner_ranked_json[1]["wins"]
        soloq_losses = summoner_ranked_json[1]["losses"]

    else:

        print(f'ERROR, QUEUE TYPE NOT VALID. QUITTING...')
        raise SystemExit

    # Calculating winrate
    soloq_games = soloq_wins + soloq_losses
    soloq_winrate = (soloq_wins * 100) / soloq_games

    # Printing profile as a dictionary
    summoner_profile = {"summoner_name": summoner_name, "summoner_level": summoner_level, 
                        "soloq_tier": soloq_tier, "soloq_rank": soloq_rank, "soloq_points": soloq_points, 
                        "soloq_wins": soloq_wins, "soloq_losses": soloq_losses, "soloq_games": soloq_games, 
                        "soloq_winrate": soloq_winrate}

    return summoner_profile


def requestInGame(api_key, summoner_name, region, summoner_id):

    ingame_info = requests.get(f'https://{region}.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{summoner_id}?api_key={api_key}')

    if ingame_info.status_code == 404:

        print(
            f'''
        CURRENTLY: NOT PLAYING RANKED
            '''
        )

        raise SystemExit

    return ingame_info.json()


def inGameProfile(summoner_name, ingame_info):

    # Finding game length (in seconds), adding 3 minutes to get realtime
    min, sec = divmod(ingame_info["gameLength"] + 180, 60)

    # Finding the id of the champion played
    for player in ingame_info["participants"]:

        if player["summonerName"] == summoner_name:

            champion_played_id = player["championId"]

    # Checking if we got an id
    # print(f'The champ id is: {champion_played_id}')

    # Creating a dictionary with gametime and champion name
    championId_and_time = {"min": min, "sec": sec, "championId": champion_played_id}

    return championId_and_time 


def championIdToName(champ_keys, championId):

    for champ_name, champ_id in champ_keys.items():

        if str(championId) == champ_id:

            return champ_name
    
    return f"ERROR: THE CHAMPION KEY ID ({championId}) IS NOT ON THE DATABASE"


def main():

    print(f'\nBASIC LEAGUE PROFILE (GitHub: folivDev)\n')

    # Getting the API key
    api_key = str(getpass('\nInsert your API key: '))
    
    # Calls the function that gets all the champion data for the current patch in the file
    champ_keys = getDDragonData()

    # Input region and summoner name
    region = str(input(f"\nEnter the region you're interested in (NA = na1, EUW = euw1): "))
    
    if region != 'na1' and region != 'euw1':

        print(f'\nWrong input, remember to use lowercase and to add 1 at the end (example: euw1 for the EUW server). QUITTING...\n')
        raise SystemExit

    else:

        if region == 'na1':

            region_updated = 'North America'

        elif region == 'euw1':

            region_updated = 'Europe West'

        else:

            print(f'\nUNKNOWN ERROR. QUITTING...\n')
            raise SystemExit
    
    summoner_name = str(input(f'\nNow enter your summoner name: '))

    # Calling function to get level and id
    summoner_data_json = requestBySummName(api_key, region, summoner_name)

    # Calling function to get ranked data
    summoner_ranked_json = requestByID(api_key, region, summoner_id = summoner_data_json["id"]) 

    # Calling function to get the summoner profile
    summoner_profile = summonerProfile(summoner_name, summoner_data_json, summoner_ranked_json)

    # Printing the summoner profile
    print(
        f'''
        {summoner_name}'s Profile (SoloQ only):\n
        Level: {summoner_profile.get("summoner_level")}
        Server: {region_updated}
        Tier/Division: {summoner_profile.get("soloq_tier")} {summoner_profile.get("soloq_rank")} ({summoner_profile.get("soloq_points")} points)
        Games Played: {summoner_profile.get("soloq_games")}
        W/L: {summoner_profile.get("soloq_wins")}/{summoner_profile.get("soloq_losses")}
        Winrate: {summoner_profile.get("soloq_winrate"):.2f}%
        '''
    )

    # Calling function to get in-game information
    ingame_info = requestInGame(api_key, summoner_name, region, summoner_id = summoner_data_json["id"])

    # Calling function to process in-game information
    championId_and_time = inGameProfile(summoner_name, ingame_info)

    champion_name = championIdToName(champ_keys, championId_and_time["championId"])

    # Printing the in-game data
    print(
        f'''
        CURRENTLY: IN GAME ({championId_and_time.get("min"):02d}:{championId_and_time.get("sec"):02d}) AS {champion_name}
        '''
    )


if __name__ == "__main__":

    main()