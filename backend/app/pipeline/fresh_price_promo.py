import streamlit as st
import asyncio

from backend.app.utilities.url_to_dict import data_dict
from backend.app.utilities.general import all_session_keys, all_session_keys_dicts
from backend.app.core.super_class import SupermarketChain


# @st.cache_data(ttl=1800)
async def fresh_price_data(chain_code: str | int, store_code: str | int, ) -> dict | None:
    """ Fetch fresh price data for the given chain and store code """
    # Get the supermarket chain class from its chain code
    chain = next((c for c in SupermarketChain.registry if c.chain_code == str(chain_code)), None)
    # Get the latest price URLs for the given chain and store code
    urls = await chain.safe_prices(store_code=store_code) if chain and store_code else None
    if urls:
        # Use pricefull URL and cookies if available
        url = urls.get('pricefull') or urls.get('PriceFull') if urls else None
        cookies = urls.get('cookies', None) if urls else None
        # Make data dict from data in pricefull URL
        price_dict = await data_dict(url=url, cookies=cookies) if url else None
        # Clean data dict to only include dicts of items
        price_data = chain.get_price_data(price_data=price_dict) if price_dict else None
        return price_data
    else:
        raise RuntimeError(f"No price URLs found for chain {chain_code} and store {store_code}.")


# @st.cache_data(ttl=1800)
async def fresh_promo_data(chain_code: str | int, store_code: str | int, ) -> dict | None:
    """ Fetch fresh promo data for the given chain and store code """
    # Get the supermarket chain class from its alias
    chain = next((c for c in SupermarketChain.registry if c.chain_code == str(chain_code)), None)
    # Get the latest price URLs for the given chain and store code
    urls = await chain.safe_prices(store_code=store_code) if chain and store_code else None
    if urls:
        # Use promofull URL and cookies if available
        url = urls.get('promofull') or urls.get('PromoFull') if urls else None
        cookies = urls.get('cookies', None) if urls else None
        # Make data dict from data in pricefull URL
        promo_dict = await data_dict(url=url, cookies=cookies) if url else None
        # Clean data dict to only include dicts of items
        promo_data = chain.get_promo_data(promo_data=promo_dict) if promo_dict else None
        return promo_data
    else:
        raise RuntimeError(f"No promo URLs found for chain {chain_code} and store {store_code}.")


async def load_stores_price_data():
    """ Load price data for all stores in session_state """
    # List of relevant session keys for which to load price data
    session_keys = all_session_keys()
    # Make list of dicts with chain_code and store_code from each session key
    session_keys_dicts = all_session_keys_dicts(session_keys=session_keys)

    # Get price data for all selected stores
    async with asyncio.TaskGroup() as tg:
        tasks = [
            tg.create_task(
                fresh_price_data(
                    chain_code=store['chain_code'],
                    store_code=store['store_code']
                )
            )
            for store in session_keys_dicts
        ]

    # Get results of all the tasks
    results = [task.result() for task in tasks]

    # Enter price data (results) into session stage
    for idx, item in enumerate(session_keys_dicts):
        session_key = f'{item['chain_code']}_{item['store_code']}'
        st.session_state[session_key] = results[idx]


async def load_main_store_promo_data():
    """ Load promo data for main store in session_state """
    # Get main store session key
    main_store_key, = st.session_state['main_store'].keys() if st.session_state.get('main_store') else None
    if not main_store_key:
        raise RuntimeError("No main store selected.")

    # Get chain_code and store_code from main store session key
    chain_code, store_code = main_store_key.split('_')

    # Get promo data for main store
    promo_data = await fresh_promo_data(chain_code=chain_code, store_code=store_code)

    # Enter promo data into session state
    st.session_state[f'{main_store_key}_promo_data'] = promo_data

