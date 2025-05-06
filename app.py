import streamlit as st
import statsapi
import json


page = st.navigation([
    st.Page("teams.py"),
    st.Page("notes.py",title="Notes")
    ])
page.run()