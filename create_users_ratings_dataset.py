import csv

import pandas as pd

rate_big = pd.read_csv("datasets/ratings.csv", chunksize=10_000)
file = open("dictionary.txt")

map = {}
while True:
    record = file.readline()
    record = record[:-1]

    if not record:
        break

    id = record.split('-')
    map[int(id[0])] = id[1]
iterator = 0
for rate in rate_big:
    with open('datasets/user_db.csv', mode='a', newline='\n') as csv_file:

        fieldnames = ['userId', 'movieId', 'rating']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if iterator == 0:
            writer.writeheader()
        for i in range(len(rate)):
            try:
                writer.writerow({'userId': rate['userId'][i + iterator * 10_000],
                                 'movieId': map[int(rate['movieId'][i + iterator * 10_000])],
                                 'rating': rate['rating'][i + iterator * 10_000]})
            except:
                ""
        iterator += 1

file.close()
print("created user_db.csv")
