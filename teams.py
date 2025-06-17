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

        
        teamStanding = teamStandingDict[id]
        
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

"""



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

showSavedLinescoreHistograms()
# removeAllLinescoreHistogramsFromCache()
def createLinescoreHistograms():
    for teamId in teamIdsDict:

        teamName = teamIdsDict[teamId]['name']
        st.write(teamName,teamId)

        linescoreHistogram = server.getLinescoreHistogram(teamId=teamId,season=SEASON,teamName=teamName)
        st.write(linescoreHistogram)
        break


# createLinescoreHistograms()
linescoreHistogram = server.getLinescoreHistogram(teamId=st.session_state['team']['id'],
                                                  season=SEASON,
                                                  teamName=st.session_state['team']['name'])
linescoreHistogram.calculateAverages()

with diskcache.Cache(server.CACHE_DIR) as cache:
    cache.set(f'linescore_histogram_{st.session_state["team"]["id"]}_{SEASON}',linescoreHistogram)
st.write(linescoreHistogram)
"""
    show a bar graph of hits for every inning
"""

columns = ["hits per inning","runs per inning"]
df = pd.DataFrame(data={"hits per inning":linescoreHistogram.averages['hits'],
                        "runs per inning":linescoreHistogram.averages['runs']})
st.subheader("Total Hits:Total Runs, Per Inning")
st.bar_chart(data=df,color=["#fd0","#f0f"])


