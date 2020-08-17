import pandas as pd
import draw


def num_of_compos_in_groups(groups):
    count = 0
    for group in groups:
        count += group.compos_number
    return count


def groups_cvt_df(groups):
    df = pd.DataFrame()
    for group in groups:
        df = df.append(group.compos_dataframe, sort=False)
    # df = df.sort_index()
    return df


class Group:
    def __init__(self, id, category, alignment, compos_ids, compos_dataframe):
        self.id = id
        self.category = category
        self.alignment = alignment
        self.compos_ids = compos_ids
        self.compos_dataframe = compos_dataframe
        self.compos_number = len(self.compos_ids)

    def visualize(self, img, img_shape, attr='class', name='board'):
        draw.visualize(img, self.compos_dataframe, img_shape, attr, name)

    def visualize_block(self, img, img_shape, attr='class', name='board'):
        draw.visualize_block(img, self.compos_dataframe, img_shape, attr, name)
