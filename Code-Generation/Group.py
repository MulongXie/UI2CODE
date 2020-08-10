import pandas as pd
import numpy as np


class Group:
    def __init__(self, id, df, alignment):
        self.id = id
        self.compos_dataframe = df
        self.alignment = alignment

