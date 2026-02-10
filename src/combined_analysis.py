"""
Combined Analysis: Fetch comments and analyze toxicity + sentiment
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_collection import YouTubeCommentCollector
from src.toxicity_analyzer import ToxicityAnalyzer
from src.sentiment_analyzer import SentimentAnalyzer
from src.utils import extract_timestamp, get_comment_stats

load_dotenv()


def analyze_video(video_url: str, max_comments: int = 100):
    """
    Complete analysis pipeline for a YouTube video
    """
    
    print("=" * 60)
    print("🎥 YouTube Video Comment Analysis")
    print("=" * 60)
    
    # Step 1: Collect comments
    print("\n📥 Step 1: Collecting Comments...")
    collector = YouTubeCommentCollector()
    video_id = collector.extract_video_id(video_url)
    
    video_info = collector.get_video_info(video_id)
    print(f"\nVideo: {video_info.get('title', 'Unknown')}")
    print(f"Channel: {video_info.get('channel', 'Unknown')}")
    print(f"Views: {video_info.get('view_count', 0):,}")
    
    comments = collector.get_comments(video_id, max_results=max_comments)
    
    if not comments:
        print("❌ No comments found!")
        return None
    
    df = collector.comments_to_dataframe(comments)
    print(f"✅ Collected {len(df)} comments")
    
    # Step 2: Analyze toxicity
    print("\n🔍 Step 2: Analyzing Toxicity...")
    toxicity_analyzer = ToxicityAnalyzer()
    df = toxicity_analyzer.analyze_dataframe(df)
    
    toxic_stats = toxicity_analyzer.get_statistics(df)
    print(f"✅ Toxicity Rate: {toxic_stats['toxicity_rate']:.1f}%")
    print(f"   Toxic Comments: {toxic_stats['toxic_comments']}")
    print(f"   Average Toxicity: {toxic_stats['avg_toxicity']:.2%}")
    
    # Step 3: Analyze sentiment
    print("\n😊 Step 3: Analyzing Sentiment...")
    sentiment_analyzer = SentimentAnalyzer()
    df = sentiment_analyzer.analyze_dataframe(df)
    
    sentiment_stats = sentiment_analyzer.get_statistics(df)
    print(f"✅ Sentiment Breakdown:")
    print(f"   Positive: {sentiment_stats['positive_rate']:.1f}%")
    print(f"   Negative: {sentiment_stats['negative_rate']:.1f}%")
    print(f"   Neutral: {sentiment_stats['neutral_rate']:.1f}%")
    
    # Step 4: Extract timestamps
    print("\n⏰ Step 4: Extracting Timestamps...")
    df['timestamp'] = df['text'].apply(extract_timestamp)
    comments_with_timestamps = df['timestamp'].notna().sum()
    print(f"✅ Found {comments_with_timestamps} comments with timestamps")
    
    # Step 5: Save results
    print("\n💾 Step 5: Saving Results...")
    output_filename = f"analysis_{video_id}"
    output_path = f"data/processed/{output_filename}.csv"
    df.to_csv(output_path, index=False)
    print(f"✅ Saved to: {output_path}")
    
    # Step 6: Show sample toxic comments
    print("\n🚨 Sample Toxic Comments:")
    print("-" * 60)
    toxic_df = toxicity_analyzer.get_toxic_comments(df, threshold=0.5)
    if not toxic_df.empty:
        for idx, row in toxic_df.head(3).iterrows():
            print(f"\n• {row['text'][:100]}...")
            print(f"  Toxicity: {row['score_toxicity']:.1%}")
            print(f"  Author: {row['author']}")
    else:
        print("No toxic comments found (great!)")
    
    # Step 7: Show sample positive comments
    print("\n💚 Sample Positive Comments:")
    print("-" * 60)
    positive_df = df[df['sentiment'] == 'positive'].sort_values('like_count', ascending=False)
    if not positive_df.empty:
        for idx, row in positive_df.head(3).iterrows():
            print(f"\n• {row['text'][:100]}...")
            print(f"  Likes: {row['like_count']}")
            print(f"  Author: {row['author']}")
    else:
        print("No positive comments found")
    
    print("\n" + "=" * 60)
    print("✅ Analysis Complete!")
    print("=" * 60)
    
    return df


if __name__ == "__main__":
    # Test with a sample video
    test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
    
    print("Starting analysis...")
    print(f"Video URL: {test_url}")
    
    results_df = analyze_video(test_url, max_comments=50)
    
    if results_df is not None:
        print(f"\n📊 Final DataFrame shape: {results_df.shape}")
        print(f"Columns: {', '.join(results_df.columns)}")