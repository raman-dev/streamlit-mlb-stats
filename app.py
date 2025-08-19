import streamlit as st
import statsapi
import json


page = st.navigation([
    st.Page("teams.py"),
    st.Page("notes.py",title="Notes"),
    st.Page("cache_viewer.py", title="Cache Viewer", icon="📊")
    ])
page.run()