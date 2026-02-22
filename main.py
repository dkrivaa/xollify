# For streamlit cloud
import subprocess
subprocess.run(["playwright", "install", "chromium"], check=True)

# For streamlit on local
import sys
import asyncio
# Fix for Windows + Playwright
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import streamlit as st


# Startup code to run the app
# Initialize all chains
from backend.app.bootstrap import initialize_backend
initialize_backend()

# st.set_page_config - Set the configuration of the Streamlit page
st.set_page_config(
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. CSS across app
st.markdown("""
<style>
    @media (max-width: 768px) {
        .block-container {padding: 1rem;}
        .stButton > button {width: 100%;}
    }
</style>
""", unsafe_allow_html=True)

# Define pages
home_page = st.Page(
    title='HOME',
    page='ui/views/home.py',
    icon=":material/home:",
    default=True
)

shop_page = st.Page(
    title='Select Store',
    page='ui/views/shop.py',
    icon=":material/shopping_cart:",
)

plan_page = st.Page(
    title='Select Stores',
    page='ui/views/plan.py',
    icon=":material/list:",
)

item_page = st.Page(
    title='Item Info',
    page='ui/views/item.py',
    icon=":material/barcode:",
)

shoppinglist_page = st.Page(
    title='Shopping List',
    page='ui/views/shoppinglist.py',
    icon=":material/list_alt:",
)

compare_page = st.Page(
    title='Compare & Optimize',
    page='ui/views/compare.py',
    icon=":material/compare_arrows:",
)

pages = {
    '': [home_page, ],
    'SHOP': [shop_page, item_page, ],
    'PLAN': [plan_page, shoppinglist_page, compare_page]
}

pg = st.navigation(pages=pages, position='top')
pg.run()
