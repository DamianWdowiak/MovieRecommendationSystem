import pickle
import joblib
from sklearn.feature_extraction.text import CountVectorizer

titles_data = pickle.load(open("../datasets/title.merged.sav", "rb"))

count = CountVectorizer()
count_matrix = count.fit_transform(titles_data['key_data'])
joblib.dump(count_matrix, '../datasets/count_matrix.joblib')
