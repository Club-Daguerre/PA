import streamlit as st
import pandas as pd
from unidecode import unidecode
import re

# Set page config for a clean look
st.set_page_config(
    page_title="Photo Antiquaria Suchmaschine",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for dark theme and improved search box, including home button
st.markdown("""
    <style>
    /* Dark theme */
    .stApp {
        background-color: #000000;
    }
    
    /* Text colors */
    .stMarkdown, .stText, p, span {
        color: white !important;
    }
    
    /* Header styling */
    h1 {
        color: white !important;
        padding-bottom: 1rem;
        text-align: center !important;
        margin-left: 3rem !important;
    }
    
    /* Description text styling */
    .description {
        text-align: center;
        margin-bottom: 2.5rem !important;
    }
    
    /* Search box container */
    .stTextInput > div {
        display: flex;
        background-color: #262730;
        padding: 5px;
        border-radius: 5px;
        border: 1px solid #4A4A4A;
        margin-top: 1.5rem;
    }
    
    /* Search box */
    .stTextInput input {
        color: white !important;
        background-color: #262730;
        border: none !important;
        caret-color: #1E90FF !important;  /* Bright blue cursor */
    }

    /* Remove the circle in the text input */
    .stTextInput div[data-baseweb="base-input"] > div > div:last-child {
        display: none !important;
    }
    
    /* Remove "Press Enter to Apply" */
    .stTextInput div[data-baseweb="base-input"] {
        width: 100% !important;
    }
    
    .stTextInput [data-testid="stMarkdownContainer"] {
        display: none !important;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #1E90FF;
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        width: 200px !important;
        white-space: nowrap;
        margin: 1rem auto;
        display: block;
    }
    
    .stButton > button:hover {
        background-color: #0066CC;
    }
    
    /* Center button container */
    div[data-testid="column"] {
        text-align: center;
    }
    
    /* Results styling */
    .search-result {
        background-color: #262730;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    
    /* Home button styling */
    .home-button {
        position: absolute;
        top: 0.5rem;
        left: 0.5rem;
        z-index: 999;
        background: rgba(30, 144, 255, 0.1);
        padding: 8px;
        border-radius: 8px;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .home-button a {
        display: flex;
        color: white;
        text-decoration: none !important;
        transition: all 0.3s ease;
    }
    
    .home-button a:hover {
        color: #1E90FF;
        transform: scale(1.1);
    }
    
    /* Prevent external link icon from appearing */
    .home-button a:after {
        display: none !important;
    }
    
    .home-icon {
        width: 28px;
        height: 28px;
    }
    </style>
    """, unsafe_allow_html=True)

# Add home button with larger, more visible SVG icon
home_button_html = """
<div class="home-button">
    <a href="http://www.club-daguerre.de" target="_self" title="Zur Homepage">
        <svg class="home-icon" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
            <path d="M9 22V12h6v10"></path>
        </svg>
    </a>
</div>
"""
st.markdown(home_button_html, unsafe_allow_html=True)

# Title and description with centered alignment
st.title("Photo Antiquaria Suchmaschine")
st.markdown('<p class="description">Durchsuchen Sie die Photo Antiquaria Inhaltsverzeichnisse für die Ausgaben 125-161 (maximal 100 Suchergebnisse)</p>', unsafe_allow_html=True)

# Add extra spacing before search input
st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

# Full-width search input with modified behavior
search_query = st.text_input("Suchbegriff eingeben:", "", key="search_input", on_change=None)

# Centered search button
search_button = st.button("Suchen", key="search_button")

# Load data (in production, this would be done once at startup)
@st.cache_data
def load_data(filename):
    try:
        df = pd.read_excel(filename)
        return df
    except Exception as e:
        st.error(f"Fehler beim Laden der Daten: {str(e)}")
        return None

# Search function
def search_content(df, query):
    if not query:
        return pd.DataFrame()
    
    # Normalize search query and content
    query = unidecode(query.lower())
    
    # Search in all columns
    mask = pd.DataFrame(False, index=df.index, columns=['match'])
    
    for column in df.columns:
        # Convert column to string and normalize
        df[column] = df[column].astype(str)
        normalized_column = df[column].apply(lambda x: unidecode(x.lower()))
        mask['match'] |= normalized_column.str.contains(query, regex=False, na=False)
    
    results = df[mask['match']].copy()
    return results.head(100)

# Main app logic
try:
    df = load_data("photo_antiquaria_index.xlsx")
    
    if df is not None and (search_query and search_button):
        results = search_content(df, search_query)
        
        if not results.empty:
            st.write(f"Gefunden: {len(results)} Ergebnisse")
            
            # Display results with numbering
            for idx, row in enumerate(results.itertuples(), 1):
                # Create a formatted result string and display it in a container
                result_text = f"{idx}. {' | '.join(str(value) for value in row[1:])}"
                st.markdown(f'<div class="search-result">{result_text}</div>', unsafe_allow_html=True)
        else:
            st.info("Keine Ergebnisse gefunden.")

except Exception as e:
    st.error(f"Ein Fehler ist aufgetreten: {str(e)}")