import pickle

import numpy as np
import pandas as pd

data1 = pd.read_csv("datasets/movies.csv")
data = pickle.load(open("datasets/title.merged.sav", "rb"))

f = open("dictionary.txt", "w")

for i in range(len(data1)):
    try:
        title_from_new_db = data1['title'][i]
        title_from_new_db = title_from_new_db.split('(')[0][:-1]
        id = ((np.where(data["primaryTitle"] == title_from_new_db))[0])[0]
        tconst = data['tconst'][id]
        record_to_save = str(data1['movieId'][i]) + "-" + str(tconst) + "\n"
        f.write(record_to_save)
    except:
        try:
            tab = title_from_new_db.split(',')
            t = ""
            for z in range(len(tab) - 1):
                t = t + tab[z]
            t = tab[(len(tab) - 1)][1:] + " " + t
            id = ((np.where(data["primaryTitle"] == t))[0])[0]
            tconst = data['tconst'][id]
            record_to_save = str(data1['movieId'][i]) + "-" + str(tconst) + "\n"
            f.write(record_to_save)
        except:
            ""

f.close()
print("created dictionary.txt")
