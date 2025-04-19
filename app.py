import streamlit as st
import statsapi
import json

# st.write("hello")
# st.write(statsapi.boxscore(565997))
result = None
# result = statsapi.get("schedule", {"startDate": "2023-03-30", "endDate": "2023-03-31"})
# result = statsapi.schedule(start_date="2023-06-01",end_date="2023-06-07")

# data = {
#     'game_id':717942
# }
# st.write(result)

# st.write(statsapi.schedule(**data))
# result = statsapi.boxscore_data(gamePk=data['game_id'])

# st.write(result)
"""
    what is the purpose of this?
    why build this?
    
        need to know what to bet and when

        baseball is a volume game

        teams play a lot of games

        need to understand which numbers are consistent enough to bet on

    how to understand pitching?

        - pitcher play is typically independent from the entire team
        - doesn't matter what team pitcher is on
        - pitcher vs batters 
            strikeout rates?
            how often has a pitcher faced batter x
            how often a pitcher has faced team x
                performance strikes/balls/strikeouts
                
"""

@st.cache_data
def getTeams():
    return statsapi.get("teams",params={'sportIds':1,'activeStatus':'Yes'})


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

st.write(st.session_state['team'])


