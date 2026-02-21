import streamlit as st

from backend.app.services.session_state import (initialize_session_state, clear_main_store,
                                                clear_compare_store)
from backend.app.services.async_runner import run_async
from backend.app.pipeline.fresh_price_promo import (load_stores_price_data)
from ui.common_dialogs import select_store_dialog
from ui.common_elements import logo, plan_header, selected_stores_element


def render():
    """ Render the plan page with shopping list input and price comparison. """
    # Initialize session state variables
    initialize_session_state()

    # Display logo and header for Plan section
    logo()
    plan_header()
    st.divider()

    with st.container():
        if st.button(label=':blue[Select "Home Store"]',
                     width='stretch',
                     type='tertiary',
                     key='main_store_button',
                     help='Select the store you usually shop at. '
                          'This will be used as the main store for price comparison and shopping list optimization.'
                     ):
            select_store_dialog(store_type=1)

        st.space()

        if st.button(label=':blue[Select stores for price comparison]',
                     width='stretch',
                     type='tertiary',
                     key='other_store_button',
                     help='Select one or more stores for price comparison. '
                          'You can select stores from different supermarket chains. '
                          'Select nearby stores to get optimized shopping list based on prices at those stores. ',

                     ):
            select_store_dialog()

        st.space()
        # Display selected stores
        selected_stores_element()

    with st.container():
        # If main_store is selected, go to shoppinglist page
        if 'main_store' in st.session_state and st.session_state['main_store']:
            if st.button(label=':green[Make Shopping List]', width='stretch',
                         icon=":material/list:", icon_position="left",):
                try:
                    # Loading store data
                    with st.spinner('Loading store data...'):
                        run_async(load_stores_price_data)
                    # Switch page
                    st.switch_page('ui/views/shoppinglist.py')
                except Exception as e:
                    if 'load_errors' in st.session_state:
                        for err in st.session_state['load_errors']:
                            st.warning(err)


if __name__ == "__main__":
    render()