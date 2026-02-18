import streamlit as st

from backend.app.core.super_class import SupermarketChain


def get_chain_from_code(chain_code):
    """ Get chain object from chain code """
    # List of all registered supermarket chains
    chains = SupermarketChain.registry
    # Get chain matching given chain code
    chain = next(c for c in chains if c.chain_code == chain_code)

    return chain


def session_code(chain_code: str | int, store_code: str | int) -> str:
    """ Make unique key combining chain_code and store_code """
    return f'{str(chain_code)}_{str(store_code)}'


def all_session_keys() -> list[str]:
    """ Get all unique session keys for main and compare stores """
    session_keys = []
    # Main store
    main_key = next(iter(st.session_state['main_store'].keys())) if st.session_state.get('main_store') else None
    if main_key:
        session_keys.append(main_key)
    # Compare stores
    compare_keys = list(st.session_state['compare_store'].keys()) if st.session_state.get('compare_store') else []
    session_keys.extend(compare_keys)

    return session_keys


def all_session_keys_dicts(session_keys: list[str]) -> list[dict[str, str]]:
    """
    Make list of dicts from list of session keys
    {chain_code: chain_code, store_code: store_code}
    """
    session_keys_dicts = []
    for key in session_keys:
        chain_code, store_code = key.split('_')
        session_keys_dicts.append({'chain_code': chain_code, 'store_code': store_code})

    return session_keys_dicts

