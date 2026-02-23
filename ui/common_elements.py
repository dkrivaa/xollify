import streamlit as st

from backend.app.core.super_class import SupermarketChain
from backend.app.utilities.general import get_chain_from_code, session_code
from backend.app.services.async_runner import run_async
from backend.app.services.db_service import get_stores_for_chain
from backend.app.services.session_state import (initialize_session_state, clear_main_store,
                                                clear_compare_store)


def logo():
    """ Display the app logo. """
    return st.title(':orange[:material/attach_money: Xollify]',
                    width='stretch',
                    text_alignment='center')


def plan_header():
    """ Display the header for the shopping plan section. """
    st.subheader('Plan Your Shopping',
                 width='stretch',
                 text_alignment='center')


def chain_selector():
    """ Chain selector dropdown """
    # Get all registered supermarket chains
    chains = SupermarketChain.registry
    # Make dict with chain_code as key and alias as value
    code_to_alias = {c.chain_code: c.alias for c in chains}
    # Sort the chain codes by their alias
    sorted_codes = sorted(code_to_alias.keys(), key=lambda x: code_to_alias[x])

    chain = st.selectbox(
        label=f':material/search: Supermarket Chain',
        options=sorted_codes,  # Use sorted list instead of list(code_to_alias)
        format_func=lambda x: code_to_alias[x].capitalize(),
        index=None,
        placeholder='Select Chain',
        key='chain_selector'
    )

    chain_alias = next(c.alias for c in chains if c.chain_code == chain) if chain else None
    # Return chain_code of selected chain
    return chain, chain_alias


@st.cache_data(show_spinner='Getting stores for selected chain...', )
def chain_stores(chain):
    # Wrapper function to get stores for chain with caching
    return run_async(get_stores_for_chain, chain=chain)


def store_selector(chain_code):
    """ Gets stores for chain defined by chain_code """
    # Get chain object matching given chain code
    chain = get_chain_from_code(chain_code)
    # Get stores for chain
    stores = chain_stores(chain)

    # Make selectBox to select store
    store = st.selectbox(
        label=f':material/search: Store',
        placeholder='Select Store',
        options=sorted([s['store_code'] for s in stores], key=lambda x: int(x)),
        format_func=lambda x: f'{x} - {next(s['store_name'] for s in stores if s['store_code'] == x)}',
        index=None,
        key='store_selector'
    )

    store_name = next(s['store_name'] for s in stores if s['store_code'] == store) if store else None

    # Return store_code for selected store
    return store, store_name


def item_selector(price_data, label: str = 'Item', session_key: str = None):
    # Remove items that are left in items list
    if session_key:
        # The items codes that cannot be used for alternative item (items still left in items_list_{session_key} or already used item codes for items in shopping list:
        items_codes_left = list({
                                    d['Item Code'] for d in st.session_state[f'items_list_{session_key}']
                                } | {
                                    d['Item Code'] for d in st.session_state['shopping_list'].get(session_key, [])
                                })
        options = [d['ItemCode'] for d in price_data if d['ItemCode'] not in items_codes_left]
    else:
        options = [d['ItemCode'] for d in price_data]

    item = st.selectbox(
        label=f':material/search: {label}',
        placeholder='Select Item',
        options=sorted(options, key=int),
        format_func=lambda x: f"{x} - {next(d.get('ItemName') or d.get('ItemNm') for d in price_data
                                            if d['ItemCode'] == x)}",
        index=None,
        key='item_selector'
    )

    return item


def price_element(item: str, item_details: dict, chain_alias: str, store_name: str):
    """ Renders a single price element for the given item """
    st.metric(
        label=f"{chain_alias} - {store_name}",
        label_visibility='visible',
        value=(
            f"₪ {item_details[item]['ItemPrice']}"
            if item_details and item_details.get(item)
            else "N/A"
        ),
    )

    st.divider()


def promo_element(chain: SupermarketChain, promo: dict):
    """ Renders a single promo element according to reward type"""
    # Dispatcher
    PROMO_RENDERERS = {
        '1': render_quantity_discount,
        '2': render_percentage_discount,
        '3': render_percentage_discount,
        '6': render_quantity_discount,
        '10': render_quantity_discount,
    }
    # Get reward type and corresponding handler
    reward_type = promo.get('RewardType')
    handler = PROMO_RENDERERS.get(reward_type, None)
    # Call handler if exists
    handler(chain, promo)


def render_quantity_discount(chain: SupermarketChain, promo: dict):
    """ Renders a single promo element with reward type 1"""
    st.markdown(f"**{promo.get('PromotionDescription', 'N/A')}**")
    st.metric(
        label="Promotion Price",
        value=f"{promo.get('DiscountedPrice', 'N/A')} NIS",
    )
    st.write(f"- Minimum Quantity: {promo.get('MinQty', 'N/A')}")
    st.write(f"- Maximum Quantity: {promo.get('MaxQty', 'N/A')}")
    st.write(f"- Minimum Purchase: {promo.get('MinPurchaseAmnt', 'N/A')}")
    st.write(f"- Target Customers: {chain.promo_audience(promo)}")
    st.write(f"- Valid Until: {promo.get('PromotionEndDate', 'N/A')}")
    st.divider()


def render_percentage_discount(chain: SupermarketChain, promo: dict):
    """ Renders a single promo element with reward type 2"""
    st.markdown(f"**{promo.get('PromotionDescription', 'N/A')}**")
    st.metric(
        label="Promotion Discount",
        value=f"{int(promo.get('DiscountRate')) / 100}%",
    )
    st.write(f"- Minimum Quantity: {promo.get('MinQty', 'N/A')}")
    st.write(f"- Maximum Quantity: {promo.get('MaxQty', 'N/A')}")
    st.write(f"- Target Customers: {chain.promo_audience(promo)}")
    st.write(f"- Valid Until: {promo.get('PromotionEndDate', 'N/A')}")
    st.divider()


def selected_stores_element(label: str):
    """
    Renders the selected stores element - an expander with the main store and stores to compare,
    each with a clear button
    """
    if st.session_state.get('main_store'):

        with st.expander('Selected Stores',):
            # Display the main store
            with st.container():
                if st.session_state['main_store']:
                    st.markdown(f":blue[**{label}:**]")
                    # The data
                    main_store_info = next(iter(st.session_state['main_store'].values()))
                    # Display
                    st.write(f'**{main_store_info["chain_alias"].capitalize()}** - '
                             f'{main_store_info["store_name"]}')
                    # Clear button
                    st.button(label=':material/delete: Clear', width='stretch',
                              key='clear_main_store_button', on_click=clear_main_store)
                else:
                    st.write("**Home Store:** :red[Not Selected]")

            # Display stores to compare
            with st.container():
                if st.session_state['compare_store']:
                    st.markdown(":blue[**Stores to Compare:**]")
                    for key, store in st.session_state['compare_store'].items():
                        st.write(f'**{store["chain_alias"].capitalize()}** - '
                                 f'{store["store_name"]}')
                        # Clear button for each compare store
                        st.button(label=':material/delete: Clear', width='stretch',
                                  key=f'clear_compare_{key}_button',
                                  on_click=clear_compare_store, args=(key,))
                else:
                    st.write("**Stores to Compare:** :red[Not Selected]")
