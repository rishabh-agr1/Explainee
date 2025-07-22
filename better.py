import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# --- 1. SERVICE IMPORTS ---
try:
    from services.language_service import handle_language_pipeline
    from services.summary_generator import summarize_article
    from services.location_extractor import extract_locations
    from services.glossary_builder import build_glossary
    from services.file_handler import write_temp_file, delete_temp_file
    REAL_SERVICES_AVAILABLE = True
except ImportError:
    REAL_SERVICES_AVAILABLE = False


# --- 2. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Explainee — AI News Explainer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 3. CUSTOM CSS FOR PROFESSIONAL UI ---
st.markdown("""
<style>
    /* --- General Styles --- */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding: 2rem 3rem; color: #0F172A; }

    /* --- Sidebar Styles --- */
    [data-testid="stSidebar"] {
        background-color: #0F172A;
        width: 380px !important;
        min-width: 380px !important;
    }
    .sidebar-header { padding: 1rem 1rem 1.5rem 1rem; }
    .sidebar-header .brand-title { color: #FFFFFF; font-size: 2.25rem; font-weight: 700; }
    .sidebar-header .brand-tagline { color: #E2E8F0; font-size: 1rem; margin-top: -0.5rem; }
    
    /* --- NEW: Improved Text Input Styling --- */
    .stTextInput > div > div > input {
        background-color: #1E293B;
        color: #FFFFFF; /* User-typed text */
        border: 1px solid #475569; /* Brighter default border */
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    /* NEW: Make placeholder text more visible */
    .stTextInput > div > div > input::placeholder {
        color: #94A3B8;
        opacity: 1;
    }
    /* NEW: Add a highlight when the input is clicked (focused) */
    .stTextInput > div > div > input:focus {
        border-color: #4F8BF9;
        box-shadow: 0 0 0 2px rgba(79, 139, 249, 0.4);
    }
    
    .stRadio > label { color: #FFFFFF !important; }

    .stButton > button { width: 100%; background-color: #4F8BF9; color: white; border-radius: 0.5rem; height: 3rem; }

    /* --- Main Content Styles --- */
    h1, h2, h3 { color: #1E293B; }
    [data-testid="stMetric"] {
        background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 0.75rem;
        padding: 1rem; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
    }
    [data-testid="stMetricLabel"] { font-weight: 500; color: #64748B; }
    [data-testid="stMetricValue"] { color: #0F172A; }
    [data-testid="stMetricDelta"] { color: #475569; }

    /* --- Tabs --- */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; background-color: transparent; border-radius: 8px; padding: 0 16px; }
    .stTabs [aria-selected="true"] { background-color: #FFFFFF; color: #4F8BF9; box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1); }
    
    /* --- Location Tags --- */
    .location-tag {
        display: inline-block; padding: 0.25rem 0.6rem; background-color: #E0E7FF;
        color: #3730A3; border-radius: 0.375rem; font-weight: 500; margin: 0.1rem;
    }

    /* --- Welcome Screen Specific Styles --- */
    .welcome-container { text-align: center; }
    .feature-card { 
        background-color: #FFFFFF; padding: 1.2rem; border-radius: 0.75rem; 
        border: 1px solid #E2E8F0; height: 100%; text-align: left;
    }
</style>
""", unsafe_allow_html=True)


# --- 4. HELPER FUNCTION FOR WELCOME SCREEN ---
def display_welcome_screen():
    """Displays the initial welcome screen before any analysis is done."""
    st.markdown("<div class='welcome-container'>", unsafe_allow_html=True)
    st.title("Welcome to Explainee")
    st.subheader("Your AI-powered assistant for instantly understanding any news article.")
    st.markdown("---")
    
    st.header("How It Works")
    col1, col2, col3 = st.columns(3, gap="large")
    with col1:
        st.markdown("<div class='feature-card'><h4>1. Paste URL</h4><p>Grab any news article link from the web and paste it into the sidebar.</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='feature-card'><h4>2. Click Analyze</h4><p>Hit the 'Analyze' button and let our AI get to work processing the content.</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='feature-card'><h4>3. Get Insights</h4><p>Receive a complete, easy-to-digest breakdown of the article in seconds.</p></div>", unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)

    st.header("Features at a Glance")
    fcol1, fcol2, fcol3 = st.columns(3, gap="large")
    with fcol1:
        st.markdown("<div class='feature-card'><h4>✨ AI-Generated Summary</h4><p>Get the key takeaways and main points without reading the entire article.</p></div>", unsafe_allow_html=True)
    with fcol2:
        st.markdown("<div class='feature-card'><h4>📖 Interactive Glossary</h4><p>Understand key terms, people, and organizations mentioned in the text.</p></div>", unsafe_allow_html=True)
    with fcol3:
        st.markdown("<div class='feature-card'><h4>🌍 Location Highlighting</h4><p>See all mentioned geographical locations pulled from the article text.</p></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# --- 5. SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("""
        <div class='sidebar-header'>
            <p class='brand-title'>Explainee</p>
            <p class='brand-tagline'>AI-powered news article explainer.</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    with st.form(key="url_form"):
        url = st.text_input("Enter a news article URL", label_visibility="collapsed", placeholder="Paste news article URL here...")
        submitted = st.form_submit_button("✨ Analyze Article")

    st.markdown("---")
    language_toggle_placeholder = st.empty()


# --- 6. MAIN PAGE LOGIC ---
if not submitted or not url:
    display_welcome_screen()
    st.stop()


# --- 7. CORE PROCESSING LOGIC ---
try:
    if not REAL_SERVICES_AVAILABLE:
        st.error("Service files are missing. Please ensure they are in the 'services' directory and all required packages are installed.")
        st.stop()
    
    with st.spinner("Fetching and processing article... This may take a moment."):
        # 1. Fetch Article Content
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        title = soup.title.string if soup.title else "No title found"
        source = urlparse(url).netloc
        paragraphs = soup.find_all("p")
        article_text = "\n\n".join(p.get_text().strip() for p in paragraphs if p.get_text().strip())

        if not article_text:
            st.warning("Could not extract any paragraph text from the article. The website might be blocking scrapers or has a non-standard format.")
            st.stop()

        # 2. Language Pipeline
        lang_code, lang_name, translated_path, was_translated = handle_language_pipeline(article_text)
        
        # 3. Read content
        original_path = write_temp_file(article_text)
        with open(translated_path, 'r', encoding='utf-8') as f_en, open(original_path, 'r', encoding='utf-8') as f_orig:
            english_content = f_en.read()
            original_content = f_orig.read()

        # 4. Generate Insights
        summary = summarize_article(translated_path)
        locations = extract_locations(translated_path)
        glossary = build_glossary(translated_path, max_entities=15)
        
        # 5. Cleanup
        delete_temp_file(translated_path)
        delete_temp_file(original_path)

except Exception as e:
    st.error(f"An error occurred. Please check the URL or try another article.")
    st.error(f"Details: {e}")
    st.stop()


# --- 8. DISPLAY RESULTS ---
if was_translated:
    with language_toggle_placeholder.container():
        show_english = st.radio(
            "View Article In:", options=["Original Language", "English"], index=1, horizontal=True)
else:
    show_english = "English" 

st.header(title)
col1, col2, col3 = st.columns(3)
col1.metric("Source", source)
col2.metric("Language", f"{lang_name.split(' ')[0]} ({lang_code})")
col3.metric("Translated to English", "Yes" if was_translated else "No")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📊 Summary & Key Info", "📖 Glossary", "📄 Full Article"])

with tab1:
    st.subheader("Key Takeaways")
    st.write(summary)
    st.markdown("<br>", unsafe_allow_html=True)
    if locations:
        st.subheader("Locations Mentioned")
        location_html = "".join(f"<span class='location-tag'>{loc}</span>" for loc in locations)
        st.markdown(location_html, unsafe_allow_html=True)

with tab2:
    st.subheader("Key People & Organizations")
    if glossary:
        for term, definition in glossary.items():
            st.markdown(f"**{term}**: {definition}")
    else:
        st.info("No key people or organizations were identified in the article.")

with tab3:
    display_lang = 'English' if show_english == 'English' else lang_name
    st.subheader(f"Reading Article in: {display_lang}")
    content_to_show = english_content if show_english == "English" else original_content
    with st.container(height=500):
        for para in content_to_show.split("\n\n"):
            st.markdown(
                f"<p style='text-align: justify; line-height: 1.7; margin-bottom: 1em;'>{para.strip()}</p>",
                unsafe_allow_html=True,
            )