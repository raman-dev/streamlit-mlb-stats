import streamlit as st
import statsapi
import json
from datetime import datetime
import pandas as pd

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

st.selectbox(
    "Team",
    teamIds,
    key='team',
    format_func=lambda x: x['name']
)

# leagueLeaderTypes = statsapi.meta('leagueLeaderTypes')
# st.selectbox(
#     "League Leader Types",
#      leagueLeaderTypes,
#      key='leagueLeaderTypes',
#      format_func=lambda x: x['displayName'].title()
# )


@st.cache_data
def get_stats(statGroup,statNames):
    statDict = statsapi.get("team_stats",
                      params={
                          'season':SEASON,
                          'stats':'season',
                          'teamId':st.session_state['team']['id'],
                          'group':statGroup})['stats'][0]['splits'][0]['stat']
    return [ statDict[x] for x in statNames ]


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
"""

# st.write(st.session_state['team'])

#format is mm/dd/yyyy as str

team_id = st.session_state['team']['id']
# st.write(statsapi.team_leader_data(teamId=team_id,
#                           leaderCategories=st.session_state['leagueLeaderTypes']['displayName'],
#                           season=SEASON
#                           ))

current,other = st.columns(2)

result = gamesToday(st.session_state['team']['id'],today_str)[0]

if result != []:
    """
        grab team names 
    """
    current_teamName = result['home_name']
    other_teamName = result['away_name']
    other_teamId = result['away_id']
    if result['home_id'] != team_id:
        #current team is not home team
        current_teamName = result['away_name']
        other_teamName = result['home_name']
        other_teamId = result['home_id']

    # current.write(current_teamName)
    # other.write(other_teamName)
    st.header(current_teamName)
    
    columns = ["Hits Allowed","Runs Allowed","RBIs","Hits","Games Played"]

    hittingStats = get_stats('hitting',['hits','rbi','gamesPlayed'])
    pitchingStats = get_stats('pitching',['hits','runs'])
    winsLosses = get_stats('pitching',['wins','losses'])
    
    st.write(winsLosses)
    data = [pitchingStats + hittingStats]
    df = pd.DataFrame(data=data,columns=columns)
    df_t = df.T.copy()
    df_t.columns = ["Value"]
    st.dataframe(df_t)
    # st.dataframe(df,hide_index=True)
    
    # """
    #     statGroups:
    #         hitting
    #             hits,atBats,rbis
    #         pitching
    #             hits, numberOfPitches
    #         fielding
    # """
    st.header(other_teamName)
    # standings = statsapi.standings_data(season='2025')
    #returns map split by division
    #div_id : {
    #   div_name:
    #   team_id_0: data,
    #   team_id_1: data,
    #   ...
    # #}
    # st.write(standings)
    # for div_id,div_data in standings.items():
    #     # st.write(d)
    #     div_name = div_data['div_name']
    #     table = []
    #     # st.write(div_name)
    #     for team_dict in div_data['teams']:
    #         row = {}
    #         if team_dict['team_id'] == team_id:
    #             # row['team_id'] = t['team_id']
    #             row['name']= team_dict['name']
    #             row['wins'] = f'`{team_dict["w"]}`'
    #             row['losses'] = team_dict['l']
    #             table.append(row)
    #             st.table(table)
else:
    st.write("No games today")