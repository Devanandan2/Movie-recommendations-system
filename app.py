import streamlit as st
import pandas as pd 
import requests
import pickle
from concurrent.futures import ThreadPoolExecutor

# Page Config
st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    with open('movie_data.pkl', 'rb') as file:
        return pickle.load(file)

movies, cosine_sim = load_data()

def fetch_poster(movie_id):
    # This safely pulls the key from your Streamlit settings
    api_key = st.secrets["Ttmdb_api_key"] 
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}'
    try:
        data = requests.get(url, timeout=5).json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
    except:
        pass
    return "https://via.placeholder.com/500x750?text=No+Poster"

def get_recommendations(title):
    idx = movies[movies['title'] == title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    movie_indices = [i[0] for i in sim_scores]
    return movies.iloc[movie_indices]

st.title("🎬 Movie Recommendation System")

selected_movie = st.selectbox("Select a movie:", movies['title'].values)

if st.button('Recommend'):
    recommendations = get_recommendations(selected_movie)
    
    # CORRECTED THREADING: Run inside the button block
    with st.spinner('Fetching posters...'):
        with ThreadPoolExecutor() as executor:
            movie_ids = recommendations['movie_id'].values
    
    st.write("Top 10 recommended movies:")
    
    # Display in 2 rows of 5
    for i in range(0, 10, 5): 
        cols = st.columns(5) 
        for col_idx, j in enumerate(range(i, i + 5)):
            # Create columns for display
            cols = st.columns(5) 

# Instead of a fixed range, use the actual length of the posters we found
        for j in range(len(poster_urls)):
            # This keeps the layout in rows of 5
            with cols[j % 5]:
                st.text(recommendations['title'].iloc[j])
                st.image(poster_urls[j])