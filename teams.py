import streamlit as st
import statsapi
import json
from datetime import datetime
import pandas as pd
import numpy as np
import server

import diskcache
import altair as alt

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
teamNames = [team['name'] for team in teamIdsDict.values()]
st.session_state["teamNames"] = teamNames
# st.write(teamIdsDict)
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


def pitchingData():
    testGameId = 777308
    """
        Get pitching data for a game
    """
    boxscoreData = statsapi.boxscore_data(gamePk=testGameId)
    st.write(boxscoreData)

# pitchingData()

showTeamsWithStats()

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
        # cacheKeys['linescores'] = list(linescoreKeys)
        # cacheKeys['games_played'] = list(filter(lambda x: 'games_played' in x, keys))
        # cacheKeys['game_data'] = list(filter(lambda x: 'game_data' in x,keys))
        cacheKeys['teamGameContainers']  = list(filter(lambda x:'team_game_container' in x,keys))
    st.write('Cache Keys:',cacheKeys)



# showCacheKeys()
# tgd = "team_game_container_108_2025"
# with diskcache.Cache(server.CACHE_DIR) as cache:
#     st.write(cache[tgd])

@st.cache_data
def getCacheLinescore(gameId:int):
    with diskcache.Cache(server.CACHE_DIR) as cache:
        key = f'linescore_{gameId}'
        if key in cache:
            return cache.get(key)
        else:
            print('No linescore found for game:',gameId)
            return None

def removeCacheLinescore(gameId:int):
    with diskcache.Cache(server.CACHE_DIR) as cache:
        key = f'linescore_{gameId}'
        if key not in cache:
            print('No linescore found for game:',gameId)
            return 
        cache.pop(key,None)

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

    if "runs" not in linescore["teams"][myKey] or "hits" not in linescore["teams"][myKey]:
        print('No runs or hits in linescore for team:',myKey)
        print(json.dumps(linescore, indent=4))
        return

    runs = linescore["teams"][myKey]["runs"]
    hits = linescore["teams"][myKey]["hits"]

    runs_allowed = linescore["teams"][otherKey]["runs"]
    hits_allowed = linescore["teams"][otherKey]["hits"]

    return {"runs":runs,"hits":hits,"runs_allowed":runs_allowed,"hits_allowed":hits_allowed}

    
custom_colors = [
    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b',
    '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
    '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5',
    '#c49c94', '#f7b6d2', '#c7c7c7', '#dbdb8d', '#9edae5',
    '#393b79', '#637939', '#8c6d31', '#843c39', '#7b4173',
    '#5254a3', '#6b6ecf', '#9c9ede', '#17becf', '#e7ba52'
]

@st.fragment
def showGraph(df: pd.DataFrame):
    options = ["sort","date" ,"team"]
    #option
    selection = st.pills(
        "Graph Sort",
        default=options[0],
        options=options,
        selection_mode="single",
        format_func= lambda x : x.title(),
        key="sortGraph"
    )
    #do what show hits for now 
    #the extra bracket wraps are necessary so i can split calls into multiple lines
    xDateAxis = alt.X("Date:N")
    if st.session_state["sortGraph"] == "sort":
        xDateAxis = alt.X("Date:N",sort="-y")
    elif st.session_state["sortGraph"] == "team":
        xDateAxis = alt.X("Date:N",sort=alt.SortField(
            field="Opponent",
            order="descending"
        ))

    hits_allowed_bar = (
        alt.Chart(df)
        .mark_bar(width=7)
        .encode(
            xDateAxis,
            alt.Y("hits_allowed:Q"),
            color = alt.Color(
            'Opponent:N',
             scale=alt.Scale(
                domain=teamNames,
                range=custom_colors
                )  
            )
        )
    )

    avg_ha_line = (
        alt.Chart(df)
        .mark_rule(color="cyan", strokeDash=[5, 5], strokeWidth=2)
        .encode(y='mean(hits_allowed):Q')
    )


    hits_bar = (
        alt.Chart(df)
        .mark_bar(width=7)
        .encode(
            xDateAxis, 
            alt.Y("hits:Q"),
            color = alt.Color(
            'Opponent:N',
             scale=alt.Scale(
                domain=teamNames,
                range=custom_colors
            )  
            )
        )
    )

    avg_line = (
        alt.Chart(df)
        .mark_rule(color="cyan", strokeDash=[5, 5], strokeWidth=2)
        .encode(y='mean(hits):Q')
    )

    st.altair_chart(avg_line + hits_bar, use_container_width=True)           
    st.altair_chart(avg_ha_line + hits_allowed_bar, use_container_width=True)           


@st.fragment
def showTable(df: pd.DataFrame):
    options = ["table","dataframe"]
    #option
    selection = st.pills(
        "Table Type",
        default=options[0],
        options=options,
        selection_mode="single",
        format_func= lambda x : x.title(),
        key="tableType"
    )

    if st.session_state['tableType'] == "table":
        st.table(df)
    else:
        st.dataframe(df,hide_index=True)

@st.fragment
def showGamesPlayed(teamId: int):
    result = server.getGamesPlayed(teamId=st.session_state['team']['id'],season=2025)
    # st.write(result)
    result = filter(server.gamePlayedFilter, result)
    columns = ["Result","Opponent","Opponent Score","Scored","hits","runs","hits_allowed","runs_allowed","Date","isHomeGame"]
    

    @st.cache_data
    def gls(gameId:int):
        return server.getLinescore(gameId=gameId)
    table = []
    for gp in result:
        
        isHomeTeam = teamId == gp['home_id']

        score = gp['away_score']

        opponentScore = gp['home_score']
        opponentTeam = gp["home_name"]
        opponentId = gp['home_id']

        awaySuffix = " :blue-background[Away]"
        if isHomeTeam:
            score = gp['home_score']
            
            opponentId = gp['away_id']
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
            "isHomeGame": "Home" if isHomeTeam else "Away",
            "Result":(':green-background[W]' if wonGame else ':red-background[L]') + awaySuffix,
            "Opponent":opponentTeam,
            "Opponent Score":int(opponentScore),
            "Scored": int(score),
            "Date": gp['game_date']
        }
        if score == 0 and opponentScore == 0:
            continue
        linescore = gls(gp['game_id'])
        # st.write(linescore)
        linescoreStats = getLinescoreStats(linescore,isHomeTeam=isHomeTeam)
        if linescoreStats is None:
            
            print('No linescore stats for game:',gp['game_id'])
            continue
        #map function? or reduce function?
        table.append(row | linescoreStats)#merge dicts
        # break
    df = pd.DataFrame(data=table,columns=columns)
    showGraph(df)
    showTable(df)
    # st.dataframe(df,hide_index=True)
    # st.table(df)

showGamesPlayed(teamId=st.session_state['team']['id'])

# server.aggregateGameDataAndLinescore()
server.addDatesToTGC()
# server.clearTGC2()
