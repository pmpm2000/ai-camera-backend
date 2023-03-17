import os
import random

import matplotlib.axes
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from matplotlib import cm


class Heatmap:
    def __init__(self, sizeX, sizeY, crd):
        # musi byc sprawdzone zeby heat nie wychodzil za inta
        # koniecznie zadbac wczesniej o przeskalowanie tych wspolrzednych tak zeby pasowaly do rozmiaru
        """
        :param sizeX: number of horizontal pixels, e.g. 1920
        :param sizeY: number of vertical pixels, e.g. 1080
        :param crd: list of dictionaries containing pixel coordinates (x, y) and heat of this pixel. Must contain variables: x, y, heat.
        """
        self.sizeX = sizeX
        self.sizeY = sizeY
        self.crd = crd

    def __dictToList(self): # docelowo funkcja bedzie usunieta
        """
        converts given dictionary into format that heatmap creating function likes
        :returns DataFrame class object with sorted and counted coordinates
        """
        crd = self.crd
        l = list()

        for i in range(0, self.sizeY):
            tmp = [None] * self.sizeX
            l.append(tmp)

        for x in crd:
            l[x["x"]][x["y"]] = x["heat"]

        df = pd.DataFrame(l)
        return df

    def saveHeatmap(self):
        p1 = sns.heatmap(self.crd, yticklabels=False, xticklabels=False, cbar=False, square=True, snap=True, cmap="Reds")
        plt.savefig("temp.png", bbox_inches='tight', pad_inches=0)
        img = Image.open("temp.png")
        img2 = img.resize((self.sizeX, self.sizeY))
        img2.save("heatmap.png")
        os.remove("temp.png")

    def randomDataToHeatmap(self):
        l = list()
        for i in range(0, self.sizeX):
            tmp = [0] * self.sizeY
            l.append(tmp)
        repeat = np.random.randint(self.sizeX*self.sizeY)
        for i in range(repeat):
            x = np.random.randint(self.sizeX)
            y = np.random.randint(self.sizeY)
            heat = np.random.randint(500)
            l[x][y] = heat
        return pd.DataFrame(l)

#a = Heatmap(1920, 1080, "asd")
#a.saveHeatmap()
