import streamlit as st

#the following comment magic block will exist in all pages
"""
Streamlit Navigation Notes

    Page source -> Python file or function

    Page label -> Navigation menu label

    Page title -> HTML <title> tag content

    Page URL pathname -> Relative path of the page from root URL

    st.Page -> creates a StreamlitPage object

    st.navigation accepts StreamlitPage objects as args
"""

def functionPage():
    st.header("Some Shit")

page = st.navigation([
    st.Page("home.py"),
    st.Page("about.py"),
    st.Page(functionPage)
    ])

page.run()
