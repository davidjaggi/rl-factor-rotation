import pandas as pd
import datetime
import random
import threading
import time  # to simulate a real time data, time loop


class Update():

    def __init__(self, df):
        self.df = df
        self.df2 = self.df.drop(df.index)

    def func1(self):
        for i in range(125):
            self.entry = self.df.iloc[[i]]
            self.df2 = pd.concat([self.df2, self.entry])
            time.sleep(1)

    def func2(self):
