import streamlit as st
import pandas as pd

from backend.app.agent.alternative_product import get_alternatives
from backend.app.services.async_runner import run_async
from backend.app.services.session_state import all_session_keys


def read_user_list(user_list):
    """ Read user uploaded items list and return list of dicts with item and quantity """
    # Read the uploaded file into a pandas DataFrame
    if user_list.name.endswith('.csv'):
        df = pd.read_csv(user_list)
    if user_list.name.endswith('.xlsx'):
        df = pd.read_excel(user_list)

    # Set column names
    df.columns = ['Item Code', 'Product Name', 'Quantity']
    df['Item Code'] = df['Item Code'].astype(str)
    df['Quantity'] = df['Quantity'].astype(float)

    # Convert the DataFrame to a list of dictionaries
    items_list = df.to_dict(orient='records')

    return items_list


def convert_for_download(df):
    """ Convert items list in session state to DataFrame and then to CSV for download """
    # Convert list of dicts to DataFrame
    df.columns = ['Item Code', 'Product Name', 'Quantity']  # Rename columns for better readability
    # Convert DataFrame to CSV
    csv = df.to_csv(index=False).encode('utf-8-sig')

    return csv


def check_item_in_price_data_and_add_to_store_shoppinglist(item: dict, key: str):
    """ Check if item (item code) available in store price data and add to shopping list if found """
    match = next((d for d in st.session_state.get(key, []) if d['ItemCode'] == item['Item Code']), None)
    # If item found in store:
    if match is not None:
        # Add item to shopping list for the store (key) in session state if not already present
        if item['Item Code'] not in [i['Item Code'] for i in st.session_state['shopping_list'].get(key, [])]:
            item['alternative_to'] = None
            st.session_state['shopping_list'].setdefault(key, []).append(item)
        # Remove item from store (key) items_list
        st.session_state[f'items_list_{key}'] = [d for d in st.session_state[f'items_list_{key}']
                                                 if d != item]
        return True

    # If item is already in store (key) shoppinglist with alternative item
    elif (st.session_state['shopping_list'].get(key, []) and
          item['Item Code'] in [d['alternative_to'] for d in st.session_state['shopping_list'][key]]):
        # Remove item from store (key) items_list
        st.session_state[f'items_list_{key}'] = [d for d in st.session_state[f'items_list_{key}']
                                                 if d != item]
        return True

    # If item not found in store:
    else:
        # Get item details from price data of any store where available
        item_dict = get_item_dict_from_any_store(str(item['Item Code']))
        # Find alternative products for the item in relevant store (key)
        if item_dict:
            alternatives = run_async(get_alternatives,
                                     all_products=st.session_state[key],
                                     input_product=item_dict)
        else:
            alternatives = []

        st.session_state['alternatives'] = alternatives
        st.session_state['item_to_replace'] = item
        st.session_state['alternatives_dialog'] = True

        return False


def get_item_dict_from_any_store(item):
    """ Check if item available in any of selected stores """
    # Get all session keys
    session_keys = all_session_keys()

    # Check if item available in any store and return item details if found
    for key in session_keys:
        match = next((d for d in st.session_state.get(key, []) if d['ItemCode'] == item), None)
        if match:
            return match

    return None


