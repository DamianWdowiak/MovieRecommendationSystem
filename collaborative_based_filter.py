import pickle
import time
import pandas
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

model_knn = NearestNeighbors(metric='cosine', algorithm='brute', n_jobs=-1)
start = time.time()
users_data = pandas.read_csv(open("datasets/user_db.csv", "rb"))
titles_data = pickle.load(open("datasets/title.merged.sav", "rb"))
print(time.time() - start)
Mean = users_data.groupby(by="userId", as_index=False)['rating'].mean()


check = users_data.pivot_table(index='userId', columns='tconst', values='rating')
pivot_matrix = users_data.pivot_table(index='userId', columns='tconst', values='rating')
pivot_matrix = pivot_matrix.fillna(pivot_matrix.mean(axis=0))

pivot_matrix_values = csr_matrix(pivot_matrix.values)
model_knn.fit(pivot_matrix_values)

query_index = 610

distances, indices = model_knn.kneighbors(pivot_matrix.iloc[query_index, :].values.reshape(1, -1), n_neighbors=31)

# to-do parameter, function
users = []
for i in range(0, len(distances.flatten())):
    if i == 0:
        user = pivot_matrix.index[indices.flatten()[i]]
        print('Recommendations for {0}:\n'.format(pivot_matrix.index[indices.flatten()[i]]))
    else:
        users.append(pivot_matrix.index[indices.flatten()[i]])
        print('{0}: {1}, with distance of {2}:'.format(i, pivot_matrix.index[indices.flatten()[i]]
                                                       , distances.flatten()[i]))

def get_user_similar_movies( user1, user2 ):
    common_movies =users_data[users_data.userId == user1].merge(
    users_data[users_data.userId == user2],
    on = "tconst",
    how = "inner"  )
    return common_movies.merge(titles_data, on='tconst')




def user_item_score(user):
    movies_watched_by_user = check.columns[check[check.index == user].notna().any()].tolist()
    Movie_seen_by_similar_users = users_data[users_data.userId.isin(users)]['tconst'].values
    Movie_under_consideration = list(set(Movie_seen_by_similar_users)-set(list(movies_watched_by_user)))
    score = []
    for item in Movie_under_consideration:
        #======= userId +
        c = check.loc[:,item]
        temp = c[c.index.isin(users)]
        temp = temp[temp.notnull()]
        #===============

        index = temp.index.values.squeeze()  # users Ids którzy obejrzeli ITEM

        if index.size == 1:
            index = [index]
        else:
            index = index.tolist()

        # correlation user -> distance
        corr = pandas.Series(distances[0][1:], index=users)
        # t = corr.index == index

        corr = corr[corr.index.isin(index)]

        fin = pandas.concat([temp, corr], axis=1)

        fin.columns = ['t_score', 'correlation']
        # wzór na score
        fin['score'] = fin.apply(lambda x:x['t_score'] * x['correlation'], axis=1)
        score_sum = fin['score'].sum()
        correlation_sum = fin['correlation'].sum()
        final_score = (score_sum/correlation_sum)*(1-correlation_sum)

        score.append(final_score)
    
    data = pandas.DataFrame({'tconst':Movie_under_consideration, 'score':score})
    top_rec = data.sort_values(by='score', ascending=False).head(15)
    Movie_Name = top_rec.merge(titles_data, how='inner', on='tconst')
    Movie_Name = Movie_Name.primaryTitle.values.tolist()

    return Movie_Name


predicted_movies = user_item_score(user)
print(predicted_movies)

a = get_user_similar_movies(611, 612)
print(a.head(20))
