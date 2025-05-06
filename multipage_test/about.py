import streamlit as st

#write to some other key not used anywhere else in page 
slider_key = "about_slider"
# dummy_key = "_" + slider_key

# if slider_key in st.session_state:
#     st.session_state.about_slider = st.session_state.about_slider

# def store():
#     st.session_state[dummy_key] = st.session_state[slider_key]

# def load():
#     st.session_state[slider_key] = st.session_state[dummy_key]

# load()
st.slider("about slider",key=slider_key)#,on_change=store)

st.write("slider: ",st.session_state[slider_key])


