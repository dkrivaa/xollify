import streamlit as st

from backend.app.utilities.general import session_code


def initialize_session_state():
    """ Initialize session state with default values for main and compare stores. """
    if 'main_store' not in st.session_state:
        st.session_state['main_store'] = {}
    if 'compare_store' not in st.session_state:
        st.session_state['compare_store'] = {}
    if 'option_key' not in st.session_state:
        st.session_state['option_key'] = None


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


def item_page_available():
    """ Conditions for item page to be available """
    # If main_store is selected, go to item details page
    if 'main_store' in st.session_state and st.session_state['main_store']:
        return True
    else:
        return False


def shoppinglist_page_available():
    """ Conditions for shoppinglist page to be available """
    # If main store defined
    if 'main_store' in st.session_state and st.session_state['main_store']:
        return True
    else:
        return False


def compare_page_available():
    """ Conditions for compare page to be available """
    if shoppinglist_page_available() and st.session_state.get('items_list', None):
        return True
    else:
        return False

