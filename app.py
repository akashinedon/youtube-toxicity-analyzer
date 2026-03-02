"""
YouTube Toxicity Analyzer - Premium Dark UI
"""

import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime
import json
from typing import List

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_collection import YouTubeCommentCollector
from src.toxicity_analyzer import ToxicityAnalyzer
from src.sentiment_analyzer import SentimentAnalyzer
from src.utils import extract_timestamp, format_timestamp, get_comment_stats
from src.visualizations import *
from src.report_generator import generate_html_report, create_summary_dict
from src.video_comparison import compare_videos, create_comparison_chart, create_radar_comparison

st.set_page_config(
    page_title="YouTube Toxicity Analyzer",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/youtube-toxicity-analyzer',
        'Report a bug': 'https://github.com/yourusername/youtube-toxicity-analyzer/issues',
        'About': '# YouTube Toxicity Analyzer\nAnalyze YouTube comments for toxicity and sentiment using AI.'
    }
)

DARK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Base reset ─────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

.stApp {
    background: #080810;
    color: #e8e8f0;
}

/* ── Scrollbar ──────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #12121e; }
::-webkit-scrollbar-thumb { background: #FF0000; border-radius: 3px; }

/* ── Sidebar ─────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0e0e1a 0%, #080810 100%);
    border-right: 1px solid rgba(255,0,0,0.15);
}

section[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1rem;
}

/* ── Main container ──────────────────────────────── */
.main .block-container {
    padding: 1.5rem 2.5rem 3rem;
    max-width: 1400px;
}

/* ── Hero banner ─────────────────────────────────── */
.hero-banner {
    background: linear-gradient(135deg, #0e0e1a 0%, #1a0505 40%, #0e0e1a 100%);
    border: 1px solid rgba(255,0,0,0.2);
    border-radius: 20px;
    padding: 3rem 2.5rem 2.5rem;
    text-align: center;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}

.hero-banner::before {
    content: '';
    position: absolute;
    top: -80px; left: 50%;
    transform: translateX(-50%);
    width: 600px; height: 300px;
    background: radial-gradient(ellipse, rgba(255,0,0,0.12) 0%, transparent 70%);
    pointer-events: none;
}

.hero-title {
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #ffffff 30%, #FF4444 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 0.6rem;
    letter-spacing: -1px;
}

.hero-subtitle {
    font-size: 1.1rem;
    color: rgba(230,230,255,0.55);
    font-weight: 400;
    margin: 0;
}

.hero-badge {
    display: inline-block;
    background: rgba(255,0,0,0.12);
    border: 1px solid rgba(255,0,0,0.35);
    color: #FF5555;
    border-radius: 999px;
    padding: 4px 14px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}

/* ── Glass card ──────────────────────────────────── */
.glass-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.25rem;
    backdrop-filter: blur(10px);
    transition: border-color 0.2s;
}

.glass-card:hover {
    border-color: rgba(255,0,0,0.2);
}

.glass-card h3 {
    font-size: 0.9rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: rgba(200,200,230,0.6);
    margin: 0 0 1rem;
}

/* ── Metric card ─────────────────────────────────── */
.metric-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.metric-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 1.4rem 1.2rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: all 0.2s;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent, linear-gradient(90deg, #FF0000, #FF4444));
}

.metric-card:hover {
    border-color: rgba(255,0,0,0.25);
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(255,0,0,0.08);
}

.metric-value {
    font-size: 2.2rem;
    font-weight: 800;
    color: #ffffff;
    line-height: 1;
    margin-bottom: 0.3rem;
}

.metric-label {
    font-size: 0.78rem;
    font-weight: 500;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: rgba(180,180,210,0.55);
}

.metric-delta {
    font-size: 0.8rem;
    color: #FF5555;
    margin-top: 0.3rem;
}

.metric-delta.positive { color: #4ade80; }

/* ── Sidebar label ───────────────────────────────── */
.sidebar-section-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: rgba(180,180,220,0.45);
    margin: 1.2rem 0 0.5rem;
}

/* ── Streamlit widget overrides ──────────────────── */
div[data-testid="stTextInput"] > div > div > input,
div[data-testid="stTextArea"] > div > div > textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #e8e8f0 !important;
    font-family: 'Inter', sans-serif !important;
}

div[data-testid="stTextInput"] > div > div > input:focus,
div[data-testid="stTextArea"] > div > div > textarea:focus {
    border-color: rgba(255,0,0,0.4) !important;
    box-shadow: 0 0 0 2px rgba(255,0,0,0.08) !important;
}

/* Radio buttons */
div[data-testid="stRadio"] > div {
    gap: 0.5rem;
}
div[data-testid="stRadio"] label {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 0.5rem 0.8rem !important;
    cursor: pointer;
    transition: all 0.2s;
}
div[data-testid="stRadio"] label:hover {
    border-color: rgba(255,0,0,0.3);
}

/* Slider */
div[data-testid="stSlider"] > div > div > div > div {
    background: #FF0000 !important;
}

/* Primary button */
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #CC0000, #FF2222) !important;
    border: none !important;
    border-radius: 12px !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.02em !important;
    padding: 0.65rem 1.5rem !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 20px rgba(255,0,0,0.25) !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #FF0000, #FF4444) !important;
    box-shadow: 0 6px 28px rgba(255,0,0,0.4) !important;
    transform: translateY(-1px) !important;
}

/* Secondary buttons */
div[data-testid="stButton"] > button[kind="secondary"],
div[data-testid="stDownloadButton"] > button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #e8e8f0 !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
}
div[data-testid="stButton"] > button[kind="secondary"]:hover,
div[data-testid="stDownloadButton"] > button:hover {
    border-color: rgba(255,0,0,0.35) !important;
    background: rgba(255,0,0,0.06) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.02) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    gap: 2px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    padding: 0.5rem 1.2rem !important;
    font-weight: 500 !important;
    color: rgba(200,200,230,0.55) !important;
    border: none !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(255,0,0,0.15) !important;
    color: #FF5555 !important;
}

/* Info / warning / error */
div[data-testid="stAlert"] {
    border-radius: 12px !important;
    border-left: 3px solid rgba(255,0,0,0.5) !important;
    background: rgba(255,0,0,0.06) !important;
}

/* Dataframe */
div[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    overflow: hidden;
}

/* Expander */
details > summary {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 10px !important;
}

/* Divider */
hr { border-color: rgba(255,255,255,0.06) !important; }

/* Progress bar */
div[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #CC0000, #FF2222) !important;
    border-radius: 4px !important;
}

/* Feature list  */
.feature-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-top: 1.5rem;
}

.feature-item {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 1.2rem 1rem;
    text-align: center;
    transition: all 0.2s;
}

.feature-item:hover {
    border-color: rgba(255,0,0,0.25);
    background: rgba(255,0,0,0.04);
    transform: translateY(-2px);
}

.feature-icon { font-size: 1.8rem; margin-bottom: 0.5rem; }
.feature-title { font-size: 0.85rem; font-weight: 600; color: #e8e8f0; margin-bottom: 0.2rem; }
.feature-desc { font-size: 0.75rem; color: rgba(180,180,210,0.5); }

/* Video info card */
.video-info-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,0,0,0.15);
    border-radius: 16px;
    padding: 1.4rem 1.8rem;
    margin-bottom: 1.5rem;
    display: flex;
    gap: 2rem;
    align-items: center;
}

/* sample url tag */
.url-tag {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    padding: 0.4rem 0.8rem;
    font-size: 0.8rem;
    color: rgba(200,200,230,0.6);
    font-family: monospace;
    word-break: break-all;
}

/* Section header */
.section-header {
    font-size: 1.15rem;
    font-weight: 700;
    color: #e8e8f0;
    margin: 1.5rem 0 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.06);
    margin-left: 0.5rem;
}

/* Status tag */
.status-tag {
    display: inline-block;
    border-radius: 999px;
    padding: 3px 12px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.tag-red { background: rgba(255,0,0,0.12); color: #FF5555; border: 1px solid rgba(255,0,0,0.3); }
.tag-green { background: rgba(74,222,128,0.1); color: #4ade80; border: 1px solid rgba(74,222,128,0.25); }
.tag-yellow { background: rgba(250,204,21,0.1); color: #fbbf24; border: 1px solid rgba(250,204,21,0.25); }
</style>
"""

st.markdown(DARK_CSS, unsafe_allow_html=True)

PLOTLY_DARK = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#c8c8e0",
)


def apply_dark_theme(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(14,14,26,0.6)",
        font=dict(family="Inter", color="#c8c8e0"),
        margin=dict(l=40, r=20, t=50, b=40),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.08)")
    return fig


def ensure_directories():
    for d in ['data', 'data/raw', 'data/processed', 'reports']:
        os.makedirs(d, exist_ok=True)


@st.cache_resource
def load_toxicity_model():
    return ToxicityAnalyzer()


@st.cache_resource
def load_sentiment_model():
    return SentimentAnalyzer()


def save_analysis_to_history(video_info, toxic_stats, sentiment_stats, df):
    if 'analysis_history' not in st.session_state:
        st.session_state['analysis_history'] = []
    st.session_state['analysis_history'].append({
        'video_info': video_info,
        'toxic_stats': toxic_stats,
        'sentiment_stats': sentiment_stats,
        'total_comments': len(df),
        'timestamp': datetime.now().isoformat()
    })
    if len(st.session_state['analysis_history']) > 5:
        st.session_state['analysis_history'].pop(0)


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center; padding: 0.5rem 0 1.5rem;'>
            <span style='font-size:2rem;'>🎥</span>
            <div style='font-size:1rem; font-weight:700; color:#e8e8f0; margin-top:4px;'>Toxicity Analyzer</div>
            <div style='font-size:0.7rem; color:rgba(180,180,210,0.45); letter-spacing:0.08em; text-transform:uppercase;'>YouTube AI Tool</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sidebar-section-label">Analysis Mode</div>', unsafe_allow_html=True)
        mode = st.radio(
            "Mode",
            options=["Single Video", "Compare Videos"],
            label_visibility="collapsed"
        )

        st.markdown('<div class="sidebar-section-label">Configuration</div>', unsafe_allow_html=True)

        if mode == "Single Video":
            video_url = st.text_input(
                "YouTube URL",
                placeholder="https://www.youtube.com/watch?v=...",
                label_visibility="collapsed"
            )
            max_comments = st.slider("Comments to analyze", 10, 500, 100, 10)
            analyze_button = st.button("🔍  Analyze Comments", type="primary", use_container_width=True)
        else:
            st.info("Enter 2–3 YouTube URLs to compare side-by-side.")
            video_urls = []
            for i in range(3):
                url = st.text_input(
                    f"Video {i+1}",
                    key=f"cmp_{i}",
                    placeholder=f"Video {i+1} URL...",
                    label_visibility="collapsed"
                )
                if url:
                    video_urls.append(url)
            max_comments = st.slider("Comments per video", 50, 200, 100, 50)
            analyze_button = st.button("🆚  Compare Videos", type="primary", use_container_width=True)
            video_url = None

        st.divider()

        with st.expander("ℹ️ About"):
            st.markdown("""
**How it works**
1. Fetches comments via YouTube Data API v3
2. Detoxify (BERT-based) scores 7 toxicity categories
3. Sentiment analysis (Positive / Negative / Neutral)
4. Interactive charts + export reports
            """)

        if 'analysis_history' in st.session_state and st.session_state['analysis_history']:
            with st.expander("📜 Recent Analyses"):
                for idx, h in enumerate(reversed(st.session_state['analysis_history'])):
                    title = h['video_info'].get('title', 'Unknown')[:28]
                    rate = h['toxic_stats'].get('toxicity_rate', 0)
                    color = "tag-red" if rate > 25 else "tag-yellow" if rate > 10 else "tag-green"
                    st.markdown(f"""
                    <div style='margin-bottom:0.6rem;'>
                        <div style='font-size:0.8rem; color:#e8e8f0; font-weight:500;'>{idx+1}. {title}…</div>
                        <span class='status-tag {color}'>{rate:.1f}% toxic</span>
                    </div>
                    """, unsafe_allow_html=True)

    if mode == "Single Video":
        return mode, video_url, None, max_comments, analyze_button
    else:
        return mode, None, video_urls, max_comments, analyze_button


# ─────────────────────────────────────────────
#  WELCOME SCREEN
# ─────────────────────────────────────────────
def show_welcome_screen():
    st.markdown("""
    <div class="hero-banner">
        <span class="hero-badge">AI-Powered · Real-Time</span>
        <h1 class="hero-title">🎥 YouTube Toxicity Analyzer</h1>
        <p class="hero-subtitle">Uncover the tone, toxicity, and sentiment hidden in any YouTube comment section — powered by BERT AI</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-grid">
        <div class="feature-item">
            <div class="feature-icon">🤖</div>
            <div class="feature-title">AI Toxicity Detection</div>
            <div class="feature-desc">7-category detection via Detoxify (BERT)</div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">😊</div>
            <div class="feature-title">Sentiment Analysis</div>
            <div class="feature-desc">Positive, Negative & Neutral scoring</div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Interactive Charts</div>
            <div class="feature-desc">10+ Plotly visualizations</div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">⏰</div>
            <div class="feature-title">Timeline Analysis</div>
            <div class="feature-desc">Map toxic moments to video timestamps</div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">🆚</div>
            <div class="feature-title">Video Comparison</div>
            <div class="feature-desc">Compare up to 3 videos side-by-side</div>
        </div>
        <div class="feature-item">
            <div class="feature-icon">📥</div>
            <div class="feature-title">Export Reports</div>
            <div class="feature-desc">HTML, CSV & JSON formats</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">🎬 Try These Sample Videos</div>', unsafe_allow_html=True)
    samples = [
        ("First YouTube Video Ever", "https://www.youtube.com/watch?v=jNQXAC9IVRw"),
        ("Despacito – Music Video", "https://www.youtube.com/watch?v=kJQP7kiw5Fk"),
        ("Rick Astley – Never Gonna Give You Up", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
    ]
    cols = st.columns(3)
    for col, (title, url) in zip(cols, samples):
        with col:
            st.markdown(f"""
            <div class='glass-card'>
                <div style='font-size:0.88rem; font-weight:600; color:#e8e8f0; margin-bottom:0.5rem;'>🎥 {title}</div>
                <div class='url-tag'>{url}</div>
            </div>
            """, unsafe_allow_html=True)
            st.code(url, language=None)


# ─────────────────────────────────────────────
#  SINGLE VIDEO ANALYSIS
# ─────────────────────────────────────────────
def analyze_single_video(video_url: str, max_comments: int):
    if 'youtube.com' not in video_url and 'youtu.be' not in video_url:
        st.error("❌ Please enter a valid YouTube URL.")
        return

    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        status_text.markdown("**📥 Step 1/4 — Fetching comments…**")
        progress_bar.progress(5)

        collector = YouTubeCommentCollector()
        video_id = collector.extract_video_id(video_url)
        video_info = collector.get_video_info(video_id)

        if not video_info:
            st.error("❌ Could not fetch video information. Check your API key or URL.")
            return

        comments = collector.get_comments(video_id, max_results=max_comments)
        if not comments:
            st.warning("⚠️ No comments found for this video.")
            return

        df = collector.comments_to_dataframe(comments)
        progress_bar.progress(30)

        status_text.markdown("**🔍 Step 2/4 — Analyzing toxicity…**")
        toxicity_analyzer = load_toxicity_model()
        df = toxicity_analyzer.analyze_dataframe(df)
        toxic_stats = toxicity_analyzer.get_statistics(df)
        progress_bar.progress(58)

        status_text.markdown("**😊 Step 3/4 — Analyzing sentiment…**")
        sentiment_analyzer = load_sentiment_model()
        df = sentiment_analyzer.analyze_dataframe(df)
        sentiment_stats = sentiment_analyzer.get_statistics(df)
        progress_bar.progress(80)

        status_text.markdown("**📊 Step 4/4 — Generating visualizations…**")
        df['timestamp'] = df['text'].apply(extract_timestamp)

        output_path = f"data/processed/analysis_{video_id}.csv"
        df.to_csv(output_path, index=False)

        progress_bar.progress(100)
        status_text.markdown("✅ **Analysis complete!**")

        st.session_state.update({
            'df': df,
            'toxic_stats': toxic_stats,
            'sentiment_stats': sentiment_stats,
            'video_info': video_info,
            'output_path': output_path
        })

        save_analysis_to_history(video_info, toxic_stats, sentiment_stats, df)
        st.rerun()

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")


# ─────────────────────────────────────────────
#  COMPARE VIDEOS
# ─────────────────────────────────────────────
def compare_multiple_videos(video_urls: List[str], max_comments: int):
    st.markdown("""
    <div class="hero-banner">
        <h1 class="hero-title">🆚 Video Comparison</h1>
        <p class="hero-subtitle">Side-by-side toxicity & sentiment comparison across multiple videos</p>
    </div>
    """, unsafe_allow_html=True)

    comparison_results = []

    for idx, url in enumerate(video_urls):
        with st.expander(f"📹 Video {idx+1}", expanded=True):
            try:
                collector = YouTubeCommentCollector()
                video_id = collector.extract_video_id(url)
                video_info = collector.get_video_info(video_id)

                st.markdown(f"**{video_info.get('title', 'Unknown')}**")
                st.caption(f"Channel: {video_info.get('channel', 'Unknown')}")

                with st.spinner(f"Analyzing video {idx+1}..."):
                    comments = collector.get_comments(video_id, max_results=max_comments)
                    df = collector.comments_to_dataframe(comments)

                    toxicity_analyzer = load_toxicity_model()
                    df = toxicity_analyzer.analyze_dataframe(df)
                    toxic_stats = toxicity_analyzer.get_statistics(df)

                    sentiment_analyzer = load_sentiment_model()
                    df = sentiment_analyzer.analyze_dataframe(df)
                    sentiment_stats = sentiment_analyzer.get_statistics(df)

                    comparison_results.append({
                        'video_info': video_info,
                        'toxic_stats': toxic_stats,
                        'sentiment_stats': sentiment_stats,
                        'total_comments': len(df)
                    })

                    c1, c2, c3 = st.columns(3)
                    c1.metric("Comments", len(df))
                    c2.metric("Toxicity", f"{toxic_stats.get('toxicity_rate', 0):.1f}%")
                    c3.metric("Positive", f"{sentiment_stats.get('positive_rate', 0):.1f}%")

            except Exception as e:
                st.error(f"Error analyzing video {idx+1}: {str(e)}")

    if len(comparison_results) >= 2:
        st.divider()
        comparison_df = compare_videos(comparison_results)

        st.markdown('<div class="section-header">📊 Comparison Table</div>', unsafe_allow_html=True)
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)

        col1, col2 = st.columns(2)
        with col1:
            fig = apply_dark_theme(create_comparison_chart(comparison_df))
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = apply_dark_theme(create_radar_comparison(comparison_df))
            st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────
#  RESULTS DISPLAY
# ─────────────────────────────────────────────
def display_results():
    df = st.session_state['df']
    toxic_stats = st.session_state['toxic_stats']
    sentiment_stats = st.session_state['sentiment_stats']
    video_info = st.session_state['video_info']

    toxicity_rate = toxic_stats.get('toxicity_rate', 0)
    if toxicity_rate > 40:
        level_tag = "<span class='status-tag tag-red'>🔴 High Toxicity</span>"
    elif toxicity_rate > 15:
        level_tag = "<span class='status-tag tag-yellow'>🟡 Moderate Toxicity</span>"
    else:
        level_tag = "<span class='status-tag tag-green'>🟢 Low Toxicity</span>"

    title_trunc = video_info.get('title', 'Unknown')
    if len(title_trunc) > 55:
        title_trunc = title_trunc[:55] + "…"

    st.markdown(f"""
    <div class="hero-banner" style='padding:2rem 2rem 1.8rem;'>
        <div style='display:flex; align-items:center; gap:1rem; flex-wrap:wrap; justify-content:center;'>
            <div>
                <div style='font-size:1.5rem; font-weight:800; color:#fff; margin-bottom:4px;'>{title_trunc}</div>
                <div style='color:rgba(200,200,230,0.5); font-size:0.9rem;'>
                    📺 {video_info.get('channel','Unknown')} &nbsp;|&nbsp; 
                    👁 {int(video_info.get('view_count',0)):,} views
                </div>
            </div>
            {level_tag}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─── Metric cards ───
    pos_rate = sentiment_stats.get('positive_rate', 0)
    neg_rate = sentiment_stats.get('negative_rate', 0)
    ts_count = int(df['timestamp'].notna().sum())
    total = len(df)

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card" style="--accent: #3b82f6;">
            <div class="metric-value">{total:,}</div>
            <div class="metric-label">Comments Analyzed</div>
        </div>
        <div class="metric-card" style="--accent: linear-gradient(90deg,#FF0000,#FF4444);">
            <div class="metric-value">{toxicity_rate:.1f}%</div>
            <div class="metric-label">Toxicity Rate</div>
            <div class="metric-delta">{toxic_stats.get('toxic_comments',0)} toxic comments</div>
        </div>
        <div class="metric-card" style="--accent: #4ade80;">
            <div class="metric-value">{pos_rate:.1f}%</div>
            <div class="metric-label">Positive Sentiment</div>
            <div class="metric-delta positive">😊 positive community</div>
        </div>
        <div class="metric-card" style="--accent: #a855f7;">
            <div class="metric-value">{ts_count}</div>
            <div class="metric-label">Timestamped Comments</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─── Tabs ───
    tab_overview, tab_toxic, tab_sentiment, tab_timeline, tab_words, tab_raw, tab_export = st.tabs([
        "📊 Overview",
        "☠️ Toxic Comments",
        "😊 Sentiment",
        "⏰ Timeline",
        "🔤 Word Analysis",
        "📋 Raw Data",
        "📥 Export",
    ])

    # ── Overview ──
    with tab_overview:
        col1, col2 = st.columns(2)
        with col1:
            fig = apply_dark_theme(create_toxicity_gauge(toxicity_rate))
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = apply_dark_theme(create_toxicity_distribution(df))
            st.plotly_chart(fig, use_container_width=True)

        st.plotly_chart(apply_dark_theme(create_toxicity_by_category(df)), use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            st.markdown('<div class="section-header">📈 Toxicity Levels</div>', unsafe_allow_html=True)
            level_counts = df['toxicity_level'].value_counts()
            for lvl, cnt in level_counts.items():
                pct = cnt / total * 100
                tag_cls = {"very_high": "tag-red", "high": "tag-red", "moderate": "tag-yellow"}.get(lvl, "tag-green")
                st.markdown(f"""
                <div style='display:flex; align-items:center; justify-content:space-between; 
                            margin-bottom:0.5rem; padding: 0.4rem 0.8rem; 
                            background:rgba(255,255,255,0.02); border-radius:8px;'>
                    <span class='status-tag {tag_cls}'>{lvl.replace("_"," ").title()}</span>
                    <span style='color:#e8e8f0; font-weight:600;'>{cnt} <span style="color:rgba(180,180,210,0.4)">({pct:.1f}%)</span></span>
                </div>""", unsafe_allow_html=True)
        with col4:
            fig = apply_dark_theme(create_engagement_scatter(df))
            st.plotly_chart(fig, use_container_width=True)

    # ── Toxic Comments ──
    with tab_toxic:
        n_top = st.slider("Show top N toxic comments", 5, 50, 15, key="n_top")
        toxic_table = create_top_toxic_table(df, n=n_top)

        st.markdown('<div class="section-header">🔴 Most Toxic Comments</div>', unsafe_allow_html=True)

        for _, row in toxic_table.iterrows():
            toxicity_pct = row['Toxicity (%)']
            tag_cls = "tag-red" if toxicity_pct > 60 else "tag-yellow" if toxicity_pct > 35 else "tag-green"
            st.markdown(f"""
            <div class='glass-card' style='border-color:rgba(255,0,0,0.12);'>
                <div style='display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.6rem;'>
                    <span style='font-size:0.82rem; font-weight:600; color:rgba(180,180,210,0.6);'>👤 {row['Author']}</span>
                    <div style='display:flex; gap:0.5rem; align-items:center;'>
                        <span style='font-size:0.78rem; color:rgba(180,180,210,0.4);'>👍 {row.get('Likes',0)}</span>
                        <span class='status-tag {tag_cls}'>{toxicity_pct:.1f}%</span>
                    </div>
                </div>
                <div style='font-size:0.9rem; color:#c8c8e0; line-height:1.5;'>{row['Comment']}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-header">📊 Category Breakdown</div>', unsafe_allow_html=True)
        fig = apply_dark_theme(create_toxicity_by_category(df))
        st.plotly_chart(fig, use_container_width=True)

    # ── Sentiment ──
    with tab_sentiment:
        col1, col2 = st.columns(2)
        with col1:
            fig = apply_dark_theme(create_sentiment_pie(sentiment_stats))
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.markdown('<div class="section-header">📊 Sentiment Breakdown</div>', unsafe_allow_html=True)
            for sentiment, key_r, key_c in [
                ("Positive 😊", "positive_rate", "positive_comments"),
                ("Negative 😞", "negative_rate", "negative_comments"),
                ("Neutral 😐", "neutral_rate", "neutral_comments"),
            ]:
                rate = sentiment_stats.get(key_r, 0)
                count = sentiment_stats.get(key_c, 0)
                bar_color = "#4ade80" if "Positive" in sentiment else "#ef4444" if "Negative" in sentiment else "#94a3b8"
                st.markdown(f"""
                <div style='margin-bottom:0.8rem;'>
                    <div style='display:flex; justify-content:space-between; margin-bottom:4px;'>
                        <span style='font-size:0.85rem; color:#e8e8f0;'>{sentiment}</span>
                        <span style='font-size:0.85rem; color:rgba(180,180,210,0.6);'>{count} ({rate:.1f}%)</span>
                    </div>
                    <div style='height:6px; background:rgba(255,255,255,0.06); border-radius:999px; overflow:hidden;'>
                        <div style='width:{rate}%; height:100%; background:{bar_color}; border-radius:999px;'></div>
                    </div>
                </div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-header">📊 Comment Length by Toxicity</div>', unsafe_allow_html=True)
        fig = apply_dark_theme(create_comment_length_analysis(df))
        st.plotly_chart(fig, use_container_width=True)

    # ── Timeline ──
    with tab_timeline:
        ts_count = int(df['timestamp'].notna().sum())
        if ts_count == 0:
            st.info("No timestamped comments found. Viewers didn't reference specific moments in this video.")
        else:
            st.success(f"Found **{ts_count}** comments referencing specific video timestamps.")
            fig = apply_dark_theme(create_timeline_chart(df))
            st.plotly_chart(fig, use_container_width=True)

            ts_df = df[df['timestamp'].notna()][['author', 'text', 'timestamp', 'score_toxicity']].copy()
            ts_df['timestamp'] = ts_df['timestamp'].apply(lambda x: format_timestamp(int(x)) if pd.notna(x) else None)
            ts_df['score_toxicity'] = (ts_df['score_toxicity'] * 100).round(1)
            ts_df.columns = ['Author', 'Comment', 'Timestamp', 'Toxicity (%)']
            st.dataframe(ts_df, use_container_width=True, hide_index=True)

    # ── Word Analysis ──
    with tab_words:
        col1, col2, col3 = st.columns(3)
        with col1:
            fig = apply_dark_theme(create_word_frequency_chart(df, 'all'))
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = apply_dark_theme(create_word_frequency_chart(df, 'positive'))
            st.plotly_chart(fig, use_container_width=True)
        with col3:
            fig = apply_dark_theme(create_word_frequency_chart(df, 'negative'))
            st.plotly_chart(fig, use_container_width=True)

    # ── Raw Data ──
    with tab_raw:
        display_cols = ['author', 'text', 'like_count', 'score_toxicity',
                        'toxicity_level', 'sentiment', 'score_severe_toxicity',
                        'score_obscene', 'score_insult', 'score_threat']
        display_cols = [c for c in display_cols if c in df.columns]
        search = st.text_input("🔍 Filter comments", placeholder="Search by keyword...")
        filtered = df[df['text'].str.contains(search, case=False, na=False)] if search else df
        st.caption(f"Showing {len(filtered):,} / {total:,} comments")
        st.dataframe(filtered[display_cols], use_container_width=True, hide_index=True)

    # ── Export ──
    with tab_export:
        st.markdown('<div class="section-header">📥 Export Your Results</div>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class='glass-card' style='text-align:center;'>
                <div style='font-size:2rem; margin-bottom:0.5rem;'>📄</div>
                <div style='font-weight:600; color:#e8e8f0; margin-bottom:0.3rem;'>CSV Data</div>
                <div style='font-size:0.78rem; color:rgba(180,180,210,0.5); margin-bottom:1rem;'>All analyzed comments with scores</div>
            """, unsafe_allow_html=True)
            csv_data = df.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv_data,
                f"analysis_{datetime.now():%Y%m%d_%H%M%S}.csv",
                "text/csv",
                use_container_width=True
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class='glass-card' style='text-align:center;'>
                <div style='font-size:2rem; margin-bottom:0.5rem;'>📰</div>
                <div style='font-weight:600; color:#e8e8f0; margin-bottom:0.3rem;'>HTML Report</div>
                <div style='font-size:0.78rem; color:rgba(180,180,210,0.5); margin-bottom:1rem;'>Shareable visual report</div>
            """, unsafe_allow_html=True)
            html_report = generate_html_report(df, video_info, toxic_stats, sentiment_stats)
            st.download_button(
                "Download HTML Report",
                html_report,
                f"report_{datetime.now():%Y%m%d_%H%M%S}.html",
                "text/html",
                use_container_width=True
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div class='glass-card' style='text-align:center;'>
                <div style='font-size:2rem; margin-bottom:0.5rem;'>📋</div>
                <div style='font-weight:600; color:#e8e8f0; margin-bottom:0.3rem;'>JSON Summary</div>
                <div style='font-size:0.78rem; color:rgba(180,180,210,0.5); margin-bottom:1rem;'>Machine-readable stats</div>
            """, unsafe_allow_html=True)
            summary = create_summary_dict(df, video_info, toxic_stats, sentiment_stats)
            st.download_button(
                "Download JSON",
                json.dumps(summary, indent=2),
                f"summary_{datetime.now():%Y%m%d_%H%M%S}.json",
                "application/json",
                use_container_width=True
            )
            st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
def main():
    ensure_directories()

    mode, video_url, video_urls, max_comments, analyze_button = render_sidebar()

    if mode == "Single Video" and analyze_button and video_url:
        analyze_single_video(video_url, max_comments)
    elif mode == "Compare Videos" and analyze_button and video_urls and len(video_urls) >= 2:
        compare_multiple_videos(video_urls, max_comments)
    elif 'df' in st.session_state:
        display_results()
    else:
        show_welcome_screen()


if __name__ == "__main__":
    main()