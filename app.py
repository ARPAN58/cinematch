import streamlit as st
import pickle
import pandas as pd
import requests
from streamlit_option_menu import option_menu
import base64

# Page configuration
st.set_page_config(
    page_title="CineMatch Pro",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
    <style>
    :root {
        --primary-color: #1E1E2D;
        --secondary-color: #2B2B40;
        --accent-color: #F64E60;
        --text-color: #FFFFFF;
        --text-secondary: #A4A4B8;
    }
    
    .stApp {
        background-color: var(--primary-color);
        color: var(--text-color);
    }
    
    .st-bw {
        color: var(--text-color) !important;
    }
    
    .st-bv {
        background-color: var(--secondary-color) !important;
    }
    
    .stButton>button {
        background-color: var(--accent-color);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stButton>button:hover {
        background-color: #EE2D41;
        color: white;
    }
    
    .movie-card {
        background-color: var(--secondary-color);
        border-radius: 10px;
        padding: 1rem;
        transition: transform 0.3s;
    }
    
    .movie-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
    }
    
    .section-title {
        color: var(--text-color);
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .sidebar .sidebar-content {
        background-color: var(--secondary-color);
    }
    
    </style>
""", unsafe_allow_html=True)

def fetch_movie_details(movie_id):
    api_key = "0ea91c84053ffec34635fe4432c05370"
    try:
        # Get basic movie details
        response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US&append_to_response=credits,videos')
        data = response.json()
        
        # Extract relevant information
        details = {
            'poster': f"https://image.tmdb.org/t/p/w500/{data.get('poster_path', '')}" if data.get('poster_path') else "https://via.placeholder.com/500x750?text=No+Image",
            'backdrop': f"https://image.tmdb.org/t/p/w1280/{data.get('backdrop_path', '')}" if data.get('backdrop_path') else None,
            'title': data.get('title', 'Unknown'),
            'year': data.get('release_date', '')[:4] if data.get('release_date') else 'N/A',
            'rating': round(data.get('vote_average', 0), 1),
            'overview': data.get('overview', 'No overview available.'),
            'genres': [genre['name'] for genre in data.get('genres', [])],
            'director': next((member['name'] for member in data.get('credits', {}).get('crew', []) 
                            if member.get('job') == 'Director'), 'N/A'),
            'cast': [{'name': member['name'], 'character': member.get('character', '')} 
                    for member in data.get('credits', {}).get('cast', [])[:5]],
            'trailer': next((f"https://www.youtube.com/watch?v={video['key']}" 
                           for video in data.get('videos', {}).get('results', []) 
                           if video['site'] == 'YouTube' and video['type'] == 'Trailer'), None)
        }
        return details
    except Exception as e:
        print(f"Error fetching movie details: {e}")
        return {
            'poster': "https://via.placeholder.com/500x750?text=No+Image",
            'title': 'Unknown',
            'year': 'N/A',
            'rating': 0,
            'overview': 'No details available.',
            'genres': [],
            'director': 'N/A',
            'cast': [],
            'trailer': None
        }

def get_recommendations(movie_title, num_recommendations=5):
    try:
        movie_index = movies[movies['title'] == movie_title].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:num_recommendations+1]
        
        recommended_movies = []
        for i in movies_list:
            movie_id = movies.iloc[i[0]].movie_id
            movie_title = movies.iloc[i[0]].title
            recommended_movies.append((movie_id, movie_title))
            
        return recommended_movies
    except Exception as e:
        print(f"Error getting recommendations: {e}")
        return []

# Load data
@st.cache_data
def load_data():
    with open('movies_list.pkl', 'rb') as f:
        movies_dict = pickle.load(f)
    with open('similarity.pkl', 'rb') as f:
        similarity = pickle.load(f)
    return pd.DataFrame(movies_dict), similarity

movies, similarity = load_data()

# Sidebar Navigation
with st.sidebar:
    st.image("https://via.placeholder.com/200x50?text=CineMatch+Pro", width=200)
    
    selected = option_menu(
        menu_title=None,
        options=["Home", "Discover", "My Watchlist", "Trending", "Settings"],
        icons=["house", "compass", "bookmark-heart", "fire", "gear"],
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#2B2B40"},
            "icon": {"color": "#F64E60", "font-size": "1.2rem"},
            "nav-link": {
                "font-size": "1rem",
                "text-align": "left",
                "margin": "0",
                "--hover-color": "#3A3A5A",
            },
            "nav-link-selected": {"background-color": "#F64E60"},
        },
    )

# Main Content
if selected == "Home":
    # Hero Section
    st.markdown("""
    <div style='padding: 2rem; background: linear-gradient(135deg, #1E1E2D 0%, #2B2B40 100%); 
                border-radius: 10px; margin-bottom: 2rem;'>
        <h1 style='color: white; margin-bottom: 0.5rem;'>Welcome to CineMatch Pro</h1>
        <p style='color: #A4A4B8; font-size: 1.1rem;'>Discover your next favorite movie with our AI-powered recommendation engine</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Search and Recommendations Section
    st.markdown("<h2 class='section-title'>Find Your Next Movie</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_movie = st.selectbox(
            'Select a movie you like:',
            movies['title'].values,
            key="movie_selector"
        )
    with col2:
        st.write("")
        st.write("")
        recommend_btn = st.button("Get Recommendations", key="recommend_btn")
    
    if recommend_btn and selected_movie:
        with st.spinner('Analyzing your selection...'):
            recommended_movies = get_recommendations(selected_movie, 5)
            
            if recommended_movies:
                st.markdown(f"<h3 style='color: white; margin-top: 2rem;'>Because you liked <span style='color: #F64E60'>{selected_movie}</span></h3>", unsafe_allow_html=True)
                
                # Display recommended movies in a responsive grid
                cols = st.columns(5)
                for idx, (movie_id, title) in enumerate(recommended_movies):
                    with cols[idx % 5]:
                        movie_details = fetch_movie_details(movie_id)
                        st.markdown(f"""
                        <div class='movie-card'>
                            <img src='{movie_details['poster']}' style='width: 100%; border-radius: 8px; margin-bottom: 0.5rem;'>
                            <div style='padding: 0.5rem 0;'>
                                <div style='font-weight: 600; color: white; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>{title}</div>
                                <div style='display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem;'>
                                    <span style='background: #F64E60; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem;'>{movie_details['rating']} ★</span>
                                    <span style='color: #A4A4B8; font-size: 0.9rem;'>{movie_details['year']}</span>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

# Add other sections for the navigation
elif selected == "Discover":
    st.markdown("<h2 class='section-title'>Discover New Movies</h2>", unsafe_allow_html=True)
    st.write("Browse through our curated collections and discover hidden gems.")
    
elif selected == "My Watchlist":
    st.markdown("<h2 class='section-title'>My Watchlist</h2>", unsafe_allow_html=True)
    st.write("Your saved movies will appear here.")
    
elif selected == "Trending":
    st.markdown("<h2 class='section-title'>Trending Now</h2>", unsafe_allow_html=True)
    st.write("See what's popular right now.")
    
elif selected == "Settings":
    st.markdown("<h2 class='section-title'>Settings</h2>", unsafe_allow_html=True)
    st.write("Customize your CineMatch experience.")
    
    # Add some settings options
    st.subheader("Appearance")
    theme = st.radio("Theme", ["Dark", "Light"], index=0)
    
    st.subheader("Notifications")
    email_notifications = st.checkbox("Email notifications", value=True)
    
    if st.button("Save Preferences"):
        st.success("Preferences saved successfully!")
