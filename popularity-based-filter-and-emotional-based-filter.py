import pickle

data = pickle.load(open("title.merged.sav", "rb"))

sredniaOcenaWszystkichFilmow = data['averageRating'].mean()
minimanlaLiczbaGlosow = data['numVotes'].quantile(0.90)
q_data = data.copy().loc[data['numVotes'] >= minimanlaLiczbaGlosow]


def weighted_rating(x, m=minimanlaLiczbaGlosow, C=sredniaOcenaWszystkichFilmow):
    v = x['numVotes']
    R = x['averageRating']

    return (v / (v + m) * R) + (m / (m + v) * C)


q_data['score'] = q_data.apply(weighted_rating, axis=1)

q_data = q_data.sort_values('score', ascending=False)
print("TOP 10:")
print(q_data[['tconst','primaryTitle', 'averageRating']].head(10))


# -------to emocjonalna czesc------

#genres = set()
#for g in data.genres.unique():
#    for a in g.split(','):
#        genres.add(a)
#genres = list(genres)

emotions = {
    "Scary": "Horror|Thriller",
    "Happy": "Music|Musical|Animation|Comedy",
    "Sad": "Documentary|War|History|Drama|Reality-TV",
    "Melting mood": "Biography|Romance",
    "Action craving": "Western|Sport|Adventure|Action|Sci-Fi|Fantasy",
    "Mysterious": "Mystery|Crime|Film-Noir|Adult",
    "Curious": "News|Talk-Show",
    "Light": "Game-Show|Family|Short"
}

def recomendedFilmToYourMood(emotion):
    e_data = data.copy().loc[data['genres'].str.contains(emotions[emotion])]
    e_data['score'] = e_data.apply(weighted_rating, axis=1)
    e_data = e_data.sort_values('score', ascending=False)
    print(e_data[['primaryTitle','genres','averageRating']].head(10))

mood = "Action craving"
print("\n\nMy mood: ",mood)
recomendedFilmToYourMood(mood)
