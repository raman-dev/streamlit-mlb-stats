import streamlit as st
import statsapi
import json
from datetime import datetime
import pandas as pd
import numpy as np
import server

import diskcache

SEASON=2025

today = datetime.today()
today_str = today.strftime("%m/%d/%Y")

@st.cache_data
def getTeams():
    return statsapi.get("teams",params={'sportIds':1,'activeStatus':'Yes'})


@st.cache_data
def getTeamIds():
    #read from file if exists
    # teams = None
    teamsDict = None
    try:
        with open('team_ids.json','r') as f:
            # teams = json.load(f)
            teamsDict = json.load(f)
    except FileNotFoundError:
        print('creating team_ids file')
        # teams = writeTeamIds()
        teamsDict = writeTeamIds()
    
    return teamsDict

def writeTeamIds():
    
    # with open('team_ids.json') as f:
    #     f.write()
    result = getTeams()
    teams = []
    teamsDict = {}
    for team_data_map in result['teams']:
        # for x in team_data:
        #     st.write(x)
        # st.write(team_data_map['name'],team_data_map['id'])
        # teams.append({'id':team_data_map['id'],'name': team_data_map['name']})
        teamsDict[team_data_map['id']] = {'id':team_data_map['id'],'name': team_data_map['name']}
    # st.write(teams)
    with open('team_ids.json','w+') as f:
        f.write(json.dumps(teamsDict))
    
    return teamsDict

# teamIds = getTeamIds()
teamIdsDict = getTeamIds()

@st.cache_data
def getStatDict(statGroup,teamId):
    return statsapi.get("team_stats",
                      params={
                          'season':SEASON,
                          'stats':'season',
                          'teamId':teamId,
                          'group':statGroup})['stats'][0]['splits'][0]['stat']


def get_stats(statGroup,statNames,teamId):
    statDict = getStatDict(statGroup,teamId)
    return [ statDict[x] for x in statNames ]


@st.fragment
def showTeamsWithStats():

    """
        write as table
    """
    table = []
    standings = statsapi.standings_data(season=SEASON)
    # st.write(standings)
    # """
        # standings -> {
        #     div_id
        #     teams [
        #         team_data_dict
        #     ]
        # }
         
    # """
    teamStandingDict = {}
    for div_id,div_dict in standings.items():
        # st.write(div_dict)
        for team_dict in div_dict['teams']:
            # st.write(team_dict)
            teamStandingDict[team_dict['team_id']] = team_dict
        
    # st.write(teamStandingDict) 
    for id,d in teamIdsDict.items():
        name = d['name']
        # id = d['id']

        # st.write(name,id)
        # print(type(id))
        teamStanding = teamStandingDict[int(id)]
        
        hittingStats = get_stats('hitting',['hits','rbi','gamesPlayed'],id)
        pitchingStats = get_stats('pitching',['hits','runs'],id)

        # st.write(pitchingStats,'putamadre')
        # winsLosses = get_stats('pitching',['wins','losses'],id)
        
        table.append([int(teamStanding['sport_rank'])] + 
                     [name] + 
                     [  teamStanding['w'],
                         teamStanding['l']] +
                     hittingStats + 
                     pitchingStats
                     )

    columns = ["Rank","team","wins","losses" ,"hits","rbi","gamesPlayed","hits allowed","runs allowed"]

    df = pd.DataFrame(data=table,columns=columns)
    st.dataframe(df,hide_index=True)

showTeamsWithStats()
# leagueLeaderTypes = statsapi.meta('leagueLeaderTypes')
# st.selectbox(
#     "League Leader Types",
#      leagueLeaderTypes,
#      key='leagueLeaderTypes',
#      format_func=lambda x: x['displayName'].title()
# )
"""
`{t["w"]}`

logo_api
"""

def logoUrl(teamId):
    return LOGO_API_URL + f"/{teamId}.svg"
LOGO_API_URL= "https://www.mlbstatic.com/team-logos/team-cap-on-dark"



@st.cache_data
def gamesToday(team_id,date):
    result = statsapi.schedule(start_date=date,
                  end_date=date,
                  team=team_id)
    if result == []:
        return [[]]
    return result
"""
    get the games today for this team

    stats only mean something in reference to others
    view all 
"""

# st.write(st.session_state['team'])

#format is mm/dd/yyyy as str

# team_id = st.session_state['team']['id']

st.selectbox(
    "Team",
    list(teamIdsDict.values()),
    key='team',
    format_func=lambda x: x['name']
)

# st.button("Clear Team Cache",
#           on_click=server.clearGamesPlayed,kwargs={
#               'teamId':st.session_state['team']['id'],
#               'season':2025})

#filter to home {
#   hits:[x,x,x,x...]
#   runs:[x,x,x,x...]   
#}

def updateLinescoreHistogram():
    for id,nameData in teamIdsDict.items():
        name = nameData['name']
        st.write(name,id)
        linescoreHistogram = server.getLinescoreHistogram(teamId=id,season=SEASON)

# showGamesPlayed(results)



def updateGamesPlayed():
# st.write(teamIds)
# fetch games played for each team
# and update cache if necessary
    for id,data in teamIdsDict.items():
        # st.write(data)
        name = data['name']
        st.write(name,id)
        server.getGamesPlayed(teamId=id,season=2025)

def removeAllLinescoreHistogramsFromCache():
    with diskcache.Cache(server.CACHE_DIR) as cache:
        #remove histogram from cache
        keys = list(filter(lambda x: 'linescore_histogram' in x,list(cache.iterkeys())))
        st.write('Deleting => ',keys)
        for k in keys:
            cache.pop(k)

# st.write(teamIdsDict)

def showSavedLinescoreHistograms():
    with diskcache.Cache(server.CACHE_DIR) as cache:
        keys = list(filter(lambda x: 'linescore_histogram' in x,list(cache.iterkeys())))
        st.write('Saved Linescore Histograms:',keys)
        # for k in keys:
        #     st.write(k)

# showSavedLinescoreHistograms()
# removeAllLinescoreHistogramsFromCache()
def createLinescoreHistograms():
    for teamId in teamIdsDict:

        teamName = teamIdsDict[teamId]['name']
        st.write(teamName,teamId)

        linescoreHistogram = server.getLinescoreHistogram(teamId=teamId,season=SEASON,teamName=teamName)
        st.write(linescoreHistogram)
        break


# createLinescoreHistograms()
# linescoreHistogram = server.getLinescoreHistogram(teamId=st.session_state['team']['id'],
#                                                   season=SEASON,
#                                                   teamName=st.session_state['team']['name'])
# linescoreHistogram.calculateAverages()

# with diskcache.Cache(server.CACHE_DIR) as cache:
#     cache.set(f'linescore_histogram_{st.session_state["team"]["id"]}_{SEASON}',linescoreHistogram)
# st.write(linescoreHistogram)
"""
    show a bar graph of hits for every inning
"""

# columns = ["hits per inning","runs per inning"]
# df = pd.DataFrame(data={"hits per inning":linescoreHistogram.averages['hits'],
#                         "runs per inning":linescoreHistogram.averages['runs']})
# st.subheader("Total Hits:Total Runs, Per Inning")
# st.bar_chart(data=df,color=["#fd0","#f0f"])
# updateGamesPlayed()

def getLinescores():
    with diskcache.Cache(server.CACHE_DIR) as cache:
        keys = list(filter(lambda x: 'linescore' in x, list(cache.iterkeys())))
        linescores = []
        for k in keys:
            linescores.append(cache.get(k))
        return linescores
    
def showCacheKeys():
    cacheKeys = {}
    with diskcache.Cache(server.CACHE_DIR) as cache:
        keys = list(cache.iterkeys())
        linescoreKeys = filter(lambda x: 'linescore' in x, keys)
        # st.write('Linescore Keys:',list(linescoreKeys))
        cacheKeys['linescores'] = list(linescoreKeys)
        cacheKeys['games_played'] = list(filter(lambda x: 'games_played' in x, keys))
    st.write('Cache Keys:',cacheKeys)

# showCacheKeys()
def removeZeroScoreFilter(gp: dict):

    if  not'home_score' in gp or not 'away_score' in gp:
        print('No score available for game: ',gp['game_id'])
        return False

    a = int(gp['home_score'])
    b = int(gp['away_score'])
    bothZero = a == 0 and b == 0
    if bothZero:
        print('Game with zero score: ',gp['game_id'])
        return False
    return True

# @st.cache_data
def getLinescoreStats(linescore: dict,isHomeTeam: bool):
    hits = 0
    runs = 0
    hits_allowed = 0
    runs_allowed = 0

    myKey = "home" if isHomeTeam else "away"    
    otherKey = "away" if isHomeTeam else "home"

    runs = linescore["teams"][myKey]["runs"]
    hits = linescore["teams"][myKey]["hits"]

    runs_allowed = linescore["teams"][otherKey]["runs"]
    hits_allowed = linescore["teams"][otherKey]["hits"]

    return {"runs":runs,"hits":hits,"runs_allowed":runs_allowed,"hits_allowed":hits_allowed}

def showGamesPlayed(teamId: int):
    result = server.getGamesPlayed(teamId=st.session_state['team']['id'],season=2025)
    # st.write(result)
    result = filter(removeZeroScoreFilter, result)
    columns = ["Result","Opponent","Opponent Score","Scored","hits","runs","hits_allowed","runs_allowed","Date"]
    

    @st.cache_data
    def gls(gameId:int):
        return server.getLinescore(gameId=gameId)
    table = []
    for gp in result:
        
        isHomeTeam = teamId == gp['home_id']

        score = gp['away_score']

        opponentScore = gp['home_score']
        opponentTeam = gp["home_name"]

        awaySuffix = " :blue-background[Away]"
        if isHomeTeam:
            score = gp['home_score']
            opponentTeam = gp["away_name"] 
            opponentScore = gp["away_score"]
            awaySuffix = ""    

        wonGame = False
        if isHomeTeam:
            if gp["home_score"] > gp["away_score"]:
                wonGame = True
        else:
            if gp["away_score"] > gp["home_score"]:
                wonGame = True

        row = {
            # gp['game_id'],
            "Result":(':green-background[W]' if wonGame else ':red-background[L]') + awaySuffix,
            "Opponent":opponentTeam,
            "Opponent Score":int(opponentScore),
            "Scored": int(score),
            "Date": gp['game_date']
        }
        linescore = gls(gp['game_id'])
        # st.write(linescore)
        linescoreStats = getLinescoreStats(linescore,isHomeTeam=isHomeTeam)
        
        #map function? or reduce function?
        table.append(row | linescoreStats)#merge dicts
        # break
    df = pd.DataFrame(data=table,columns=columns)
    st.dataframe(df,hide_index=True)
    # st.table(df)

showGamesPlayed(teamId=st.session_state['team']['id'])
# content = [st.badge("Home", color="blue")]
# st.write(content)

