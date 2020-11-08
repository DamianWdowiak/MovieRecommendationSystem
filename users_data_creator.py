import pandas as pd
import pickle
import numpy as np

data1 = pd.read_csv("C:/Users/Wiktoura/Desktop/PK/baza_uzytkownikow/big/ml-latest/movies.csv")
data = pickle.load(open("datasets/title.merged.sav", "rb"))


f = open("slownikBIG.txt","w")

for i in range(len(data1)):
    try:
        orginal_title = data1['title'][i]
        title_from_new_db = data1['title'][i]
        title_from_new_db = title_from_new_db.split('(')[0][:-1]
        id = ((np.where(data["primaryTitle"] == title_from_new_db))[0])[0]
        record_to_save = str(data1['movieId'][i]) + "-" + str(id) + "\n"
        f.write(record_to_save)
    except:
        try:
            tab = title_from_new_db.split(',')
            t=""
            for z in range(len(tab)-1):
                t = t + tab[z]
            t = tab[(len(tab)-1)][1:]+" "+t
            id = ((np.where(data["primaryTitle"] == t))[0])[0]
            record_to_save = str(data1['movieId'][i]) + "-" + str(id) + "\n"
            f.write(record_to_save)
        except:
            ""

f.close()

