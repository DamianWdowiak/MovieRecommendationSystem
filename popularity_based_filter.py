import pickle

data = pickle.load(open("datasets/title.merged.sav", "rb"))
average_rating_of_all_film = data['averageRating'].mean()
down_boundary = data['numVotes'].quantile(0.90)

def weighted_rating(x, m=down_boundary, C=average_rating_of_all_film):
    v = x['numVotes']
    R = x['averageRating']

    return (v / (v + m) * R) + (m / (m + v) * C)

def getTopN(n):
    q_data = data.copy().loc[data['numVotes'] >= down_boundary]
    q_data['score'] = q_data.apply(weighted_rating, axis=1)
    q_data = q_data.sort_values('score', ascending=False)
    return q_data[['primaryTitle', 'averageRating']].head(n)
