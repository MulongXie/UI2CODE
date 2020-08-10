from DF_Compos import DF_Compos


def recog_repetition_nontext(compos, show=True):
    compos_cp = compos.copy()
    compos_cp.select_by_class(['Compo', 'Background'], replace=True)

    compos_cp.cluster_dbscan_by_attr('center_column', eps=5, show=show, show_method='block')
    compos_cp.cluster_dbscan_by_attr('center_row', eps=5, show=show, show_method='block')
    compos_cp.cluster_dbscan_by_attr('area', eps=200, show=show, show_method='block')

    compos_cp.group_by_clusters(cluster=['cluster_area', 'cluster_center_column'], show=show, new_groups=True)
    compos_cp.group_by_clusters(cluster=['cluster_area', 'cluster_center_row'], show=show, new_groups=False, show_method='block')

    compos_cp.compos_dataframe.rename({'group':'group_nontext'}, axis=1, inplace=True)

    return compos_cp


def recog_repetition_text(compos, show=True):
    compos_cp = compos.copy()
    compos_cp.select_by_class(['Text', 'Background'], replace=True)

    compos_cp.cluster_dbscan_by_attr('row_min', 5, show=show, show_method='line')
    compos_cp.cluster_dbscan_by_attr('column_min', 5, show=show, show_method='line')

    compos_cp.group_by_clusters('cluster_row_min', new_groups=True, show=show, show_method='block')
    compos_cp.group_by_clusters_conflict('cluster_column_min', 'cluster_row_min', show=show, show_method='block')

    compos_cp.compos_dataframe.rename({'group':'group_text'}, axis=1, inplace=True)

    return compos_cp



