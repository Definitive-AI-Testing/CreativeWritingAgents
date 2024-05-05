from pathlib import Path

import streamlit as st
from st_pages import Page, show_pages, add_page_title

#with st.echo("below"):
"## Declaring the pages in your app:"

show_pages(
    [
        Page("main.py", "Home", "🏠"),
        Page("graph.py", "Content Creation Team"),
    ]
)

add_page_title()  # Optional method to add title and icon to current page
