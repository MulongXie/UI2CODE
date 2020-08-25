import pandas as pd


def search_list_item_by_compoid(item_ids, compo_id):
    """
        list_items: dictionary => {id of first compo: ListItem}
    """
    for i in item_ids:
        if compo_id in item_ids[i]:
            return i


def gather_list_items(compos):
    '''
        gather compos into a list item in the same row/column of a same pair(list)
    '''
    list_items = {}
    item_ids = {}
    mark = []
    for i in range(len(compos)):
        compo = compos.iloc[i]
        # new item
        if compo['id'] not in mark and compo['pair_to'] not in mark:
            compo_paird = compos.loc[compo['pair_to']]

            list_items[compo['id']] = [compo, compo_paird]
            item_ids[compo['id']] = [compo['id'], compo['pair_to']]

            compos.loc[compo['id'], 'list_item'] = compo['id']
            compos.loc[compo['pair_to'], 'list_item'] = compo['id']
            mark += [compo['id'], compo['pair_to']]

        elif compo['id'] in mark and compo['pair_to'] not in mark:
            index = search_list_item_by_compoid(item_ids, compo['id'])
            list_items[index].append(compos.loc[compo['pair_to']])
            item_ids[index].append(compo['pair_to'])

            compos.loc[compo['pair_to'], 'list_item'] = index
            mark.append(compo['pair_to'])

        elif compo['id'] not in mark and compo['pair_to'] in mark:
            index = search_list_item_by_compoid(item_ids, compo['pair_to'])
            list_items[index].append(compos.loc[compo['id']])
            item_ids[index].append(compo['id'])

            compos.loc[compo['id'], 'list_item'] = index
            mark.append(compo['id'])

    compos['list_item'] = compos['list_item'].astype(int)
    return list_items
