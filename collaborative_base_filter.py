import pickle
import pandas
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
import numpy as np

model_knn = NearestNeighbors(metric='cosine', algorithm='brute', n_jobs=-1)

users_data = pandas.read_csv(open("datasets/user_db_smalll.csv", "rb"))
titles_data = pickle.load(open("datasets/title.merged.sav", "rb"))



pivot_matrix = users_data.pivot_table(index='movieId', columns='userId', values='rating').fillna(0)

pivot_matrix_values = csr_matrix(pivot_matrix.values)
model_knn.fit(pivot_matrix_values)

query_index = np.random.choice(pivot_matrix.shape[0])

movie_to_idx = {
    movie: i for i, movie in
    enumerate(list(titles_data.loc[pivot_matrix.index].primaryTitle))
}

query_index = movie_to_idx['Toy Story']

print(titles_data['primaryTitle'][pivot_matrix.index[7018]])
print(pivot_matrix.shape)

distances, indices = model_knn.kneighbors(pivot_matrix.iloc[query_index,:].values.reshape(1,-1), n_neighbors=10)
# to-do parameter, function

for i in range(0, len(distances.flatten())):
    if i == 0:
        print('Recommendations for {0}:\n'.format(titles_data['primaryTitle'][pivot_matrix.index[query_index]]))
    else:
        print('{0}: {1}, with distance of {2}:'.format(i, titles_data['primaryTitle'][pivot_matrix.index[indices.flatten()[i]]], distances.flatten()[i]))