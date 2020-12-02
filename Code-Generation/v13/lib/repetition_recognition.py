
def recog_repetition_nontext(compos, show=True, inplace=True):
    compos_cp = compos.copy()
    compos_cp.select_by_class(['Compo', 'Background'], replace=True)

    compos_cp.cluster_dbscan_by_attr('center_column', eps=5, show=show, show_method='block')
    compos_cp.cluster_dbscan_by_attr('center_row', eps=5, show=show, show_method='block')
    compos_cp.cluster_dbscan_by_attr('area', eps=200, show=show, show_method='block')

    compos_cp.group_by_clusters(cluster=['cluster_area', 'cluster_center_column'], alignment='v', show=show, new_groups=True)
    compos_cp.group_by_clusters(cluster=['cluster_area', 'cluster_center_row'], alignment='h', show=show, new_groups=False, show_method='block')
    compos_cp.compos_dataframe.rename({'group':'group_nontext'}, axis=1, inplace=True)

    df = compos_cp.compos_dataframe
    # df = df.drop(columns=['cluster_area', 'cluster_center_column', 'cluster_center_row'])
    return df


def recog_repetition_text(compos, show=True, inplace=True):
    compos_cp = compos.copy()
    compos_cp.select_by_class(['Text'], replace=True)

    compos_cp.cluster_dbscan_by_attr('row_min', 5, show=show, show_method='line')
    compos_cp.cluster_dbscan_by_attr('column_min', 5, show=show, show_method='line')

    compos_cp.group_by_clusters('cluster_row_min', alignment='h', new_groups=True, show=show, show_method='block')
    compos_cp.group_by_clusters_conflict('cluster_column_min', 'cluster_row_min', alignment='v', show=show, show_method='block')

    compos_cp.compos_dataframe.rename({'group':'group_text'}, axis=1, inplace=True)

    df = compos_cp.compos_dataframe
    # df = df.drop(columns=['cluster_column_min', 'cluster_row_min'])
    return df



