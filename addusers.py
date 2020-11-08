import pandas as pd
import pickle
import csv

data1 = pd.read_csv("datasets/movies.csv")
rate_big = pd.read_csv("datasets/ratings.csv",chunksize=10_000)
data = pickle.load(open("datasets/title.merged.sav", "rb"))
file = open("slownikBIG.txt")

map={}
while True:
    rekord = file.readline()
    rekord = rekord[:-1]

    if not rekord:
        break

    id = rekord.split('-')
    map[int(id[0])]=int(id[1])
iterator = 0
for rate in rate_big:
    with open('user_db_REAL_REAL_BIG_FINAL_VERSION.csv', mode='a',newline='\n') as csv_file:
        fieldnames = ['userId', 'movieId', 'rating']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if iterator == 0:
            writer.writeheader()
        for i in range(len(rate)):
            try:
                writer.writerow({'userId': rate['userId'][i+iterator*10_000], 'movieId': map[int(rate['movieId'][i + iterator * 10_000])], 'rating': rate['rating'][i + iterator * 10_000]})
            except:
                ""
        iterator+=1





