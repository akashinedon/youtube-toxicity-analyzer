"""
YouTube Comment Collection Module
Fetches comments from YouTube videos using the official API
"""

import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
from dotenv import load_dotenv
from typing import List, Dict, Optional
import time

# Load environment variables
load_dotenv()

class YouTubeCommentCollector:
    """
    Collects comments from YouTube videos using the Data API v3
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the YouTube API client

        Args:
            api_key: YouTube Data API key. If None, loads from .env or Streamlit secrets
        """
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')

        # Fallback: try Streamlit secrets (for Streamlit Cloud deployment)
        if not self.api_key:
            try:
                import streamlit as st
                self.api_key = st.secrets.get('YOUTUBE_API_KEY')
            except Exception:
                pass

        if not self.api_key:
            raise ValueError(
                "YouTube API key not found! "
                "Set YOUTUBE_API_KEY in .env file or Streamlit secrets."
            )
        
        # Build YouTube API client
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        print("✅ YouTube API client initialized successfully!")
    
    def extract_video_id(self, url: str) -> str:
        """
        Extract video ID from YouTube URL
        
        Args:
            url: YouTube video URL
            
        Returns:
            video_id: 11-character video ID
            
        Examples:
            https://www.youtube.com/watch?v=dQw4w9WgXcQ -> dQw4w9WgXcQ
            https://youtu.be/dQw4w9WgXcQ -> dQw4w9WgXcQ
        """
        if 'youtube.com/watch?v=' in url:
            return url.split('v=')[1].split('&')[0]
        elif 'youtu.be/' in url:
            return url.split('youtu.be/')[1].split('?')[0]
        else:
            # Assume it's already a video ID
            return url
    
    def get_video_info(self, video_id: str) -> Dict:
        """
        Get basic information about a video
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dictionary with video metadata
        """
        try:
            request = self.youtube.videos().list(
                part='snippet,statistics',
                id=video_id
            )
            response = request.execute()
            
            if not response['items']:
                raise ValueError(f"Video {video_id} not found!")
            
            video = response['items'][0]
            
            return {
                'video_id': video_id,
                'title': video['snippet']['title'],
                'channel': video['snippet']['channelTitle'],
                'published_at': video['snippet']['publishedAt'],
                'view_count': int(video['statistics'].get('viewCount', 0)),
                'like_count': int(video['statistics'].get('likeCount', 0)),
                'comment_count': int(video['statistics'].get('commentCount', 0))
            }
        
        except HttpError as e:
            print(f"❌ Error fetching video info: {e}")
            return {}
    
    def get_comments(
        self, 
        video_id: str, 
        max_results: int = 1000,
        order: str = 'relevance'
    ) -> List[Dict]:
        """
        Fetch comments from a YouTube video
        
        Args:
            video_id: YouTube video ID
            max_results: Maximum number of comments to fetch
            order: Sort order ('time', 'relevance')
            
        Returns:
            List of comment dictionaries
        """
        comments = []
        next_page_token = None
        
        print(f"📥 Fetching comments for video: {video_id}")
        print(f"   Requested: {max_results} comments")
        
        try:
            while len(comments) < max_results:
                # Request comments
                request = self.youtube.commentThreads().list(
                    part='snippet,replies',
                    videoId=video_id,
                    maxResults=min(100, max_results - len(comments)),
                    pageToken=next_page_token,
                    order=order,
                    textFormat='plainText'
                )
                
                response = request.execute()
                
                # Extract comment data
                for item in response['items']:
                    # Top-level comment
                    top_comment = item['snippet']['topLevelComment']['snippet']
                    
                    comment_data = {
                        'comment_id': item['id'],
                        'video_id': video_id,
                        'author': top_comment['authorDisplayName'],
                        'text': top_comment['textDisplay'],
                        'like_count': top_comment['likeCount'],
                        'published_at': top_comment['publishedAt'],
                        'updated_at': top_comment['updatedAt'],
                        'reply_count': item['snippet']['totalReplyCount'],
                        'is_reply': False
                    }
                    
                    comments.append(comment_data)
                    
                    # Get replies if they exist
                    if 'replies' in item:
                        for reply in item['replies']['comments']:
                            reply_snippet = reply['snippet']
                            
                            reply_data = {
                                'comment_id': reply['id'],
                                'video_id': video_id,
                                'author': reply_snippet['authorDisplayName'],
                                'text': reply_snippet['textDisplay'],
                                'like_count': reply_snippet['likeCount'],
                                'published_at': reply_snippet['publishedAt'],
                                'updated_at': reply_snippet['updatedAt'],
                                'reply_count': 0,
                                'is_reply': True,
                                'parent_id': item['id']
                            }
                            
                            comments.append(reply_data)
                
                # Check for more pages
                next_page_token = response.get('nextPageToken')
                
                if not next_page_token:
                    break
                
                # Progress update
                print(f"   Fetched: {len(comments)} comments...")
                
                # Rate limiting (be nice to the API)
                time.sleep(0.1)
        
        except HttpError as e:
            if 'commentsDisabled' in str(e):
                print(f"❌ Comments are disabled for this video")
            else:
                print(f"❌ Error fetching comments: {e}")
        
        print(f"✅ Successfully fetched {len(comments)} comments!")
        return comments[:max_results]
    
    def comments_to_dataframe(self, comments: List[Dict]) -> pd.DataFrame:
        """
        Convert comment list to pandas DataFrame
        
        Args:
            comments: List of comment dictionaries
            
        Returns:
            pandas DataFrame
        """
        df = pd.DataFrame(comments)
        
        if not df.empty:
            # Convert timestamps to datetime
            df['published_at'] = pd.to_datetime(df['published_at'])
            df['updated_at'] = pd.to_datetime(df['updated_at'])
            
            # Sort by likes (most popular first)
            df = df.sort_values('like_count', ascending=False).reset_index(drop=True)
        
        return df
    
    def save_comments(
        self, 
        comments: List[Dict], 
        filename: str,
        format: str = 'csv'
    ):
        """
        Save comments to file
        
        Args:
            comments: List of comment dictionaries
            filename: Output filename (without extension)
            format: File format ('csv' or 'json')
        """
        df = self.comments_to_dataframe(comments)
        
        if format == 'csv':
            filepath = f"data/raw/{filename}.csv"
            df.to_csv(filepath, index=False)
            print(f"💾 Saved {len(df)} comments to {filepath}")
        
        elif format == 'json':
            filepath = f"data/raw/{filename}.json"
            df.to_json(filepath, orient='records', indent=2)
            print(f"💾 Saved {len(df)} comments to {filepath}")
        
        else:
            raise ValueError(f"Unsupported format: {format}")


# Example usage (for testing)
if __name__ == "__main__":
    # Initialize collector
    collector = YouTubeCommentCollector()
    
    # Test with a popular video
    test_video_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # "Me at the zoo" (first YouTube video)
    
    # Extract video ID
    video_id = collector.extract_video_id(test_video_url)
    print(f"\n📹 Video ID: {video_id}")
    
    # Get video info
    video_info = collector.get_video_info(video_id)
    print(f"\n📊 Video Info:")
    for key, value in video_info.items():
        print(f"   {key}: {value}")
    
    # Fetch comments
    comments = collector.get_comments(video_id, max_results=100)
    
    # Convert to DataFrame
    df = collector.comments_to_dataframe(comments)
    print(f"\n📋 Comments DataFrame:")
    print(df.head())
    print(f"\nShape: {df.shape}")
    
    # Save to file
    collector.save_comments(comments, filename='test_comments', format='csv')
    
    print("\n✅ Test completed successfully!")