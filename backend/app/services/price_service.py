import streamlit as st
import itertools
import math


def best_cost_for_k_stores(shoppinglist, k):
    """
    Calculate the best cost for shoppinglist using k stores.

    Tries all combinations of up to k stores and finds the combination
    where buying each item at the cheapest available store yields the lowest total cost.

    Args:
        shoppinglist: {
            "StoreA": [ {"Item Code": ..., "Product Name": ..., "Quantity": ..., "price": ...}, ... ],
            "StoreB": [...],
            ...
        }
        k: max number of stores to visit

    Returns:
        best_combo: tuple of store keys with lowest total cost
        best_total: total cost for best combination
        best_plan: dict of {store: [items assigned to that store]}
    """
    stores = list(shoppinglist.keys())

    # Number of items (all store lists are the same length)
    n_items = len(next(iter(shoppinglist.values())))

    # ---- Build price maps: {store: {item_index: float(price)}} ----
    price_maps = {
        store: {i: float(shoppinglist[store][i]["price"]) for i in range(n_items)}
        for store in stores
    }

    best_combo = None
    best_total = math.inf
    best_plan = None

    # ---- Try all store combinations up to size k ----
    for r in range(1, k + 1):
        for combo in itertools.combinations(stores, r):

            store_plan = {s: [] for s in combo}
            total_cost = 0

            for i in range(n_items):
                # Get available prices for this item across stores in combo
                available = [(store, price_maps[store][i]) for store in combo]

                # Choose the cheapest store for this item
                best_store, unit_price = min(available, key=lambda x: x[1])

                # Take quantity from the assigned store
                qty = shoppinglist[best_store][i]["Quantity"]
                cost = unit_price * qty

                store_plan[best_store].append({
                    'item': shoppinglist[best_store][i]["Item Code"],
                    'item_name': shoppinglist[best_store][i]["Product Name"],  # name from assigned store
                    'quantity': qty,
                    'unit_price': unit_price,
                    'total_price': cost
                })

                total_cost += cost

            print(f"combo: {combo}, total: {total_cost:.2f}")

            # Record best result if this combo is cheaper
            if total_cost < best_total:
                best_total = total_cost
                best_combo = combo
                best_plan = store_plan

    return best_combo, best_total, best_plan


def add_prices_to_shopping_list(shopping_list: dict) -> dict:
    """
    Add 'price' to every item in every store in the shopping list.
    Looks up prices from st.session_state[store_key].
    Returns a NEW updated shopping dict.
    """
    updated = {}

    for session_key, items in shopping_list.items():
        price_data = st.session_state.get(session_key, [])

        new_items = []
        for item in items:
            # Normalize item code to string
            item_code = str(item["Item Code"])

            # Find price for this item in the store's price data
            price = next(
                (d["ItemPrice"] for d in price_data if d["ItemCode"] == item_code),
                None
            )

            # Create a copy so we don't mutate the original
            updated_item = dict(item)
            updated_item["price"] = price

            new_items.append(updated_item)

        updated[session_key] = new_items

    return updated


def total_per_store(shoppinglist):
    """ Calculate total cost per store """
    totals = {}
    for session_key, items in shoppinglist.items():
        total = sum(float(item['Quantity']) * float(item['price']) for item in items)
        totals[session_key] = total
    return totals


def from_key_to_store_name(key):
    """ Convert session key to chain, store name """
    all_stores_dict = st.session_state.get('main_store') | st.session_state.get('compare_store')
    chain = next(d['chain_alias'] for d in all_stores_dict.values()
                 if d['chain_code'] == key.split('_')[0])
    store = next(d['store_name'] for d in all_stores_dict.values()
                 if d['chain_code'] == key.split('_')[0] and d['store_code'] == key.split('_')[1])
    return f'{chain} - {store}'


def shoppinglist_common_items(updated_shoppinglist: dict[str, [list]]):
    """ Get list of items in shopping list across all selected stores """
    # Assume all inner lists have the same length
    keys = list(updated_shoppinglist.keys())
    length = len(next(iter(updated_shoppinglist.values())))

    result = []

    for i in range(length):
        row = {}
        for key in keys:
            row[key] = updated_shoppinglist[key][i]
        result.append(row)

    return result




def all_common_items(session_keys):
    """ Get list of all item codes common to all selected stores """
    item_sets = []
    for key in session_keys:
        items = set(d['ItemCode'] for d in st.session_state[key])
        item_sets.append(items)
    common = set.intersection(*item_sets)
    return common
