import statsapi
import json
from datetime import datetime,timedelta
import diskcache
import functools

from dataclasses import dataclass

SEASON = "2025"
SEASON_START = "03/18/" + SEASON
CACHE_DIR = "statsapi_cache"

"""
    store what?
    linescore per game or histogram of linescore until today

    need per game hits, at bats, runs
"""


def getLinescore(gameId: int):
    """
        get linescore for gameId
        if linescore is not in diskcache, fetch from statsapi
        store in diskcache
    """
    if type(gameId) != int:
        return None
    
    with diskcache.Cache(CACHE_DIR) as cache:
        key = f"linescore_{gameId}"
        if key in cache:
            print('Using cached linescore for', gameId)
            return cache[key]
        else:
            print('Fetching linescore from statsapi for', gameId)
            linescore = statsapi.get("game_linescore",params={
                'gamePk':gameId
            })
            cache[key] = linescore
            return linescore


# def diskcache_it(key_prefix="",keys=[]):
#     def decorator_wrapper(func):
#         @functools.wraps(func)
#         def wrapper(*args,**kwargs):
#             cache_key = key_prefix
#             for k in keys:
#                 cache_key += "_"+k
            
#             result = None
#             with diskcache.Cache(CACHE_DIR) as cache:
#                 if cache_key in cache:
#                     result = cache[cache_key]['data']
#                 else:
#                     result = func(*args,**kwargs)
#                     cache[cache_key]['data'] = result
#             return result
#         return wrapper
#     return decorator_wrapper


#store games
#store linescores for games

@dataclass
class Game:
    gameId: int
    data: dict

@dataclass
class Linescore:
    game: Game
    linescoreData: dict
    
@dataclass
class GamesPlayed:
    teamId: int
    season: int
    games: list

@dataclass 
class GameData:
    gameId: int
    gameData: dict
    linescoreData: dict

@dataclass
class TeamGameContainer:
    teamId: int
    season: int
    playedGameIds: list#list of game ids


@dataclass
class TeamGameContainer2:
    teamId: int
    season: int
    playedGameIds: list#list of game ids
    
    mostRecentDate: datetime.date
    mostRecentGameId: int
     

def clearTGC2():
    """
        clear the cache for team_game_container2
    """
    with diskcache.Cache(CACHE_DIR) as cache:
        keys = list(cache.iterkeys())
        teamGameContainer2Keys = filter(lambda x: 'team_game_container2' in x, keys)
        for tgc2Key in teamGameContainer2Keys:
            if tgc2Key in cache:
                cache.pop(tgc2Key)
                print('Cleared cache for', tgc2Key)

def addDatesToTGC():
    #for every teamGameContainer in diskcache
    #grab the latest game date from gameData in diskcache
    with diskcache.Cache(CACHE_DIR) as cache:
        keys = list(cache.iterkeys())
        teamGameContainerKeys = filter(lambda x: 'team_game_container' in x, keys)
        for tgcKey in teamGameContainerKeys:
            tgc = cache[tgcKey]
            tgcKey2 = f"team_game_container2_{tgc.teamId}_{tgc.season}"
            tgc2 = TeamGameContainer2(
                teamId=tgc.teamId,
                season=tgc.season,
                playedGameIds=tgc.playedGameIds,
                mostRecentDate=None,
                mostRecentGameId=None)
            
            mostRecentDate = None
            mostRecentGameId = None
            for gameId in tgc.playedGameIds:
                gameDataKey = f"game_data_{gameId}"
                if gameDataKey in cache:
                    gameData = cache[gameDataKey]
                    
                    print(gameData.gameData['game_date'])
                    gameDate = datetime.strptime(gameData.gameData['game_date'], '%Y-%m-%d').date()
                    if not mostRecentDate or gameDate > mostRecentDate:
                        mostRecentDate = gameDate
                        mostRecentGameId = gameId
            tgc2.mostRecentDate = mostRecentDate
            tgc2.mostRecentGameId = mostRecentGameId
            cache[tgcKey2] = tgc2
            print(f"Updated {tgcKey2} with most recent date {mostRecentDate} and game id {mostRecentGameId}")

def aggregateGameDataAndLinescore():
    #do what 
    #for every game id 
    #grab the corresponding stored linescore
    #store in a single object
    with diskcache.Cache(CACHE_DIR) as cache:
        keys = list(cache.iterkeys())
        #for games played
        linescoreKeys = filter(lambda x: 'linescore' in x, keys)
        linescores = list(linescoreKeys)
        games_played = list(filter(lambda x: 'games_played' in x, keys))

        for gpKey in games_played:
            #do what here
            teamId = int(gpKey.split('_')[2])
            teamGameContainerKey = f"team_game_container_{teamId}_{SEASON}"
            teamGameContainer = TeamGameContainer(teamId=teamId,season=SEASON,playedGameIds=[])
            
            print('Working on => ',teamId,gpKey)
            gamesPlayed = cache[gpKey]['data']
            teamGameContainer.playedGameIds = [ gp['game_id'] for gp in gamesPlayed ]
            for gp in gamesPlayed:
                gameDataKey = f"game_data_{gp['game_id']}"
                #check if key already in cache
                if not gameDataKey in cache:  
                    gd = GameData(gameId=gp['game_id'],gameData=gp,linescoreData=None)
                    linescore = getLinescore(gameId=gp['game_id'])
                    gd.linescoreData = linescore
                    # print(gd)
                    cache[gameDataKey] = gd
                # break
            # print(teamGameContainer)
            cache[teamGameContainerKey] = teamGameContainer
            # break
        # pass

def clearGamesPlayed(teamId: int, season: int):
    """
        clear the cache for the given key
    """
    if type(teamId) != int:
        return False
    if type(season) != int:
        return False
    
    key = f"games_played_{teamId}_{season}"

    with diskcache.Cache(CACHE_DIR) as cache:
        cache.pop(key)
        print('Cleared cache for', key)
        # del cache[key]
    return True

def gamePlayedFilter(game: dict):
    #make sure that at least one of the scores is not zero and the status is 'Final'
    return (int(game['home_score']) != 0 or int(game['away_score']) != 0) and game['status'] == 'Final'


def updateGamesPlayed(teamId: int, season: int):
    #grab all games played after today that are completed
    if type(teamId) != int:
        print('teamId is not an int:', teamId)
        return []
    if type(season) != int:
        print('season is not an int:', season)
        return []
    currentDate = datetime.today().strftime('%m/%d/%Y')
    startDate = SEASON_START


def getGamesPlayed2(teamId: int, season: int):
    if type(teamId) != int:
        print('teamId is not an int:', teamId)
        return []
    if type(season) != int:
        print('season is not an int:', season)
        return []
    
    with diskcache.Cache(CACHE_DIR) as cache:
        #grab teamGameContainer from cache
        teamGameContainerKey = f"team_game_container_{teamId}_{season}"
        if teamGameContainerKey in cache:
            print('Using cached team game container for', teamId, season)
            teamGameContainer = cache[teamGameContainerKey]
            #for each game id in teamGameContainer.playedGameIds
            games = []
            for gameId in teamGameContainer.playedGameIds:
                gameDataKey = f"game_data_{gameId}"
                if gameDataKey in cache:
                    games.append(cache[gameDataKey])
            return games
    return []
                    

def getGamesPlayed(teamId: int,season: int):
    if type(teamId) != int:
        print('teamId is not an int:', teamId)
        return []
    if type(season) != int:
        print('season is not an int:', season)
        return []
    
    #create date range from start of season to today
    currentDate = datetime.today().strftime('%m/%d/%Y')
    startDate = SEASON_START
    """
        check diskcache for data for teamid and season and enddate

        if enddate is before today 
        query statsapi for games played from stored enddate to today
        merge the data with the data in diskcache
        store the data in diskcache
    """
    with diskcache.Cache(CACHE_DIR) as cache:
        key = f"games_played_{teamId}_{season}"
    
        if key in cache:
            print('using cache',key)
            stored = cache[key]
            if stored['endDate'] < currentDate: #dates are strings
                # query statsapi for games played from stored enddate to today
                print('Updating cache for', key)
                endDatePlusOne = datetime.strptime(stored['endDate'], '%m/%d/%Y') + timedelta(days=1)
                result = statsapi.schedule(
                        team=teamId,
                        season=season,
                        start_date=endDatePlusOne.strftime('%m/%d/%Y'),
                        end_date=currentDate)
                result = list(filter(gamePlayedFilter, result))
                print(json.dumps(result, indent=4))
                stored['data'] += result
                stored['endDate'] = currentDate
                cache[key] = stored
                
                return stored['data']
            else:
                # return the data from diskcache
                print('Returning cached data for', key)
                return list(filter(gamePlayedFilter, stored['data'])) 
        else:
            print('Fetching from statsapi',key)
            # query statsapi for games played from startDate to today
            result = list(
                        filter(gamePlayedFilter, 
                        statsapi.schedule(
                            team=teamId,
                            season=season,
                            start_date=startDate,
                            end_date=currentDate)
                        )
                    )
            stored = {
                'data': result,
                'endDate': currentDate
            }
            cache[key] = stored 
            return result
        # store the data in diskcache
        # cache[key] = result['dates']
    return []

def getTeams():
    """Get all MLB teams"""
    return statsapi.get("teams",params={'sportIds':1,'activeStatus':'Yes'})

def getStatDict(statGroup, teamId):
    """Get team stats for a specific group and team"""
    return statsapi.get("team_stats",
                      params={
                          'season': SEASON,
                          'stats': 'season',
                          'teamId': teamId,
                          'group': statGroup})['stats'][0]['splits'][0]['stat']

def getStandings(season):
    """Get standings data for a season"""
    return statsapi.standings_data(season=season)

def gamesToday(team_id, date):
    """Get games for a specific team on a specific date"""
    result = statsapi.schedule(start_date=date,
                  end_date=date,
                  team=team_id)
    if result == []:
        return [[]]
    return result

def getTeamRoster(teamId: int, date: str):
    """Get team roster for a specific team and date"""
    try:
        # Get roster data from statsapi
        roster_data = statsapi.get("team_roster", params={'teamId': teamId, 'date': date})
        return roster_data
    except Exception as e:
        print(f"Error fetching roster for team {teamId}: {e}")
        return {'roster': []}

def getTeamPitchers(teamId: int, date: str):
    """Get pitchers from team roster"""
    roster_data = getTeamRoster(teamId, date)
    pitchers = []
    
    if 'roster' in roster_data:
        for player in roster_data['roster']:
            person = player.get('person', {})
            position = player.get('position', {})
            
            # Check if player is a pitcher (position type is 'Pitcher')
            if position.get('type') == 'Pitcher':
                pitchers.append({
                    'id': person.get('id'),
                    'name': person.get('fullName', 'Unknown'),
                    'position': position.get('abbreviation', 'P')
                })
    
    return pitchers