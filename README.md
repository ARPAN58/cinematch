# CineMatch Pro 🎬

A movie recommendation system that suggests similar movies based on your preferences. Built with Python, Streamlit, and TMDB API.

## Features
- Movie recommendations based on content similarity
- Modern, responsive UI with dark theme
- Movie details including ratings, cast, and overview
- Interactive user interface

## Setup
1. Clone the repository
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Get a TMDB API key from [TMDB](https://www.themoviedb.org/settings/api)
4. Run the app:
   ```bash
   streamlit run app.py
   ```

## Requirements
- Python 3.7+
- Streamlit
- Pandas
- Scikit-learn
- Requests
- Streamlit-Option-Menu

## Usage
1. Select a movie you like from the dropdown
2. Click "Get Recommendations"
3. Browse through the suggested movies

## Data
Uses TMDB 5000 Movie Dataset for recommendations.

## License
MIT
