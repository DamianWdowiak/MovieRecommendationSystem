import pickle

from filters.popularity_based_filter import weighted_rating

data = pickle.load(open("../datasets/title.merged.sav", "rb"))

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


def recommendedFilmToYourMood(emotion, n):
    e_data = data.copy().loc[data['genres'].str.contains(emotions[emotion])]
    e_data['score'] = e_data.apply(weighted_rating, axis=1)
    e_data = e_data.sort_values('score', ascending=False)
    return e_data[['primaryTitle', 'genres', 'averageRating']].head(n)
