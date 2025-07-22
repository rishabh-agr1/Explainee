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

# --- Initialize Session State ---
if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False
    st.session_state.article_data = {}

# --- 2. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Explainee — AI News Explainer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 3. HELPER FUNCTION FOR WELCOME SCREEN ---
# Unchanged, hidden for brevity
def display_welcome_screen():
    st.markdown("<div class='welcome-container'>...</div>", unsafe_allow_html=True)


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


# --- 4. SIDEBAR & FORM SUBMISSION LOGIC ---
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

# --- 5. CORE PROCESSING LOGIC ---
if submitted and url:
    try:
        if not REAL_SERVICES_AVAILABLE:
            st.error("Service files are missing.")
            st.stop()
        
        with st.spinner("Fetching and processing article... This may take a few moments."):
            # Step 1: Fetch and parse
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            article_text = "\n\n".join(p.get_text().strip() for p in soup.find_all("p") if p.get_text().strip())
            if not article_text:
                st.warning("Could not extract paragraph text.")
                st.stop()

            # Step 2: Handle language and get file paths
            lang_code, lang_name, translated_path, was_translated = handle_language_pipeline(article_text)
            original_path = write_temp_file(article_text)
            
            # --- MODIFIED: Generate insights for BOTH languages ---
            with st.spinner("Generating English insights..."):
                english_summary = summarize_article(translated_path)
                english_glossary = build_glossary(translated_path, max_entities=15)
                # English locations are the standard
                locations = extract_locations(translated_path)

            original_summary = ""
            original_glossary = {}
            if was_translated:
                with st.spinner(f"Generating {lang_name} insights..."):
                    original_summary = summarize_article(original_path)
                    original_glossary = build_glossary(original_path, max_entities=15)
            else:
                # If not translated, original is the same as English
                original_summary = english_summary
                original_glossary = english_glossary

            # Step 3: Read content for display
            with open(translated_path, 'r', encoding='utf-8') as f_en, open(original_path, 'r', encoding='utf-8') as f_orig:
                english_content = f_en.read()
                original_content = f_orig.read()
            
            # --- MODIFIED: Store all versions in st.session_state ---
            st.session_state.article_data = {
                "title": soup.title.string if soup.title else "No title found",
                "source": urlparse(url).netloc,
                "locations": locations,
                "lang_code": lang_code,
                "lang_name": lang_name,
                "was_translated": was_translated,
                "english_content": english_content,
                "original_content": original_content,
                "english_summary": english_summary,
                "original_summary": original_summary,
                "english_glossary": english_glossary,
                "original_glossary": original_glossary,
            }
            st.session_state.analysis_complete = True
            
            # Step 4: Cleanup
            delete_temp_file(translated_path)
            delete_temp_file(original_path)
            
            st.rerun()

    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.session_state.analysis_complete = False
        st.session_state.article_data = {}

# --- 6. DISPLAY LOGIC ---
if not st.session_state.analysis_complete:
    display_welcome_screen()
    st.stop()

# Retrieve all data from session state
data = st.session_state.article_data

# The radio button toggle
if data['was_translated']:
    with language_toggle_placeholder.container():
        show_english = st.radio(
            "View Insights In:", options=["Original Language", "English"], index=1, horizontal=True)
else:
    show_english = "English" 

# Determine which content to show based on the toggle
if show_english == 'English':
    summary_to_show = data['english_summary']
    glossary_to_show = data['english_glossary']
    content_to_show = data['english_content']
    display_lang = 'English'
else:
    summary_to_show = data['original_summary']
    glossary_to_show = data['original_glossary']
    content_to_show = data['original_content']
    display_lang = data['lang_name']

# --- Display Results ---
st.header(data['title'])
col1, col2, col3 = st.columns(3)
col1.metric("Source", data['source'])
col2.metric("Language", f"{data['lang_name'].split(' ')[0]} ({data['lang_code']})")
col3.metric("Translated", "Yes" if data['was_translated'] else "No")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📊 Summary & Key Info", "📖 Glossary", "📄 Full Article"])

with tab1:
    st.subheader(f"Key Takeaways ({display_lang})")
    st.write(summary_to_show)
    if data['locations']:
        st.subheader("Locations Mentioned (from English text)")
        st.markdown("".join(f"<span class='location-tag'>{loc}</span>" for loc in data['locations']), unsafe_allow_html=True)

with tab2:
    st.subheader(f"Key People & Organizations ({display_lang})")
    if glossary_to_show:
        for term, definition in glossary_to_show.items():
            st.markdown(f"**{term}**: {definition}")
    else:
        st.info("No key entities identified in this language.")

with tab3:
    st.subheader(f"Reading Article in: {display_lang}")
    with st.container(height=500):
        for para in content_to_show.split("\n\n"):
            st.markdown(f"<p style='text-align: justify;'>{para.strip()}</p>", unsafe_allow_html=True)