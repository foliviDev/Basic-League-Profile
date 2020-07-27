import requests

# dev API key
api_temp = 'ENTER YOUR API KEY HERE OR IT WONT WORK'

def requestBySummName(region, summoner_name):

    summoner_data = requests.get(f'https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}?api_key={api_temp}')

    return summoner_data.json()

def requestByID(region, summoner_id):

    summoner_ranked = requests.get(f'https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}?api_key={api_temp}')

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

def requestInGame(summoner_name, region, summoner_id):

    ingame_info = requests.get(f'https://{region}.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{summoner_id}?api_key={api_temp}')

    if ingame_info.status_code == 404:

        print(
            f'''
        CURRENTLY: NOT PLAYING RANKED
            '''
        )

        raise SystemExit

    return ingame_info.json()

def inGameProfile(summoner_name, ingame_info):

    # Finding game length and champion played
    min, sec = divmod(ingame_info["gameLength"], 60)
    champion_played = "fiora" # CHANGE THIS TO READ THE CHAMPION PLAYED

    # Creating a dictionary with it
    champion_time = {"min": min, "sec": sec,"champion": champion_played}

    return champion_time 

def main():

    print(f'\nBASIC LEAGUE PROFILE (GitHub: folivDev)\n')

    # Input region and summoner name
    region = str(input(f"Enter the region you're interested in (NA = na1, EUW = euw1): "))
    
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
    
    summoner_name = str(input(f'\nNow please enter your summoner name: '))

    # Calling function to get level and id
    summoner_data_json = requestBySummName(region, summoner_name)

    # Calling function to get ranked data
    summoner_ranked_json = requestByID(region, summoner_id = summoner_data_json["id"])

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
    ingame_info = requestInGame(summoner_name, region, summoner_id = summoner_data_json["id"])

    # Calling function to process in-game information
    champion_time = inGameProfile(summoner_name, ingame_info)

    # Printing the in-game data
    print(
        f'''
        CURRENTLY: IN GAME ({champion_time.get("min")}:{champion_time.get("sec")}) AS {champion_time.get("champion")}
        '''
    )

if __name__ == "__main__":

    main()