import os

import pysqlite3
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import streamlit as st
import sqlite3


from st_pages import Page, show_pages, add_page_title

# Optional -- adds the title and icon to the current page
add_page_title("AI Agents")

show_pages(
    [
        Page("graph.py", "Content Creation Team"),
        # Page("other_pages/page2.py", "Page 2", ":books:"),
    ]
)
