import pandas as pd
from surprise import KNNWithMeans
from surprise.model_selection import cross_validate
from surprise import Dataset
from surprise import Reader

algo = KNNWithMeans()
r_cols = ['user_id', 'item_id', 'rating']
ratings = pd.read_csv('user-id-sentiment-category_and_score', names=r_cols)
reader = Reader(rating_scale=(-1, 1))
data = Dataset.load_from_df(ratings[['user_id', 'item_id', 'rating']], reader)
trainset = data.build_full_trainset();
algo.fit(trainset)
# Run 5-fold cross-validation and print results
cross_validate(algo, data, measures=['RMSE', 'MAE', 'FCP'], cv=5, verbose=True)