import streamlit as st

from backend.app.services.session_state import clear_session_state
from ui.common_elements import logo


def render():
    """ Render the home page with welcome message and instructions. """
    logo()
    st.markdown(
        'The shopping companion that saves '
        '<span style="font-size:24px">time</span> and <span style="font-size:24px">money</span>!!',
        unsafe_allow_html=True)
    st.divider()
    st.space()
    shop = st.button(label=':material/shopping_cart: Price and promo info while shopping',
                     width='stretch',
                     key='shop')
    st.space()
    plan = st.button(label=':material/list: Prepare shopping list and compare prices',
                     width='stretch',
                     key='plan')

    if shop:
        st.switch_page('ui/views/shop.py')

    if plan:
        st.switch_page('ui/views/plan.py')

    st.button('reset session state', on_click=clear_session_state)
    st.write(st.session_state)









if __name__ == "__main__":
    render()