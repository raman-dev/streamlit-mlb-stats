import statsapi
import json
from datetime import datetime,timedelta
import diskcache

SEASON = "2025"
SEASON_START = "03/18/" + SEASON

"""
    store what?
    linescore per game or histogram of linescore until today

    need per game hits, at bats, runs
"""

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