import glob
import gzip
import os
import pickle
import shutil

import pandas as pd
import requests


def download_datasets(urls):
    for url in urls:
        filename = url.split("/")[-1]
        with open("../datasets/" + filename, "wb") as f:
            r = requests.get(url)
            f.write(r.content)


def extract_datasets():
    gz_files = glob.glob("../datasets/*.gz")
    for file in gz_files:
        with gzip.open(file, 'rb') as f:
            filename = file[:-3]
            with open(filename, 'wb') as out:
                shutil.copyfileobj(f, out)
        os.remove(file)


def convert_datasets():
    tsv_files = glob.glob("../datasets/*.tsv")
    for file in tsv_files:
        print(file)
        pickle.dump(pd.read_table(file, sep="\t", low_memory=False, na_values=["\\N", "nan"]),
                    open(file[:-4] + ".sav", "wb"))
        os.remove(file)


def merge_datasets():
    df_title_basics = pickle.load(open("../datasets/title.basics.sav", "rb"))
    df_title_ratings = pickle.load(open("../datasets/title.ratings.sav", "rb"))
    df_title_crew = pickle.load(open("../datasets/title.crew.sav", "rb"))
    df_title_principals = pickle.load(open("../datasets/title.principals.sav", "rb"))

    df_title_basics = df_title_basics[(df_title_basics.titleType == "movie") | (df_title_basics.titleType == "tvMovie")]
    df_title_basics.drop(["titleType", "originalTitle", "startYear", "endYear", "runtimeMinutes", "isAdult"], axis=1,
                         inplace=True)

    df_title_principals.drop(["ordering", "category", "job", "characters"], axis=1, inplace=True)
    df_title_principals = df_title_principals.groupby('tconst', as_index=False).agg(
        {'tconst': 'first', 'nconst': ','.join})

    data = pd.merge(df_title_basics, df_title_ratings, on="tconst")
    data = pd.merge(data, df_title_crew, on="tconst")
    data = pd.merge(data, df_title_principals, on="tconst")
    data = data.fillna('')

    data['key_data'] = data.apply(concat, axis=1)
    data.drop(["directors", "writers", "nconst"], axis=1, inplace=True)

    data.info()  # database information

    pickle.dump(data, open("../datasets/title.merged.sav", "wb"))

    os.remove('../datasets/title.basics.sav')
    os.remove('../datasets/title.ratings.sav')
    os.remove('../datasets/title.crew.sav')
    os.remove('../datasets/title.principals.sav')

    print("File datasets/title.merged.sav saved.")


def concat(x):
    return ''.join(x['genres'].replace(',', ' ')) + ' ' + ''.join(x['directors'].replace(',', ' ')) + ' ' + ''.join(
        x['writers'].replace(',', ' ')) + ' ' + ''.join(x['nconst'].replace(',', ' '))


if __name__ == '__main__':
    urls = ['https://datasets.imdbws.com/title.basics.tsv.gz',
            'https://datasets.imdbws.com/title.crew.tsv.gz',
            'https://datasets.imdbws.com/title.ratings.tsv.gz',
            'https://datasets.imdbws.com/title.principals.tsv.gz']

    download_datasets(urls)
    extract_datasets()
    convert_datasets()
    merge_datasets()
