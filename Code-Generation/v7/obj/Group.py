
class Group:
    def __init__(self, id, compos):
        self.id = id
        self.compos = compos                                    # dataframe
        self.alignment = compos.iloc[0]['alignment_in_group']   # group element's alignment

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
