import streamlit as st

from backend.app.utilities.general import session_code
from backend.app.services.price_service import from_key_to_store_name
from backend.app.services.shoppinglist_service import get_item_dict_from_any_store
from ui.common_elements import chain_selector, store_selector, item_selector


@st.dialog(title='Select Store', dismissible=False)
def select_store_dialog(store_type: int = 2):
    """
    Dialog to select store for shopping data.
    args: store_type: 1 for main store, 2 for compare store (default)
    """
    chain, chain_alias = chain_selector()
    if chain:
        store, store_name = store_selector(chain_code=chain)

        if store:
            if store_type == 1:
                st.session_state['main_store'] = {
                    session_code(chain, store): {
                        'chain_code': chain,
                        'chain_alias': chain_alias,
                        'store_code': store,
                        'store_name': store_name
                    }
                }
            else:
                st.session_state['compare_store'][session_code(chain, store)] = {
                        'chain_code': chain,
                        'chain_alias': chain_alias,
                        'store_code': store,
                        'store_name': store_name
                }

            st.rerun()


@st.dialog(title="Item Not Found", dismissible=False, )
def alternatives_dialog():
    """ Dialog to show alternative items when item not found in store. """
    # Item dict from price data for item to be replaced
    item = st.session_state['item_to_replace']
    # List of dicts of alternative items (dicts from price data)
    alternatives = st.session_state['alternatives']
    # session key for store in current iteration
    key = st.session_state.get('current_key', None)
    # Quantity taken from relevant item in items_list
    quantity = st.session_state['quantity']

    # The items codes that cannot be used for alternative item (items still left in items_list_{key} or already used item codes for items in shopping list:
    items_codes_left = list({
                                d['Item Code'] for d in st.session_state[f'items_list_{key}']
                            } | {
                                d['Item Code'] for d in st.session_state['shopping_list'].get(key, [])
                            })

    # The actual dialog

    # Get user input
    with st.form("Item Not Found", clear_on_submit=True):
        st.write(f"No match found for:")
        st.write(f':blue[{from_key_to_store_name(key)}]')
        st.subheader(f':blue[{item['Product Name']}]')
        st.write(f"Please select or search for alternative items:")

        if alternatives:
            options = [d['ItemCode'] for d in alternatives if d['ItemCode'] not in items_codes_left]
            alt = st.radio(label='Suggested',
                           options=options,
                           format_func=lambda x: (
                               lambda d: f'{d.get("ItemName") or d.get("ItemNm")} - ₪{float(d["ItemPrice"]):.2f}'
                           )(next(d for d in alternatives if d["ItemCode"] == x)),
                           index=None)

        user_alt = item_selector(price_data=st.session_state.get(key),
                                 label='Search for alternative item',
                                 session_key=key)

        alt_qty = st.number_input(label='Change quantity',
                                  min_value=0.0,
                                  value=0.0,
                                  step=1.0,
                                  )

        # When user accepts alternative item
        submit = st.form_submit_button('Submit', icon=':material/add:', icon_position='left')

    if submit:
        # Add alternative to relevant store's shopping list

        # User selects item from dropdown
        if user_alt:
            alt_dict = next(d for d in st.session_state.get(key) if d['ItemCode'] == str(user_alt))
            alt = user_alt
        # User selects from the radio (generated alternatives)
        else:
            alt_dict = next(d for d in alternatives if d['ItemCode'] == str(alt))

        # User enter alternative quantity
        if alt_qty != 0.0:
            quantity = alt_qty

        if alt not in [i['Item Code'] for i in st.session_state['shopping_list'].get(key, [])]:
            st.session_state['shopping_list'].setdefault(key, []).append({'Item Code': str(alt),
                                                                          'Product Name': alt_dict['ItemName'] or alt_dict['ItemNm'],
                                                                          'Quantity': quantity,
                                                                          'alternative_to': item['Item Code']})
        # Remove item from store (key) items_list
        st.session_state[f'items_list_{key}'] = [d for d in st.session_state[f'items_list_{key}']
                                                 if d != item]

        # Reset dialog flag
        st.session_state['alternatives_dialog'] = False

        st.rerun()




