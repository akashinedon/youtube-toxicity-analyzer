"""
Utility functions for the YouTube Toxicity Analyzer project
"""

import re
from typing import Optional, Dict
import pandas as pd


def extract_timestamp(text: str) -> Optional[int]:
    """
    Extract timestamp from comment text
    Returns timestamp in seconds, or None if not found
    """
    if not text or not isinstance(text, str):
        return None
    
    # Pattern 1: MM:SS or HH:MM:SS
    pattern1 = r'(?:(\d{1,2}):)?(\d{1,2}):(\d{2})'
    match = re.search(pattern1, text)
    
    if match:
        hours = int(match.group(1)) if match.group(1) else 0
        minutes = int(match.group(2))
        seconds = int(match.group(3))
        return hours * 3600 + minutes * 60 + seconds
    
    # Pattern 2: XmYs or Xm Ys
    pattern2 = r'(\d{1,3})m\s*(\d{1,2})s'
    match = re.search(pattern2, text, re.IGNORECASE)
    
    if match:
        minutes = int(match.group(1))
        seconds = int(match.group(2))
        return minutes * 60 + seconds
    
    # Pattern 3: Just Xm
    pattern3 = r'(\d{1,3})m(?!\w)'
    match = re.search(pattern3, text, re.IGNORECASE)
    
    if match:
        minutes = int(match.group(1))
        return minutes * 60
    
    return None


def format_timestamp(seconds: int) -> str:
    """
    Convert seconds to readable timestamp (MM:SS or HH:MM:SS)
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"


def clean_text(text: str) -> str:
    """
    Clean comment text for analysis
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove URLs
    text = re.sub(r'http\S+|www.\S+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Clean up extra spaces
    text = ' '.join(text.split())
    
    return text.strip()


def get_comment_stats(df: pd.DataFrame) -> Dict:
    """
    Calculate statistics about comments
    """
    stats = {
        'total_comments': len(df),
        'unique_authors': df['author'].nunique() if 'author' in df.columns else 0,
        'total_likes': df['like_count'].sum() if 'like_count' in df.columns else 0,
        'avg_likes_per_comment': df['like_count'].mean() if 'like_count' in df.columns else 0,
        'median_likes': df['like_count'].median() if 'like_count' in df.columns else 0,
        'comments_with_timestamps': df['text'].apply(
            lambda x: extract_timestamp(x) is not None
        ).sum() if 'text' in df.columns else 0,
        'reply_count': df['is_reply'].sum() if 'is_reply' in df.columns else 0,
        'avg_comment_length': df['text'].str.len().mean() if 'text' in df.columns else 0,
    }
    
    return stats


if __name__ == "__main__":
    print("Testing utility functions...\n")
    
    # Test timestamp extraction
    test_texts = [
        "This part at 2:35 is funny",
        "3m 20s is the best",
        "Check out 1:23:45",
        "5m mark is great",
        "No timestamp here"
    ]
    
    print("Timestamp Extraction:")
    print("-" * 40)
    for text in test_texts:
        timestamp = extract_timestamp(text)
        if timestamp:
            formatted = format_timestamp(timestamp)
            print(f"'{text}' -> {timestamp}s ({formatted})")
        else:
            print(f"'{text}' -> No timestamp found")
    
    # Test text cleaning
    print("\nText Cleaning:")
    print("-" * 40)
    dirty_text = "Check  this   link: https://example.com  and  email: test@email.com   "
    clean = clean_text(dirty_text)
    print(f"Before: '{dirty_text}'")
    print(f"After:  '{clean}'")
    
    print("\n✅ Utility functions test completed!")