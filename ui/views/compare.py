import streamlit as st
import itertools
import math
import copy

from backend.app.services.shoppinglist_service import (check_item_in_price_data_and_add_to_store_shoppinglist,
                                                       get_item_dict_from_any_store)
from backend.app.services.session_state import all_session_keys
from backend.app.services.price_service import (best_cost_for_k_stores, add_prices_to_shopping_list,
                                                total_per_store, max_stores, from_key_to_store_name,
                                                common_items)
from ui.common_elements import logo
from ui.common_dialogs import alternatives_dialog


def add_item_to_shoppinglists():
    """
    Build shopping lists for all stores in session state based on items in items list.
    """
    # Dialog flag: Check if dialog should be shown
    if st.session_state.get("alternatives_dialog", False):
        # Show dialog with alternatives for the item
        alternatives_dialog()
        # prevent running the loop in same pass
        st.stop()

    # Last key (store) flag
    st.session_state['last_key'] = False
    # Get all session keys
    session_keys = all_session_keys()

    for idx, key in enumerate(session_keys):
        # Make copy of items_list for use with each key (if copy doesn't exist)
        if f'items_list_{key}' not in st.session_state:
            st.session_state[f'items_list_{key}'] = copy.deepcopy(st.session_state.get('items_list', []))
        st.session_state['current_key'] = key

        for item in st.session_state.get(f'items_list_{key}', []):
            # Get quantity from item
            st.session_state['quantity'] = item['Quantity']

            # Check if item code available in store (key) and add to shopping list for that store
            # Return value - True / False
            match = check_item_in_price_data_and_add_to_store_shoppinglist(item, key)

            # If item not found (=> alternatives already in session_state['alternatives'])
            if not match:
                # This will rerun the dialog because the dialog flag is set to True
                st.rerun()




def render():
    """ The main function to render the compare page """
    logo()
    st.divider()

    # Make shopping lists for each store, incl. replacing missing items
    add_item_to_shoppinglists()

    # Add prices to the shopping lists
    updated = add_prices_to_shopping_list(st.session_state.get('shopping_list'))

    # Tabs to display data
    tab1, tab2, tab3 = st.tabs(['Total per Store', 'Save the Most', 'All Prices'])

    # Totals
    with tab1:
        # Calc totals
        totals = total_per_store(updated)

        # Display totals for each store
        for key in totals:
            delta = (totals[key] - min(totals.values()))
            if delta == 0:
                delta_color = 'normal'
            else:
                delta_color = 'inverse'

            st.metric(label=from_key_to_store_name(key),
                      value=f"₪{totals[key]:,.2f}",
                      delta=f'{delta:.2f}',
                      delta_color=delta_color,
                      )
            st.divider()

    with tab2:
        session_keys = all_session_keys()
        if len(session_keys) == 1:
            st.subheader('Only 1 Store Selected')
        else:
            # Find best cost for k stores
            k = st.slider(
                label='Max Number of Stores to Visit',
                min_value=1,
                max_value=max_stores(),
                value=2,
                step=1
            )

            # Get best combination, total cost and shopping plan for each of k stores
            best_combo, best_total, best_plan = best_cost_for_k_stores(updated, k=k)

            st.subheader('Visit:')
            for store in best_combo:
                st.write(from_key_to_store_name(store))

            st.divider()

            st.metric(
                label='Total Cost',
                value=f"₪ {best_total:.2f}",
                delta=f"₪ {best_total - total_per_store(updated)[best_combo[0]]:.2f} saved",
                delta_arrow='off'
            )

            st.divider()
            for store in best_combo:
                st.subheader(from_key_to_store_name(store))
                with st.expander('For max SAVING'):
                    for item in best_plan[store]:
                        st.write(f"{item['item']} - {item['item_name']}:")
                        st.write(f"{item['quantity']} x ₪ {float(item['unit_price']):.2f} = ₪ {item['total_price']:.2f}")
                        st.divider()

        with tab3:
            # Display all prices for all items with same itemCode in all stores
            common = common_items(session_keys)
            for item in common:
                st.write(
                    f"{item} - {next(d.get('ItemName') or d.get('ItemNm') for d in st.session_state[session_keys[1]] if d['ItemCode'] == item)}")
                for key in session_keys:
                    price = next((d['ItemPrice'] for d in st.session_state[key] if d['ItemCode'] == item), None)
                    st.write(f"{from_key_to_store_name(key)}:", f"₪ {price}")
                st.divider()








if __name__ == "__main__":
    render()