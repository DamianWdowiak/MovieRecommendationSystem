import csv

import pandas as pd

rate_big = pd.read_csv("datasets/ratings.csv", chunksize=10_000)
file = pd.read_csv("datasets/links.csv")

iterator = 0
for rate in rate_big:
    with open('datasets/user_db.csv', mode='a', newline='\n') as csv_file:

        fieldnames = ['userId', 'tconst', 'rating']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if iterator == 0:
            writer.writeheader()
        for i in range(len(rate)):
            id = 'tt' + str(file[file['movieId'] == rate['movieId'][i + iterator * 10_000]]['imdbId'].values[0]).zfill(
                7)
            try:
                writer.writerow({'userId': rate['userId'][i + iterator * 10_000],
                                 'tconst': id,
                                 'rating': rate['rating'][i + iterator * 10_000]})
            except:
                ""
        iterator += 1

print("created user_db.csv")
