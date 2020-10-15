
def split_groups_with_intersection(compos):
    grps = {}
    intersections = {}
    groups = compos.groupby('group').groups
    for i in groups:
        if len(groups[i]) <= 1:
            continue
        grp = Group(i, compos.loc[groups[i]])
        for j in grps:
            g = grps[j]
            if grp.is_intersected(g):
                if grp.id not in intersections:
                    intersections[grp.id] = [g.id]
                else:
                    intersections[grp.id].append(g.id)
                if g.id not in intersections:
                    intersections[g.id] = [grp.id]
                else:
                    intersections[g.id].append(grp.id)
        grps[grp.id] = grp
    return grps, intersections


def find_sandwiches_in_group(group, compos_all):
    alignment = group.alignment
    sandwiches = []
    for i in range(len(group.compos) - 1):
        c_a = group.compos.iloc[i]
        c_b = group.compos.iloc[i + 1]
        col_min = min(c_a['column_min'], c_b['column_min'])
        col_max = max(c_a['column_max'], c_b['column_max'])
        row_min = min(c_a['row_min'], c_b['row_min'])
        row_max = max(c_a['row_max'], c_b['row_max'])
        sandwich = compos_all[compos_all['group'] != group.id]
        if alignment == 'h':
            # filter elements not on the same horizontal level
            sandwich = sandwich[~((sandwich['row_max'] < row_min) | (sandwich['row_min'] > row_max))]
            # c_a is on the left of c_b
            sandwich = sandwich[
                (sandwich['column_min'] > c_a['column_max']) & (sandwich['column_max'] < c_b['column_min'])]
        elif alignment == 'v':
            # filter elements not on the same vertical level
            sandwich = sandwich[~((sandwich['column_max'] < col_min) | (sandwich['column_min'] > col_max))]
            # c_a is above c_b
            sandwich = sandwich[(sandwich['row_min'] > c_a['row_max']) & (sandwich['row_max'] < c_b['row_min'])]
        sandwiches.append(sandwich)
    return sandwiches


class Group:
    def __init__(self, id, compos):
        self.id = id
        self.compos = compos                                    # dataframe
        self.alignment = compos.iloc[0]['alignment_in_group']   # group element's alignment
        if self.alignment == 'v':
            self.compos.sort_values('row_min', inplace=True)
        else:
            self.compos.sort_values('column_min', inplace=True)

        self.top, self.bottom, self.left, self.right = self.group_boundary()
        self.width = self.bottom - self.top
        self.height = self.right - self.left
        self.area = self.width * self.height

        self.intersected_grps = []

    def group_boundary(self):
        compo = self.compos
        top = compo['row_min'].min()
        left = compo['column_min'].min()
        bottom = compo['row_max'].max()
        right = compo['column_max'].max()
        return top, bottom, left, right

    def get_boundary(self):
        return self.top, self.bottom, self.left, self.right

    def is_intersected(self, group_b):
        top_a, bottom_a, left_a, right_a = self.get_boundary()
        top_b, bottom_b, left_b, right_b = group_b.get_boundary()
        top_s = max(top_a, top_b)
        bottom_s = min(bottom_a, bottom_b)
        left_s = max(left_a, left_b)
        right_s = min(right_a, right_b)
        w = max(0, bottom_s - top_s)
        h = max(0, right_s - left_s)
        if w == 0 or h == 0:
            return False
        return True
