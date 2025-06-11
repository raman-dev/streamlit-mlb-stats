import statsapi
import json
from datetime import datetime,timedelta
import diskcache

from dataclasses import dataclass

SEASON = "2025"
SEASON_START = "03/18/" + SEASON

"""
    store what?
    linescore per game or histogram of linescore until today

    need per game hits, at bats, runs
"""
# class Game:
#     def __init__(self,gameData):
#         self.gameId = gameData['game_id']
#         self.homeId = gameData['home_id']
#         self.awayId = gameData['away_id']
#         self.date = gameData['game_date']
#         self.homeName = gameData['home_name']
#         self.awayName = gameData['away_name']
#         self.awayRuns = gameData['away_score']
#         self.homeRuns = gameData['home_score']

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

@dataclass
class Linescore:
    gameId: int
    linescoreData: dict

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
    
    def __str__(self):
        return f'Team:{self.teamName} Linescore Histogram\n teamId: {self.teamId} \n hits: {self.hits} \n runs: {self.runs} \n hits allowed: {self.hits_allowed} \n runs allowed: {self.runs_allowed} \n total hits: {self.total_hits} \n total runs: {self.total_runs} \n total hits allowed: {self.total_hits_allowed} \n total runs allowed: {self.total_runs_allowed} \n games played: {self.games_played}\n'
    

def getLinescoreHistogram(teamId: int, season: int, teamName: str="N/A"):
    #check if object key in diskcache
    #if in cache fetch object
    key = f'linescore_histogram_{teamId}_{season}'
    #check if object is up to date
    with diskcache.Cache('statsapi_cache') as cache:
        if key in cache:
            linescoreHistogram = cache[key]
            return linescoreHistogram
        else:
            #get games played for teamId and season
            #grab gameId's 
            #use gameIds to get linescores
            #store games and gameIds in cache?
            pass
    #if not up to date grab games played after last date in object
    #grab linescores for each game played ``
    #update object for each linescore
    return None

def clearGamesPlayed(teamId: int, season: int):
    """
        clear the cache for the given key
    """
    if type(teamId) != int:
        return False
    if type(season) != int:
        return False
    
    key = f"games_played_{teamId}_{season}"

    with diskcache.Cache('statsapi_cache') as cache:
        cache.pop(key,None)
        print('Cleared cache for', key)
        # del cache[key]
    return True

def getGamesPlayed(teamId: int,season: int):
    if type(teamId) != int:
        return []
    if type(season) != int:
        return []
    
    #create date range from start of season to today
    endDate = datetime.today().strftime('%m/%d/%Y')
    startDate = SEASON_START
    """
        check diskcache for data for teamid and season and enddate

        if enddate is before today 
        query statsapi for games played from stored enddate to today
        merge the data with the data in diskcache
        store the data in diskcache
    """
    with diskcache.Cache('statsapi_cache') as cache:
        key = f"games_played_{teamId}_{season}"
    
        if key in cache:
            print('using cache',key)
            stored = cache[key]
            if stored['endDate'] < endDate: #dates are strings
                # query statsapi for games played from stored enddate to today
                endDatePlusOne = datetime.strptime(stored['endDate'], '%m/%d/%Y') + timedelta(days=1)
                result = statsapi.schedule(
                        team=teamId,
                        season=season,
                        start_date=endDatePlusOne.strftime('%m/%d/%Y'),
                        end_date=endDate)
                stored['data'] += result
                stored['endDate'] = endDate
                cache[key] = stored
                
                return stored['data']
            else:
                # return the data from diskcache
                return cache[key]['data']
        else:
            print('Fetching from statsapi',key)
            # query statsapi for games played from startDate to today
            result = statsapi.schedule(
                        team=teamId,
                        season=season,
                        start_date=startDate,
                        end_date=endDate)
            stored = {
                'data': result,
                'endDate': endDate
            }
            cache[key] = stored 
            return result
        # store the data in diskcache
        # cache[key] = result['dates']
    return []