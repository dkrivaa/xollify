import streamlit as st


def initialize_session_state():
    """ Initialize session state with default values for main and compare stores. """
    if 'main_store' not in st.session_state:
        st.session_state['main_store'] = {}
    if 'compare_store' not in st.session_state:
        st.session_state['compare_store'] = {}


def clear_session_state():
    """ Clear all session state. """
    st.session_state.clear()


def clear_main_store():
    """ Clear the main store from session state. """
    st.session_state['main_store'] = {}


def clear_compare_store(session_key):
    """ Clear a store from the compare store list in session state. """
    if session_key in st.session_state['compare_store']:
        del st.session_state['compare_store'][session_key]


def all_session_keys():
    """ Get all unique session keys for main and compare stores. """
    session_keys = []
    # Main store
    main_key = next(iter(st.session_state['main_store'].keys())) if st.session_state.get('main_store') else None
    if main_key:
        session_keys.append(main_key)
    # Compare stores
    compare_keys = list(st.session_state['compare_store'].keys()) if st.session_state.get('compare_store') else []
    session_keys.extend(compare_keys)

    return session_keys