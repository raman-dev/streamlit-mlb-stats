import streamlit as st
import statsapi
import json
from datetime import datetime
import pandas as pd
import numpy as np
import server

SEASON ="2025"

today = datetime.today()
today_str = today.strftime("%m/%d/%Y")

@st.cache_data
def getTeams():
    return statsapi.get("teams",params={'sportIds':1,'activeStatus':'Yes'})


@st.cache_data
def getTeamIds():
    #read from file if exists
    teams = None
    try:
        with open('team_ids.json','r') as f:
            teams = json.load(f)
    except FileNotFoundError:
        print('creating team_ids file')
        teams = writeTeamIds()
    
    return teams

def writeTeamIds():
    
    # with open('team_ids.json') as f:
    #     f.write()
    result = getTeams()
    teams = []
    for team_data_map in result['teams']:
        # for x in team_data:
        #     st.write(x)
        # st.write(team_data_map['name'],team_data_map['id'])
        teams.append({'id':team_data_map['id'],'name': team_data_map['name']})

    # st.write(teams)
    with open('team_ids.json','w+') as f:
        f.write(json.dumps(teams))
    
    return teams

teamIds = getTeamIds()

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
    standings = statsapi.standings_data(season='2025')
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
    for d in teamIds:
        name = d['name']
        id = d['id']

        
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
    teamIds,
    key='team',
    format_func=lambda x: x['name']
)

results = server.getGamesPlayed(teamId=st.session_state['team']['id'],
                                season=2025)
# results = statsapi.schedule(team=st.session_state['team']['id'],
#                             season=2025,
#                             end_date=today_str,
#                             start_date='03/19/2025')

# st.button("Clear Team Cache",
#           on_click=server.clearGamesPlayed,kwargs={
#               'teamId':st.session_state['team']['id'],
#               'season':2025})
testGameId = 777917
testHomeId = 133
testAwayId = 119
def gamesPlayed(results):
    data = []
    global testGameId
    for game in results:
        id = game['game_id']
        home_id = game['home_id']
        away_id = game['away_id']
        date = game['game_date']
        home = game['home_name']
        away = game['away_name']
        away_runs = game['away_score']
        home_runs = game['home_score']
    
    # x = statsapi.get("game_linescore",params={
    #     'gamePk':id
    # })
        

    # """
    # break
        data.append([
            id,date,home,home_id,away,away_id,away_runs,home_runs
        ])
    #grab hits at bats walks

    st.table(data)


@st.cache_data
def getLinescore(gameId):
    return statsapi.get("game_linescore",params={
    'gamePk':gameId
    })

linescore = getLinescore(testGameId)
st.write(linescore)
linescoreHistogram = server.LinescoreHistogram(teamId=st.session_state['team']['id'],teamName="Athletics")
linescoreHistogram.addLinescore(linescore=linescore,homeId=testHomeId)
st.write(linescoreHistogram)
#filter to home {
#   hits:[x,x,x,x...]
#   runs:[x,x,x,x...]   
#}


# gamesPlayed(results)

"""
    show a bar graph of hits for every inning

"""

# columns = ["hits per inning","runs per inning"]
# hits = [2,4,6,7,12,4,2,1,0.5]
# runs = [4,3,1,3,5,6,8,9,1]

# df = pd.DataFrame(data={"hits per inning":hits,"runs per inning":runs})
# st.subheader("Hits/Runs Per Inning")
# st.bar_chart(data=df,color=["#fd0","#f0f"])