import pandas
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors


def collaborative_filter(users_data, userId, n_recommendations=10):
    model_knn = NearestNeighbors(metric='cosine', algorithm='brute', n_jobs=-1)

    check = users_data.pivot_table(index='userId', columns='tconst', values='rating')
    pivot_matrix = users_data.pivot_table(index='userId', columns='tconst', values='rating')
    pivot_matrix = pivot_matrix.fillna(pivot_matrix.mean(axis=0))

    pivot_matrix_values = csr_matrix(pivot_matrix.values)
    model_knn.fit(pivot_matrix_values)

    distances, indices = model_knn.kneighbors(pivot_matrix.iloc[userId - 1, :].values.reshape(1, -1), n_neighbors=31)

    users = pivot_matrix.index[indices.flatten()]
    users = users[1:].tolist()

    movies_watched_by_user = check.columns[check[check.index == userId].notna().any()].tolist()
    movie_seen_by_similar_users = users_data[users_data.userId.isin(users)]['tconst'].values
    movie_under_consideration = list(set(movie_seen_by_similar_users) - set(list(movies_watched_by_user)))
    score = []
    for item in movie_under_consideration:
        c = check.loc[:, item]
        temp = c[c.index.isin(users)]
        temp = temp[temp.notnull()]

        index = temp.index.values.squeeze()

        if index.size == 1:
            index = [index]
        else:
            index = index.tolist()

        corr = pandas.Series(distances[0][1:], index=users)
        corr = corr[corr.index.isin(index)]

        fin = pandas.concat([temp, corr], axis=1)

        fin.columns = ['t_score', 'correlation']
        fin['score'] = fin.apply(lambda x: x['t_score'] * x['correlation'] * (1 - x['correlation']), axis=1)
        score_sum = fin['score'].sum()
        correlation_sum = fin['correlation'].sum()
        final_score = (score_sum / correlation_sum)

        score.append(final_score)

    data = pandas.DataFrame({'tconst': movie_under_consideration, 'score': score})
    top_rec = data.sort_values(by='score', ascending=False).head(n_recommendations)

    return top_rec.tconst.values.tolist()
