import streamlit as st
import statsapi
import json
from datetime import datetime

SEASON ="2025"
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

today = datetime.today()
today_str = today.strftime("%m/%d/%Y")

@st.cache_data
def gamesToday(team_id,date):
    return statsapi.schedule(start_date=date,
                  end_date=date,
                  team=team_id)
"""
    get the games today for this team
"""

# st.write(st.session_state['team'])

#format is mm/dd/yyyy as str

team_id = st.session_state['team']['id']

current,other = st.columns(2)

result = gamesToday(st.session_state['team']['id'],today_str)[0]
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

current.write(current_teamName)
other.write(other_teamName)

standings = statsapi.standings_data(season='2025')
#returns map split by division
#div_id : {
#   div_name:
#   team_id_0: data,
#   team_id_1: data,
#   ...
#}
st.write(standings)
for div_id,div_data in standings.items():
    # st.write(d)
    div_name = div_data['div_name']
    table = []
    # st.write(div_name)
    for team_dict in div_data['teams']:
        row = {}
        if team_dict['team_id'] == team_id:
            # row['team_id'] = t['team_id']
            row['name']= team_dict['name']
            row['wins'] = f'`{team_dict["w"]}`'
            row['losses'] = team_dict['l']
            table.append(row)
            st.table(table)
