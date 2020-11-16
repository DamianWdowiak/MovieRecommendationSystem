import pickle
import time

import numpy as np
import pandas
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

model_knn = NearestNeighbors(metric='cosine', algorithm='brute', n_jobs=-1)
start = time.time()
users_data = pandas.read_csv(open("datasets/user_db.csv", "rb"))
titles_data = pickle.load(open("datasets/title.merged.sav", "rb"))
print(time.time() - start)
users_data = users_data.head(100_000)


pivot_matrix = users_data.pivot_table(index='userId', columns='movieId', values='rating').fillna(0)

pivot_matrix_values = csr_matrix(pivot_matrix.values)
model_knn.fit(pivot_matrix_values)

query_index = np.random.choice(pivot_matrix.shape[0])

# movie_to_idx = {
#     movie: i for i, movie in
#     enumerate(list(titles_data.set_index('tconst').loc[pivot_matrix.index].primaryTitle))
# }

# query_index = movie_to_idx['Toy Story']

distances, indices = model_knn.kneighbors(pivot_matrix.iloc[query_index, :].values.reshape(1, -1), n_neighbors=10)
# to-do parameter, function

for i in range(0, len(distances.flatten())):
    if i==1:
        user2 = pivot_matrix.index[indices.flatten()[i]]
    if i == 0:
        user1 = pivot_matrix.index[indices.flatten()[i]]
        print('Recommendations for {0}:\n'.format(pivot_matrix.index[indices.flatten()[i]]))
    else:
        print('{0}: {1}, with distance of {2}:'.format(i, pivot_matrix.index[indices.flatten()[i]]
                                                       , distances.flatten()[i]))

def get_user_similar_movies( user1, user2 ):
    common_movies =users_data[users_data.userId == user1].merge(
    users_data[users_data.userId == user2],
    on = "movieId",
    how = "inner"  )
    return common_movies


a = get_user_similar_movies(user1, user2)
print(a.head(10))

# for i in range(0, len(distances.flatten())):
#     if i == 0:
#         print('Recommendations for {0}:\n'.format(titles_data[
#                                                       titles_data.tconst == pivot_matrix.index[
#                                                           indices.flatten()[i]]].primaryTitle.values[0]))
#     else:
#         print('{0}: {1}, with distance of {2}:'.format(i, titles_data[
#             titles_data.tconst == pivot_matrix.index[indices.flatten()[i]]].primaryTitle.values[0]
#                                                        , distances.flatten()[i]))
