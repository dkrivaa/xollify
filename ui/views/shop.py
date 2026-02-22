import streamlit as st

from backend.app.utilities.general import session_code
from backend.app.services.session_state import (initialize_session_state, clear_main_store,
                                                clear_compare_store)
from backend.app.services.async_runner import run_async
from backend.app.pipeline.fresh_price_promo import (load_stores_price_data,
                                                    load_main_store_promo_data)
from ui.common_elements import logo, selected_stores_element
from ui.common_dialogs import select_store_dialog


def render():
    """ Render the shop page  """
    # Initialize session state variables
    initialize_session_state()

    logo()
    st.subheader('Get :blue[Price and Promo] info while shopping',
                 width='stretch',
                 text_alignment='center')
    st.divider()

    with st.container():
        if st.button(label=':blue[Where are you shopping?]',
                     width='stretch',
                     type='tertiary',
                     key='main_store_button',):
            select_store_dialog(store_type=1)

        st.space()

        if st.button(label=':blue[Stores for price comparison]',
                     width='stretch',
                     type='tertiary',
                     key='other_store_button',
        ):
            select_store_dialog()

    st.space()

    # If main_store is selected, go to item details page
    if 'main_store' in st.session_state and st.session_state['main_store']:
        if st.button(label=':material/info: Get Price and Promo Info', width='stretch',
                     key='go_to_item_details_button', ):
            # Loading store data
            with st.spinner('Loading store data...'):
                run_async(load_stores_price_data)
                run_async(load_main_store_promo_data)
            # Switch page
            st.switch_page('ui/views/item.py')
        st.divider()

    # Display selected stores

    selected_stores_element()


if __name__ == "__main__":
    render()