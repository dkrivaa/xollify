import streamlit as st

from backend.app.utilities.general import get_chain_from_code
from ui.common_elements import logo, item_selector, price_element, promo_element


def render():
    """ Render the item page with item details and price comparison. """
    logo()
    st.subheader("Item Details")
    st.write("Here you can see the details of the selected item and compare prices across selected stores.")
    st.divider()

    # Get main store session key (chain_code + store_code) to access price and promo data
    main_session_key = next(iter(st.session_state.get('main_store').keys()))
    # Get chain object matching given chain code
    chain_code = st.session_state.get('main_store')[main_session_key]['chain_code']
    chain_alias = st.session_state.get('main_store')[main_session_key]['chain_alias']
    store_name = st.session_state.get('main_store')[main_session_key]['store_name']
    chain = get_chain_from_code(chain_code)
    # Get price data for main store from session state
    price_data = st.session_state.get(main_session_key)
    # Populate item selector with items from price data
    item = item_selector(price_data)

    if item:
        # Get price details for item from price data
        main_item_details = chain.get_shopping_prices(price_data=st.session_state.get(main_session_key),
                                                      shoppinglist=[item]) if st.session_state.get(main_session_key) else None
        # Get relevant promo blacklist for the chain
        blacklist = chain.promo_blacklist() if chain else set()
        # Get promo details for item from promo data
        item_promos = chain.get_shopping_promos(promo_data=st.session_state.get(f'{main_session_key}_promo_data'),
                                                shoppinglist=[item],
                                                blacklist=blacklist) if st.session_state.get(main_session_key) else None

        # Show price
        st.subheader('Price')
        price_element(item, main_item_details, chain_alias, store_name)

        for key in st.session_state['compare_store'].keys():
            # Get chain object matching given chain code
            chain_code = st.session_state['compare_store'][key]['chain_code']
            chain_alias = st.session_state['compare_store'][key]['chain_alias']
            store_name = st.session_state['compare_store'][key]['store_name']
            compare_chain = get_chain_from_code(chain_code)
            # Get price details for item from price data
            compare_item_details = compare_chain.get_shopping_prices(price_data=st.session_state.get(key),
                                                                     shoppinglist=[item]) if st.session_state.get(key) else None
            # Show price comparison
            price_element(item, compare_item_details, chain_alias, store_name)

        # Show promotions
        if item_promos:
            with st.expander("Promotions"):
                st.subheader('Promotions')
                if item_promos and item_promos.get(item):
                    for promo in item_promos[item]:
                        promo_element(chain, promo)
        else:
            st.info("No promotions available for this product at the moment.")








if __name__ == "__main__":
    render()