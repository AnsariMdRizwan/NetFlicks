from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import pandas as pd
import requests
import joblib

app = Flask(__name__)
CORS(app)

# Load data once
movies = pickle.load(open('model.pkl', 'rb'))
similarity = joblib.load(open('similarity_compressed.pkl', 'rb'))
movies = pd.DataFrame(movies)

TMDB_API_KEY = "f9537e4494f1293f6c52ba7677986fca"

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path', '')
    return f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else ""

@app.route('/movies', methods=['GET'])
def get_movies():
    return jsonify(movies['title'].tolist())

@app.route('/recommend', methods=['POST'])
def recommend():
    movie = request.json.get("movie")
    if movie not in movies['title'].values:
        return jsonify({"error": "Movie not found"}), 404

    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_movie_posters.append(fetch_poster(movie_id))

    return jsonify({
        "names": recommended_movie_names,
        "posters": recommended_movie_posters
    })

if __name__ == '__main__':
    app.run(debug=True)