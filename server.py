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

@dataclass
class GamesPlayedData:
    teamId: int
    season: int
    games: list
    """
    list of what objects
        {
            runs_scored: int
            runs_allowed: int
            hits: int
            hits_allowed: int
            gameWon: bool
            errors: int
            date: str
            gameId: int
        }
    """
    def addGame(self,gameData):
        game = {}
        isHomeTeam = gameData['home_id'] == self.teamId
        game['gameId'] = gameData['game_id']
        game['date'] = gameData['game_date']

        if isHomeTeam:
            game['runs_scored'] = gameData['home_score']
            game['runs_allowed'] = gameData['away_score']
            game['hits'] = gameData['home_hits']
            game['hits_allowed'] = gameData['away_hits']
        else:
            game['runs_scored'] = gameData['away_score']
            game['runs_allowed'] = gameData['home_score']
            game['hits'] = gameData['away_hits']
            game['hits_allowed'] = gameData['home_hits']

        game['gameWon'] = game['runs_scored'] > game['runs_allowed']


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

def getLinescoreHistogram(teamId: int, season: int,teamName: str = "N/A"):
    #check if diskcache has data for teamId and season
    with diskcache.Cache(CACHE_DIR) as cache:
        key = f"linescore_histogram_{teamId}_{season}"
        if key in cache:
            print(f'Using cached linescore histogram for key: {key}')
            return cache[key]
        else:
            print(f'Fetching linescore histogram from statsapi for key: {key}')
            gamesPlayed = getGamesPlayed(teamId=teamId, season=season)
            print('Number of games played:', len(gamesPlayed))
            histogram = LinescoreHistogram(teamId=teamId, teamName=teamName)
            
            for gp in gamesPlayed:
                
                linescore = getLinescore(gameId=gp['game_id'])
                histogram.addLinescore(linescore, homeId=gp['home_id'])
            
            cache[key] = histogram
            return histogram


        
class LinescoreHistogram:
    def __init__(self,teamId,teamName="N/A"):
        self.teamId = teamId
        self.teamName = teamName
        """
            need hits histogram 
            necessary implement
                hits,runs
            secondary implementation 
                .first
                .second
                .third

        """
        self.date = "N/A" #never added
        self.hits = [0] * 9
        self.runs = [0] * 9
        self.hits_allowed = [0] * 9
        self.runs_allowed = [0] * 9

        self.total_hits = 0
        self.total_runs = 0
        self.total_hits_allowed = 0
        self.total_runs_allowed = 0
        self.games_played = 0

        self.first = []#only first inning data
        self.second = []#only second inning data
        self.third = []#only third inning data
        self.fourth = []#only fourth inning data
        self.fifth = []#only fifth inning data
        self.sixth = []#only sixth inning data
        self.seventh = []#only seventh inning data
        self.eighth = []#only eighth inning data
        self.ninth = []#only ninth inning data

        self.averages = {}
    
    def addLinescore(self,linescore,homeId):
        isHomeTeam = homeId == self.teamId
        """
            what does game look like?
            dict
            {    
                "copyright"
                "currentInning":9
                "currentInningOrdinal":"9th"
                "inningState":"Bottom"
                "inningHalf":"Bottom"
                "isTopInning":false
                "scheduledInnings":9
                "innings": [
                    i -> 
                        home : { 
                            runs 
                            hits
                            errors
                            leftOnBase
                        }
                        away: {...}
                ]
                "teams":{...}
                "defense":{...}
                "offense":{...}
                "balls":2
                "strikes":0
                "outs":3
        }
        """
        teamSideKey = 'home' if isHomeTeam else 'away'
        otherKey = 'away' if isHomeTeam else 'home'
        for inningIdx,inning in enumerate(linescore['innings']):
            if inningIdx >= 9:
                break
             # innings are 1-indexed
            if 'runs'in inning[teamSideKey]:
                self.runs[inningIdx] += inning[teamSideKey]['runs']
            if 'hits' in inning[teamSideKey]:
                self.hits[inningIdx] += inning[teamSideKey]['hits']
            if 'runs' in inning[otherKey]:
                self.runs_allowed[inningIdx] += inning[otherKey]['runs']
            if 'hits' in inning[otherKey]:
                self.hits_allowed[inningIdx] += inning[otherKey]['hits']
        
        if 'runs' in linescore['teams'][teamSideKey]:
            self.total_runs += linescore['teams'][teamSideKey]['runs']
        if 'hits' in linescore['teams'][teamSideKey]:
            self.total_hits += linescore['teams'][teamSideKey]['hits']
        if 'runs' in linescore['teams'][otherKey]:
            self.total_runs_allowed += linescore['teams'][otherKey]['runs']
        if 'hits' in linescore['teams'][otherKey]:
            self.total_hits_allowed += linescore['teams'][otherKey]['hits']

        self.games_played += 1
    
    def calculateAverages(self): 
        """
            calculate averages for hits and runs per inning
            return a dict with the averages
        """
        self.averages = {
            'hits': [round(h / self.games_played, 2) for h in self.hits],
            'runs': [round(r / self.games_played, 2) for r in self.runs],
            'hits_allowed': [round(ha / self.games_played, 2) for ha in self.hits_allowed],
            'runs_allowed': [round(ra / self.games_played, 2) for ra in self.runs_allowed],
            'total_hits': round(self.total_hits / self.games_played, 2),
            'total_runs': round(self.total_runs / self.games_played, 2),
            'total_hits_allowed': round(self.total_hits_allowed / self.games_played, 2),
            'total_runs_allowed': round(self.total_runs_allowed / self.games_played, 2)
        }

    def __str__(self):
        return f'Team:{self.teamName} Linescore Histogram\n teamId: {self.teamId} \n hits: {self.hits} \n runs: {self.runs} \n hits allowed: {self.hits_allowed} \n runs allowed: {self.runs_allowed} \n total hits: {self.total_hits} \n total runs: {self.total_runs} \n total hits allowed: {self.total_hits_allowed} \n total runs allowed: {self.total_runs_allowed} \n games played: {self.games_played}\n'


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
        cache.pop(key,None)
        print('Cleared cache for', key)
        # del cache[key]
    return True

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
                result = list(filter(lambda x: int(x['home_score']) != 0 or int(x['away_score']) != 0, result))
                stored['data'] += result
                stored['endDate'] = currentDate
                cache[key] = stored
                
                return stored['data']
            else:
                # return the data from diskcache
                print('Returning cached data for', key)
                return list(filter(lambda x: int(x['home_score']) != 0 or int(x['away_score']) != 0, stored['data'])) 
        else:
            print('Fetching from statsapi',key)
            # query statsapi for games played from startDate to today
            result = list(
                        filter(lambda x: int(x['home_score']) != 0 or int(x['away_score']) != 0, 
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