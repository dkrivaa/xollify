import streamlit as st
import pandas as pd

from backend.app.services.shoppinglist_service import read_user_list, convert_for_download
from backend.app.pipeline.fresh_price_promo import shoppinglist_page_data
from backend.app.utilities.general import get_chain_from_code
from ui.common_elements import logo, plan_header, item_selector


def check_page_ready():
    """ Check that data for selected stores is available"""
    key = next(iter(st.session_state['main_store'].keys()))
    if not st.session_state.get(key):
        # Loading store data
        with st.spinner('Loading store data...'):
            shoppinglist_page_data()


def render():
    """ Render the shoppinglist page with shopping list input """
    check_page_ready()

    # Initialize shopping list in session state if not already present
    if 'shopping_list' not in st.session_state:
        st.session_state['shopping_list'] = {}
    # The items_list contains the items to be added to the shopping list after checking availability in stores.
    if 'items_list' not in st.session_state:
        st.session_state['items_list'] = []

    # Display logo and header for Plan section
    logo()
    plan_header()
    st.divider()

    tab1, tab2, tab3 = st.tabs([":green[Upload Shopping List]",
                                ":green[Make / Add to Shopping List]",
                                ":green[See Items in List]"])

    with tab1:
        # Upload shopping list
        st.space()
        user_list = st.file_uploader("Upload your shopping list (CSV or Excel)",
                                     type=['csv', 'xlsx'])

        if user_list:
            st.session_state['items_list'] = read_user_list(user_list)

    with tab2:
        # Make / Add items to shopping list
        # Get main store session key (chain_code + store_code) to access price and promo data
        main_session_key = next(iter(st.session_state.get('main_store').keys()))
        # Get price data for main store from session state
        price_data = st.session_state.get(main_session_key)

        # Make form for adding items to shopping list
        with st.form(key='add_item_form', clear_on_submit=True):
            # Populate item selector with items from price data
            item = item_selector(price_data)
            quantity = st.number_input("Quantity (items/Kg)", min_value=0.5, value=1.0, step=0.5)
            if st.form_submit_button(label='Add', icon=":material/add_shopping_cart:", icon_position="left"):
                if item:
                    # Get item details from price data of any store where available
                    item_dict = next(d for d in price_data if d['ItemCode'] == item) if price_data else None
                    if item_dict:
                        item_name = item_dict['ItemName'] or item_dict['ItemNm']
                        # Add item and quantity to shopping list in session state
                        st.session_state['items_list'].append(
                            {'Item Code': item, 'Product Name': item_name, 'Quantity': quantity})

    with tab3:
        # See items in list
        with st.expander("Items in your shopping list"):

            # Add Delete checkbox to each item
            items_with_delete = [{'Delete': False, **item} for item in st.session_state['items_list']]

            # Data editor
            edited = st.data_editor(
                data=items_with_delete,
                hide_index=True,
                column_config={
                    'Delete': st.column_config.CheckboxColumn("🗑️", default=False, width="small"),
                    'Item Code': st.column_config.TextColumn("Item Code", disabled=True),
                    'Product Name': st.column_config.TextColumn("Product Name", disabled=True),
                    'Quantity': st.column_config.NumberColumn("Quantity", format="%g", step=0.5)
                },
                key='items_list_editor'
            )

            # Always update quantities (before potential deletion)
            st.session_state['items_list'] = [
                {k: v for k, v in item.items() if k != 'Delete'}
                for item in edited
                if not item['Delete']
            ]

            # Delete button (will trigger rerun, which updates quantities)
            if st.button("🗑️ Delete Selected"):
                st.rerun()

            # Enable download button of list as CSV
            if len(st.session_state['items_list']) > 0:
                df = pd.DataFrame(st.session_state['items_list'])
                csv = convert_for_download(df)

                st.download_button(
                    label="Download Shopping list as CSV",
                    data=csv,
                    file_name="shoppinglist.csv",
                    mime="text/csv",
                    icon=":material/download:",
                    key='download_button',
                    type='tertiary'
                )

    # Compare prices button - only enabled if there are items in the items list
    if st.session_state.get('items_list') is not None and len(st.session_state['items_list']) > 0:
        if st.button(label='Compare Prices', width='stretch', key='compare_prices_button',
                     help='Compare prices for items in your shopping list across selected stores '
                          'and get optimized shopping list based on prices at those stores.',
                     icon=":material/compare_arrows:", icon_position="left", ):
            # Flag to make / remake shoppinglists - Used when user adds items
            st.session_state['make_new_shoppinglists'] = True
            st.switch_page('ui/views/compare.py')





if __name__ == "__main__":
    render()