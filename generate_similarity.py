import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import ast
import pickle

# 1. Load Data
movies = pd.read_csv(r'./data/tmdb_5000_movies.csv')
credits = pd.read_csv(r'./data/tmdb_5000_credits.csv')

# 2. Merge Dataframes on title
movies = movies.merge(credits, on='title')

# 3. Select useful columns
movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]
movies.dropna(inplace=True)

# 4. Helper Functions to clean JSON columns
def convert(obj):
    L = []
    for i in ast.literal_eval(obj):
        L.append(i['name'])
    return L

def convert3(obj):
    L = []
    counter = 0
    for i in ast.literal_eval(obj):
        if counter != 3:
            L.append(i['name'])
            counter+=1
        else:
            break
    return L

def fetch_director(obj):
    L = []
    for i in ast.literal_eval(obj):
        if i['job'] == 'Director':
            L.append(i['name'])
            break
    return L

# 5. Apply transformations
print("Processing data... this might take a minute.")
movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)
movies['cast'] = movies['cast'].apply(convert3)
movies['crew'] = movies['crew'].apply(fetch_director)

# Convert string overview to list
movies['overview'] = movies['overview'].apply(lambda x:x.split())

# Remove spaces to create unique tags (e.g., 'Sam Worthington' -> 'SamWorthington')
movies['genres'] = movies['genres'].apply(lambda x:[i.replace(" ","") for i in x])
movies['keywords'] = movies['keywords'].apply(lambda x:[i.replace(" ","") for i in x])
movies['cast'] = movies['cast'].apply(lambda x:[i.replace(" ","") for i in x])
movies['crew'] = movies['crew'].apply(lambda x:[i.replace(" ","") for i in x])

# 6. Create the "Tag"
movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']
new_df = movies[['movie_id', 'title', 'tags']]
new_df['tags'] = new_df['tags'].apply(lambda x:" ".join(x))
new_df['tags'] = new_df['tags'].apply(lambda x:x.lower())

# 7. Vectorization (Text to Numbers)
# We use Bag of Words (CountVectorizer) - limiting to 5000 most frequent words
cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(new_df['tags']).toarray()

# 8. Calculate Cosine Similarity
# This calculates the angle between every movie and every other movie
similarity = cosine_similarity(vectors)

# 9. Save files
pickle.dump(new_df, open('movies_list.pkl', 'wb'))
pickle.dump(similarity, open('similarity.pkl', 'wb'))

print("Success! Model files generated.")
