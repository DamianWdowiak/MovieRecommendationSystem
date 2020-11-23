import pickle
import time

import numpy as np
import pandas
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity

model_knn = NearestNeighbors(metric='cosine', algorithm='brute', n_jobs=-1)
start = time.time()
users_data = pandas.read_csv(open("datasets/user_db.csv", "rb"))
titles_data = pickle.load(open("datasets/title.merged.sav", "rb"))
print(time.time() - start)
Mean = users_data.groupby(by="userId", as_index=False)['rating'].mean()
Rating_avg = pandas.merge(users_data, Mean, on="userId")
# Rating_avg['adg_rating']=Rating_avg['rating_x']-Rating_avg['rating_y']


check = Rating_avg.pivot_table(index='userId', columns='tconst', values='rating_x')
pivot_matrix = users_data.pivot_table(index='userId', columns='tconst', values='rating')
# pivot_matrix = Rating_avg.pivot_table(index='userId', columns='tconst', values='adg_rating')
pivot_matrix = pivot_matrix.fillna(pivot_matrix.mean(axis=0))

# final = Rating_avg.pivot_table(index='userId', columns='tconst', values='adg_rating')

# final_movie = final.fillna(final.mean(axis=0))

# cosine = cosine_similarity(final_movie)
# np.fill_diagonal(cosine, 0)
# similarity_with_movie = pandas.DataFrame(cosine, index=final_movie.index, columns=final_movie.index)

pivot_matrix_values = csr_matrix(pivot_matrix.values)
model_knn.fit(pivot_matrix_values)

# query_index = np.random.choice(pivot_matrix.shape[0])
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
        c = pivot_matrix.loc[:,item]
        f = c[c.index.isin(users)]
        f = f[f.notnull()]
        #===============

        index = f.index.values.squeeze().tolist()  # users Ids którzy obejrzeli ITEM

        # correlation user -> distance
        corr = pandas.Series(distances[0][1:], index=index)


        fin = pandas.concat([f, corr], axis=1)

        fin.columns = ['t_score', 'correlation']
        # wzór na score
        fin['score'] = fin.apply(lambda x:x['t_score'] * x['correlation'], axis=1)
        nume = fin['score'].sum()
        deno = fin['correlation'].sum()
        final_score = (nume/deno)
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

















# for i in range(0, len(distances.flatten())):
#     if i == 0:
#         print('Recommendations for {0}:\n'.format(titles_data[
#                                                       titles_data.tconst == pivot_matrix.index[
#                                                           indices.flatten()[i]]].primaryTitle.values[0]))
#     else:
#         print('{0}: {1}, with distance of {2}:'.format(i, titles_data[
#             titles_data.tconst == pivot_matrix.index[indices.flatten()[i]]].primaryTitle.values[0]
#                                                        , distances.flatten()[i]))
