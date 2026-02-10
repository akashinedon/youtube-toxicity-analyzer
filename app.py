"""
YouTube Toxicity Analyzer - Enhanced Streamlit Dashboard
With video comparison, reports, and deployment features
"""

import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime
import json

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_collection import YouTubeCommentCollector
from src.toxicity_analyzer import ToxicityAnalyzer
from src.sentiment_analyzer import SentimentAnalyzer
from src.utils import extract_timestamp, format_timestamp, get_comment_stats
from src.visualizations import *
from src.report_generator import generate_html_report, create_summary_dict
from src.video_comparison import compare_videos, create_comparison_chart, create_radar_comparison

# Page configuration
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

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
</style>
""", unsafe_allow_html=True)


def ensure_directories():
    """Create necessary directories"""
    directories = ['data', 'data/raw', 'data/processed', 'reports']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)


@st.cache_resource
def load_toxicity_model():
    """Load and cache the toxicity model"""
    return ToxicityAnalyzer()


@st.cache_resource
def load_sentiment_model():
    """Load and cache the sentiment model"""
    return SentimentAnalyzer()


def save_analysis_to_history(video_info, toxic_stats, sentiment_stats, df):
    """Save analysis to history for comparison"""
    if 'analysis_history' not in st.session_state:
        st.session_state['analysis_history'] = []
    
    analysis_data = {
        'video_info': video_info,
        'toxic_stats': toxic_stats,
        'sentiment_stats': sentiment_stats,
        'total_comments': len(df),
        'timestamp': datetime.now().isoformat()
    }
    
    st.session_state['analysis_history'].append(analysis_data)
    
    # Keep only last 5 analyses
    if len(st.session_state['analysis_history']) > 5:
        st.session_state['analysis_history'].pop(0)


def main():
    """Main application function"""
    
    ensure_directories()
    
    # Header
    st.markdown('<h1 class="main-header">🎥 YouTube Toxicity Analyzer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Analyze comments for toxicity and sentiment using AI</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Mode selection
        mode = st.radio(
            "Analysis Mode",
            options=["Single Video", "Compare Videos"],
            help="Choose to analyze one video or compare multiple"
        )
        
        st.divider()
        
        if mode == "Single Video":
            # Single video mode
            video_url = st.text_input(
                "YouTube Video URL",
                placeholder="https://www.youtube.com/watch?v=...",
                help="Paste any YouTube video URL"
            )
            
            max_comments = st.slider(
                "Number of comments to analyze",
                min_value=10,
                max_value=500,
                value=100,
                step=10,
                help="More comments = more accurate but slower"
            )
            
            analyze_button = st.button("🔍 Analyze Comments", type="primary", use_container_width=True)
            
        else:
            # Compare videos mode
            st.info("Compare up to 3 videos at once!")
            
            video_urls = []
            for i in range(3):
                url = st.text_input(
                    f"Video {i+1} URL",
                    key=f"compare_url_{i}",
                    placeholder=f"https://www.youtube.com/watch?v=..."
                )
                if url:
                    video_urls.append(url)
            
            max_comments = st.slider(
                "Comments per video",
                min_value=50,
                max_value=200,
                value=100,
                step=50
            )
            
            analyze_button = st.button("🔍 Compare Videos", type="primary", use_container_width=True)
        
        st.divider()
        
        # About section
        with st.expander("ℹ️ About This Tool"):
            st.markdown("""
            ### Features
            - 🔍 **AI-Powered Toxicity Detection**
            - 😊 **Sentiment Analysis**
            - ⏰ **Timeline Analysis**
            - 📊 **Interactive Visualizations**
            - 📥 **Export Reports (HTML/CSV)**
            - 🆚 **Compare Multiple Videos**
            
            ### How It Works
            1. Fetches comments via YouTube API
            2. Analyzes toxicity using Detoxify AI
            3. Performs sentiment analysis
            4. Generates insights and visualizations
            """)
        
        # Analysis history
        if 'analysis_history' in st.session_state and st.session_state['analysis_history']:
            with st.expander("📜 Analysis History"):
                for idx, analysis in enumerate(reversed(st.session_state['analysis_history'])):
                    st.markdown(f"**{idx+1}.** {analysis['video_info'].get('title', 'Unknown')[:30]}...")
                    st.caption(f"Toxicity: {analysis['toxic_stats'].get('toxicity_rate', 0):.1f}%")
    
    # Main content
    if mode == "Single Video" and analyze_button and video_url:
        analyze_single_video(video_url, max_comments)
    
    elif mode == "Compare Videos" and analyze_button and len(video_urls) >= 2:
        compare_multiple_videos(video_urls, max_comments)
    
    elif 'df' in st.session_state:
        display_results()
    
    else:
        show_welcome_screen()


def analyze_single_video(video_url: str, max_comments: int):
    """Analyze a single video"""
    
    if 'youtube.com' not in video_url and 'youtu.be' not in video_url:
        st.error("❌ Please enter a valid YouTube URL")
        return
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Fetch comments
        status_text.text("📥 Step 1/4: Fetching comments...")
        progress_bar.progress(10)
        
        collector = YouTubeCommentCollector()
        video_id = collector.extract_video_id(video_url)
        video_info = collector.get_video_info(video_id)
        
        if not video_info:
            st.error("❌ Could not fetch video information")
            return
        
        comments = collector.get_comments(video_id, max_results=max_comments)
        if not comments:
            st.warning("⚠️ No comments found")
            return
        
        df = collector.comments_to_dataframe(comments)
        progress_bar.progress(30)
        
        # Step 2: Toxicity analysis
        status_text.text("🔍 Step 2/4: Analyzing toxicity...")
        toxicity_analyzer = load_toxicity_model()
        df = toxicity_analyzer.analyze_dataframe(df)
        toxic_stats = toxicity_analyzer.get_statistics(df)
        progress_bar.progress(60)
        
        # Step 3: Sentiment analysis
        status_text.text("😊 Step 3/4: Analyzing sentiment...")
        sentiment_analyzer = load_sentiment_model()
        df = sentiment_analyzer.analyze_dataframe(df)
        sentiment_stats = sentiment_analyzer.get_statistics(df)
        progress_bar.progress(80)
        
        # Step 4: Finalize
        status_text.text("⏰ Step 4/4: Generating visualizations...")
        df['timestamp'] = df['text'].apply(extract_timestamp)
        
        # Save
        output_path = f"data/processed/analysis_{video_id}.csv"
        df.to_csv(output_path, index=False)
        
        progress_bar.progress(100)
        status_text.text("✅ Analysis complete!")
        
        # Store in session state
        st.session_state['df'] = df
        st.session_state['toxic_stats'] = toxic_stats
        st.session_state['sentiment_stats'] = sentiment_stats
        st.session_state['video_info'] = video_info
        st.session_state['output_path'] = output_path
        
        # Save to history
        save_analysis_to_history(video_info, toxic_stats, sentiment_stats, df)
        
        # Auto-rerun to display results
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")


def compare_multiple_videos(video_urls: List[str], max_comments: int):
    """Compare multiple videos"""
    
    st.subheader("🆚 Video Comparison")
    
    comparison_results = []
    
    for idx, url in enumerate(video_urls):
        with st.expander(f"📹 Video {idx+1}", expanded=True):
            try:
                collector = YouTubeCommentCollector()
                video_id = collector.extract_video_id(url)
                video_info = collector.get_video_info(video_id)
                
                st.write(f"**{video_info.get('title', 'Unknown')}**")
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
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Comments", len(df))
                    col2.metric("Toxicity", f"{toxic_stats.get('toxicity_rate', 0):.1f}%")
                    col3.metric("Positive", f"{sentiment_stats.get('positive_rate', 0):.1f}%")
                
            except Exception as e:
                st.error(f"Error analyzing video {idx+1}: {str(e)}")
    
    if len(comparison_results) >= 2:
        st.divider()
        
        # Create comparison
        comparison_df = compare_videos(comparison_results)
        
        st.subheader("📊 Comparison Results")
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)
        
        # Comparison charts
        col1, col2 = st.columns(2)
        
        with col1:
            fig_comparison = create_comparison_chart(comparison_df)
            st.plotly_chart(fig_comparison, use_container_width=True)
        
        with col2:
            fig_radar = create_radar_comparison(comparison_df)
            st.plotly_chart(fig_radar, use_container_width=True)


def display_results():
    """Display analysis results"""
    
    df = st.session_state['df']
    toxic_stats = st.session_state['toxic_stats']
    sentiment_stats = st.session_state['sentiment_stats']
    video_info = st.session_state['video_info']
    
    # Video info
    st.subheader("📹 Video Information")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Title", video_info.get('title', 'Unknown')[:40] + "...")
    with col2:
        st.metric("Channel", video_info.get('channel', 'Unknown'))
    with col3:
        st.metric("Views", f"{video_info.get('view_count', 0):,}")
    
    st.divider()
    
    # Key metrics
    st.subheader("📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Comments", len(df))
    with col2:
        st.metric("Toxicity Rate", f"{toxic_stats.get('toxicity_rate', 0):.1f}%",
                 delta=f"{toxic_stats.get('toxic_comments', 0)} toxic")
    with col3:
        st.metric("Positive", f"{sentiment_stats.get('positive_rate', 0):.1f}%")
    with col4:
        st.metric("Timestamps", df['timestamp'].notna().sum())
    
    st.divider()
    
    # Tabs (same as before, keeping your existing tab structure)
    # ... [Keep all your existing tab code from the previous version]
    
    # Export section with HTML report
    st.divider()
    st.subheader("📥 Export Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv = df.to_csv(index=False)
        st.download_button(
            "📄 Download CSV",
            csv,
            f"analysis_{datetime.now():%Y%m%d_%H%M%S}.csv",
            "text/csv",
            use_container_width=True
        )
    
    with col2:
        # Generate HTML report
        html_report = generate_html_report(df, video_info, toxic_stats, sentiment_stats)
        st.download_button(
            "📰 Download HTML Report",
            html_report,
            f"report_{datetime.now():%Y%m%d_%H%M%S}.html",
            "text/html",
            use_container_width=True
        )
    
    with col3:
        # Summary JSON
        summary = create_summary_dict(df, video_info, toxic_stats, sentiment_stats)
        st.download_button(
            "📋 Download Summary (JSON)",
            json.dumps(summary, indent=2),
            f"summary_{datetime.now():%Y%m%d_%H%M%S}.json",
            "application/json",
            use_container_width=True
        )


def show_welcome_screen():
    """Show welcome screen when no analysis"""
    
    st.info("👈 Enter a YouTube video URL in the sidebar to get started!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✨ Features")
        st.markdown("""
        - 🤖 **AI-Powered Analysis** using Detoxify
        - 📊 **Interactive Dashboards** with Plotly
        - ⏰ **Timeline Tracking** for video moments
        - 🆚 **Video Comparison** tool
        - 📥 **Export Reports** in multiple formats
        - 📜 **Analysis History** tracking
        """)
    
    with col2:
        st.subheader("🎬 Sample Videos")
        
        samples = [
            ("First YouTube Video", "https://www.youtube.com/watch?v=jNQXAC9IVRw"),
            ("Popular Music Video", "https://www.youtube.com/watch?v=kJQP7kiw5Fk"),
            ("Educational Content", "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        ]
        
        for title, url in samples:
            with st.expander(f"🎥 {title}"):
                st.code(url)


if __name__ == "__main__":
    main()