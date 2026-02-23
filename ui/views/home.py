import streamlit as st

from backend.app.services.session_state import initialize_session_state
from backend.app.services.async_runner import run_async
from backend.app.pipeline.fresh_price_promo import (item_page_data, load_stores_price_data,
                                                    load_main_store_promo_data)
from backend.app.services.session_state import clear_session_state
from ui.common_elements import logo, selected_stores_element
from ui.common_dialogs import select_store_dialog


def select_stores(label: str):
    """ Select "home" and "compare" stores"""
    with st.container():
        if st.button(label=f'{label}',
                     width='stretch',
                     type='tertiary',
                     icon=':material/store:',
                     icon_position='left',
                     key='main_store_button', ):
            select_store_dialog(store_type=1)

        if st.button(label='Stores for price comparison',
                     width='stretch',
                     type='tertiary',
                     icon=':material/add_business:',
                     icon_position='left',
                     key='other_store_button'):
            select_store_dialog()


def render():
    """ Render the home page with general selection. """
    # Initialize session state variables
    initialize_session_state()

    logo()
    st.subheader(body=':grey[Optimize Shopping and Save MONEY!!]',
                 width='stretch',
                 text_alignment='center')
    st.divider()

    # Reset all session_state
    if st.button(label=':grey[Reset all]', icon=':material/clear_all:', icon_position='left', key='reset_button',
                 type='tertiary', on_click=clear_session_state):
        st.rerun()

    with st.container():
        # Select SHOP or PLAN
        option_maps = {
            1: ':material/shopping_cart: SHOP',
            2: ':material/list: PLAN'
        }

        # Select what to do - SHOP or PLAN
        option = st.pills(label='Select what to do',
                          label_visibility='hidden',
                          options=option_maps.keys(),
                          format_func=lambda x: option_maps[x],
                          width='stretch',
                          default=None,
                          key='option_key')

        col1, col2 = st.columns(2)

        # If SHOP
        with col1:
            if option == 1:
                st.space()
                # Display select stores element
                select_stores('Where are you shopping?')

                # Display selected stores
                selected_stores_element(label='Shopping at')

                st.divider()

                # If main_store is selected, go to item details page
                if 'main_store' in st.session_state and st.session_state['main_store']:
                    if st.button(label=':material/info: :green[Get Price and Promo Info]',
                                 width='stretch',
                                 key='go_to_item_details_button', ):
                        # Loading store data
                        with st.spinner('Loading store data...'):
                            item_page_data()
                        # Switch page
                        st.switch_page('ui/views/item.py')

        # If PLAN
        with col2:
            if option == 2:
                st.space()
                select_stores('Select "Home Store"')

                # Display selected stores
                selected_stores_element(label="'Home Store'")

                st.divider()

                with st.container():
                    # If main_store is selected, go to shoppinglist page
                    if 'main_store' in st.session_state and st.session_state['main_store']:
                        if st.button(label=':green[Make Shopping List]', width='stretch',
                                     icon=":material/list:", icon_position="left", ):
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
                                    if 'load_errors' in st.session_state:
                                        del st.session_state['load_errors']


if __name__ == "__main__":
    render()