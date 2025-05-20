import statsapi
import json
from datetime import datetime,timedelta
import diskcache


def getGamesPlayed(teamId: int,season: int):
    if type(teamId) != int:
        return []
    if type(season) != int:
        return []
    
    #create date range from start of season to today
    endDate = datetime.today().strftime('%m/%d/%Y')
    startDate = "01/01/" + str(season)
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
            stored = cache[key]
            if stored['endDate'] < endDate: #dates are strings
                # query statsapi for games played from stored enddate to today
                endDatePlusOne = datetime.strptime(stored['endDate'], '%m/%d/%Y') + timedelta(days=1)
                result = statsapi.get(
                    "schedule",
                    params={
                        'teamId': teamId,
                        'season': season,
                        'startDate': endDatePlusOne.strftime('%m/%d/%Y'),
                        'endDate': endDate,
                    }
                )
                stored['data'] += result
        # store the data in diskcache
        # cache[key] = result['dates']
    return []