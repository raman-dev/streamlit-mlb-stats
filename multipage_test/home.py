import streamlit as st



st.header("Home")
st.slider("home slider",key="home_slider")

st.write('slider:',st.session_state["home_slider"])