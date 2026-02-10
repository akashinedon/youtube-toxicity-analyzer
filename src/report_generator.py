"""
Report Generator Module
Creates professional HTML reports for YouTube toxicity analysis
"""

import pandas as pd
from datetime import datetime
from typing import Dict, Optional
import numpy as np


def convert_to_serializable(obj):
    """
    Convert numpy types to Python native types for JSON serialization
    
    Args:
        obj: Any object that might contain numpy types
    
    Returns:
        JSON-serializable version of the object
    """
    if isinstance(obj, dict):
        return {key: convert_to_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif pd.isna(obj):
        return None
    else:
        return obj


def generate_html_report(
    df: pd.DataFrame,
    video_info: Dict,
    toxic_stats: Dict,
    sentiment_stats: Dict,
    output_path: Optional[str] = None
) -> str:
    """
    Generate a professional HTML report
    
    Args:
        df: DataFrame with analyzed comments
        video_info: Dictionary with video metadata
        toxic_stats: Dictionary with toxicity statistics
        sentiment_stats: Dictionary with sentiment statistics
        output_path: Optional path to save the HTML file
    
    Returns:
        HTML content as string
    """
    
    # Convert numpy types to Python types
    video_info = convert_to_serializable(video_info)
    toxic_stats = convert_to_serializable(toxic_stats)
    sentiment_stats = convert_to_serializable(sentiment_stats)
    
    # Calculate additional stats
    total_comments = int(len(df))
    toxic_count = int(toxic_stats.get('toxic_comments', 0))
    avg_toxicity = float(toxic_stats.get('avg_toxicity', 0)) * 100
    
    # Get top toxic comments
    top_toxic = df.nlargest(5, 'score_toxicity')[
        ['author', 'text', 'score_toxicity']
    ].to_dict('records')
    
    # Convert numpy types in records
    for record in top_toxic:
        record['score_toxicity'] = float(record['score_toxicity'])
    
    # Get top positive comments
    positive_df = df[df['sentiment'] == 'positive']
    if not positive_df.empty:
        top_positive = positive_df.nlargest(5, 'like_count')[
            ['author', 'text', 'like_count']
        ].to_dict('records')
        # Convert numpy types
        for record in top_positive:
            record['like_count'] = int(record['like_count'])
    else:
        top_positive = []
    
    # Build HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>YouTube Toxicity Analysis Report</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background: #f5f5f5;
                padding: 20px;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            
            .header {{
                text-align: center;
                padding-bottom: 30px;
                border-bottom: 3px solid #3498db;
                margin-bottom: 30px;
            }}
            
            .header h1 {{
                color: #2c3e50;
                font-size: 2.5em;
                margin-bottom: 10px;
            }}
            
            .header .subtitle {{
                color: #7f8c8d;
                font-size: 1.2em;
            }}
            
            .header .date {{
                color: #95a5a6;
                margin-top: 10px;
                font-size: 0.95em;
            }}
            
            .video-info {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 25px;
                border-radius: 8px;
                margin-bottom: 30px;
            }}
            
            .video-info h2 {{
                margin-bottom: 15px;
                font-size: 1.4em;
            }}
            
            .video-info p {{
                margin: 8px 0;
                font-size: 1.1em;
                opacity: 0.95;
            }}
            
            .metrics {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }}
            
            .metric-card {{
                background: white;
                border: 2px solid #ecf0f1;
                padding: 25px;
                border-radius: 10px;
                text-align: center;
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            
            .metric-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            }}
            
            .metric-card.primary {{
                border-color: #3498db;
                background: linear-gradient(135deg, #3498db15 0%, #3498db05 100%);
            }}
            
            .metric-card.danger {{
                border-color: #e74c3c;
                background: linear-gradient(135deg, #e74c3c15 0%, #e74c3c05 100%);
            }}
            
            .metric-card.success {{
                border-color: #2ecc71;
                background: linear-gradient(135deg, #2ecc7115 0%, #2ecc7105 100%);
            }}
            
            .metric-card.warning {{
                border-color: #f39c12;
                background: linear-gradient(135deg, #f39c1215 0%, #f39c1205 100%);
            }}
            
            .metric-card h3 {{
                font-size: 1em;
                color: #7f8c8d;
                margin-bottom: 10px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            .metric-card .value {{
                font-size: 2.8em;
                font-weight: bold;
                color: #2c3e50;
                margin: 10px 0;
            }}
            
            .metric-card.danger .value {{
                color: #e74c3c;
            }}
            
            .metric-card.success .value {{
                color: #2ecc71;
            }}
            
            .metric-card .description {{
                font-size: 0.9em;
                color: #95a5a6;
            }}
            
            .section {{
                margin: 40px 0;
            }}
            
            .section h2 {{
                color: #2c3e50;
                font-size: 1.6em;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 2px solid #3498db;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .comment-list {{
                background: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
            }}
            
            .comment-item {{
                background: white;
                padding: 20px;
                margin-bottom: 15px;
                border-radius: 8px;
                border-left: 5px solid #e74c3c;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                transition: transform 0.2s;
            }}
            
            .comment-item:hover {{
                transform: translateX(5px);
            }}
            
            .comment-item.positive {{
                border-left-color: #2ecc71;
            }}
            
            .comment-item .author {{
                font-weight: bold;
                color: #3498db;
                margin-bottom: 10px;
                font-size: 1.1em;
            }}
            
            .comment-item .author::before {{
                content: "👤 ";
            }}
            
            .comment-item .text {{
                color: #555;
                line-height: 1.6;
                margin-bottom: 12px;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 5px;
            }}
            
            .comment-item .meta {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 0.9em;
                color: #7f8c8d;
            }}
            
            .badge {{
                display: inline-block;
                padding: 5px 12px;
                border-radius: 20px;
                font-size: 0.85em;
                font-weight: bold;
            }}
            
            .badge.danger {{
                background: #e74c3c;
                color: white;
            }}
            
            .badge.success {{
                background: #2ecc71;
                color: white;
            }}
            
            .sentiment-grid {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 20px;
                text-align: center;
                padding: 30px;
                background: #f8f9fa;
                border-radius: 10px;
            }}
            
            .sentiment-item h3 {{
                font-size: 1.2em;
                margin-bottom: 10px;
            }}
            
            .sentiment-item .value {{
                font-size: 2.5em;
                font-weight: bold;
                margin: 10px 0;
            }}
            
            .sentiment-item .count {{
                color: #7f8c8d;
                font-size: 0.95em;
            }}
            
            .sentiment-item.positive h3 {{ color: #2ecc71; }}
            .sentiment-item.positive .value {{ color: #2ecc71; }}
            
            .sentiment-item.negative h3 {{ color: #e74c3c; }}
            .sentiment-item.negative .value {{ color: #e74c3c; }}
            
            .sentiment-item.neutral h3 {{ color: #95a5a6; }}
            .sentiment-item.neutral .value {{ color: #95a5a6; }}
            
            .footer {{
                text-align: center;
                margin-top: 50px;
                padding-top: 30px;
                border-top: 2px solid #ecf0f1;
                color: #7f8c8d;
            }}
            
            .footer h3 {{
                color: #2c3e50;
                margin-bottom: 10px;
            }}
            
            .footer p {{
                margin: 5px 0;
                font-size: 0.95em;
            }}
            
            @media print {{
                body {{
                    background: white;
                    padding: 0;
                }}
                .container {{
                    box-shadow: none;
                    padding: 20px;
                }}
                .comment-item:hover {{
                    transform: none;
                }}
            }}
            
            @media (max-width: 768px) {{
                .metrics {{
                    grid-template-columns: repeat(2, 1fr);
                }}
                .sentiment-grid {{
                    grid-template-columns: 1fr;
                }}
                .header h1 {{
                    font-size: 1.8em;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- Header -->
            <div class="header">
                <h1>🎥 YouTube Toxicity Analysis Report</h1>
                <p class="subtitle">Comprehensive Analysis of Comment Toxicity and Sentiment</p>
                <p class="date">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>
            
            <!-- Video Information -->
            <div class="video-info">
                <h2>📹 Video Information</h2>
                <p><strong>Title:</strong> {video_info.get('title', 'Unknown')}</p>
                <p><strong>Channel:</strong> {video_info.get('channel', 'Unknown')}</p>
                <p><strong>Views:</strong> {video_info.get('view_count', 0):,}</p>
                <p><strong>Total Comments:</strong> {video_info.get('comment_count', 0):,}</p>
            </div>
            
            <!-- Key Metrics -->
            <div class="metrics">
                <div class="metric-card primary">
                    <h3>Total Analyzed</h3>
                    <div class="value">{total_comments}</div>
                    <div class="description">Comments processed</div>
                </div>
                
                <div class="metric-card danger">
                    <h3>Toxic Comments</h3>
                    <div class="value">{toxic_count}</div>
                    <div class="description">{toxic_stats.get('toxicity_rate', 0):.1f}% of total</div>
                </div>
                
                <div class="metric-card success">
                    <h3>Positive Sentiment</h3>
                    <div class="value">{sentiment_stats.get('positive_comments', 0)}</div>
                    <div class="description">{sentiment_stats.get('positive_rate', 0):.1f}% of total</div>
                </div>
                
                <div class="metric-card warning">
                    <h3>Average Toxicity</h3>
                    <div class="value">{avg_toxicity:.1f}%</div>
                    <div class="description">Overall toxicity score</div>
                </div>
            </div>
            
            <!-- Most Toxic Comments -->
            <div class="section">
                <h2>🚨 Most Toxic Comments</h2>
                <div class="comment-list">
    """
    
    # Add toxic comments
    if top_toxic:
        for comment in top_toxic:
            toxicity_percent = float(comment['score_toxicity']) * 100
            text_preview = str(comment['text'])[:300] + ('...' if len(str(comment['text'])) > 300 else '')
            html_content += f"""
                    <div class="comment-item">
                        <div class="author">{comment['author']}</div>
                        <div class="text">{text_preview}</div>
                        <div class="meta">
                            <span class="badge danger">⚠️ Toxicity: {toxicity_percent:.1f}%</span>
                        </div>
                    </div>
            """
    else:
        html_content += """
                    <p style="text-align: center; padding: 30px; color: #7f8c8d;">
                        No toxic comments found! 🎉
                    </p>
        """
    
    html_content += """
                </div>
            </div>
            
            <!-- Most Liked Positive Comments -->
            <div class="section">
                <h2>💚 Most Liked Positive Comments</h2>
                <div class="comment-list">
    """
    
    # Add positive comments
    if top_positive:
        for comment in top_positive:
            text_preview = str(comment['text'])[:300] + ('...' if len(str(comment['text'])) > 300 else '')
            like_count = int(comment['like_count'])
            html_content += f"""
                    <div class="comment-item positive">
                        <div class="author">{comment['author']}</div>
                        <div class="text">{text_preview}</div>
                        <div class="meta">
                            <span class="badge success">❤️ {like_count:,} likes</span>
                        </div>
                    </div>
            """
    else:
        html_content += """
                    <p style="text-align: center; padding: 30px; color: #7f8c8d;">
                        No positive comments found
                    </p>
        """
    
    # Get sentiment stats with proper type conversion
    positive_rate = float(sentiment_stats.get('positive_rate', 0))
    negative_rate = float(sentiment_stats.get('negative_rate', 0))
    neutral_rate = float(sentiment_stats.get('neutral_rate', 0))
    positive_comments = int(sentiment_stats.get('positive_comments', 0))
    negative_comments = int(sentiment_stats.get('negative_comments', 0))
    neutral_comments = int(sentiment_stats.get('neutral_comments', 0))
    
    html_content += f"""
                </div>
            </div>
            
            <!-- Sentiment Breakdown -->
            <div class="section">
                <h2>📊 Sentiment Breakdown</h2>
                <div class="sentiment-grid">
                    <div class="sentiment-item positive">
                        <h3>😊 Positive</h3>
                        <div class="value">{positive_rate:.1f}%</div>
                        <div class="count">{positive_comments} comments</div>
                    </div>
                    <div class="sentiment-item negative">
                        <h3>😞 Negative</h3>
                        <div class="value">{negative_rate:.1f}%</div>
                        <div class="count">{negative_comments} comments</div>
                    </div>
                    <div class="sentiment-item neutral">
                        <h3>😐 Neutral</h3>
                        <div class="value">{neutral_rate:.1f}%</div>
                        <div class="count">{neutral_comments} comments</div>
                    </div>
                </div>
            </div>
            
            <!-- Footer -->
            <div class="footer">
                <h3>YouTube Toxicity Analyzer</h3>
                <p>Powered by Detoxify AI and Natural Language Processing</p>
                <p style="margin-top: 15px; font-size: 0.9em; color: #95a5a6;">
                    This report analyzes comment toxicity, sentiment, and engagement patterns
                    to help content creators understand their audience better.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Save to file if path provided
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ Report saved to: {output_path}")
    
    return html_content


def create_summary_dict(
    df: pd.DataFrame,
    video_info: Dict,
    toxic_stats: Dict,
    sentiment_stats: Dict
) -> Dict:
    """
    Create a summary dictionary for JSON export
    All values are converted to JSON-serializable Python types
    
    Args:
        df: DataFrame with analyzed comments
        video_info: Video metadata
        toxic_stats: Toxicity statistics
        sentiment_stats: Sentiment statistics
    
    Returns:
        Dictionary with analysis summary (JSON-serializable)
    """
    
    # Get timestamp stats
    timestamps_found = 0
    if 'timestamp' in df.columns:
        timestamps_found = int(df['timestamp'].notna().sum())
    
    # Build summary with explicit type conversion
    summary = {
        'report_info': {
            'generated_at': datetime.now().isoformat(),
            'tool': 'YouTube Toxicity Analyzer',
            'version': '1.0.0'
        },
        'video': {
            'title': str(video_info.get('title', 'Unknown')),
            'channel': str(video_info.get('channel', 'Unknown')),
            'video_id': str(video_info.get('video_id', '')),
            'url': f"https://youtube.com/watch?v={video_info.get('video_id', '')}",
            'views': int(video_info.get('view_count', 0)),
            'total_comments': int(video_info.get('comment_count', 0))
        },
        'analysis': {
            'comments_analyzed': int(len(df)),
            'toxicity': {
                'toxic_comments': int(toxic_stats.get('toxic_comments', 0)),
                'toxicity_rate': round(float(toxic_stats.get('toxicity_rate', 0)), 2),
                'average_toxicity': round(float(toxic_stats.get('avg_toxicity', 0)) * 100, 2),
                'max_toxicity': round(float(toxic_stats.get('max_toxicity', 0)) * 100, 2)
            },
            'sentiment': {
                'positive_count': int(sentiment_stats.get('positive_comments', 0)),
                'positive_rate': round(float(sentiment_stats.get('positive_rate', 0)), 2),
                'negative_count': int(sentiment_stats.get('negative_comments', 0)),
                'negative_rate': round(float(sentiment_stats.get('negative_rate', 0)), 2),
                'neutral_count': int(sentiment_stats.get('neutral_comments', 0)),
                'neutral_rate': round(float(sentiment_stats.get('neutral_rate', 0)), 2)
            },
            'timestamps_found': timestamps_found
        }
    }
    
    # Double-check that everything is serializable
    summary = convert_to_serializable(summary)
    
    return summary


# Test the module
if __name__ == "__main__":
    print("=" * 50)
    print("Testing Report Generator")
    print("=" * 50)
    
    import numpy as np
    
    # Create sample data with numpy types (to test conversion)
    sample_df = pd.DataFrame({
        'author': ['User1', 'User2', 'User3', 'User4', 'User5'],
        'text': [
            'This video is amazing! Thank you so much!',
            'This is terrible and you should feel bad',
            'Interesting content',
            'Great tutorial, very helpful',
            'Boring video, wasted my time'
        ],
        'like_count': np.array([100, 5, 20, 50, 3]),  # numpy array
        'score_toxicity': np.array([0.05, 0.85, 0.10, 0.03, 0.60]),  # numpy array
        'sentiment': ['positive', 'negative', 'neutral', 'positive', 'negative'],
        'timestamp': [None, np.int64(120), None, np.int64(300), None]  # numpy int64
    })
    
    video_info = {
        'title': 'Sample Video Title',
        'channel': 'Sample Channel',
        'video_id': 'abc123',
        'view_count': np.int64(1000000),  # numpy int64
        'comment_count': np.int64(5000)  # numpy int64
    }
    
    toxic_stats = {
        'toxic_comments': np.int64(2),  # numpy int64
        'toxicity_rate': np.float64(40.0),  # numpy float64
        'avg_toxicity': np.float64(0.326),  # numpy float64
        'max_toxicity': np.float64(0.85)  # numpy float64
    }
    
    sentiment_stats = {
        'positive_comments': np.int64(2),
        'positive_rate': np.float64(40.0),
        'negative_comments': np.int64(2),
        'negative_rate': np.float64(40.0),
        'neutral_comments': np.int64(1),
        'neutral_rate': np.float64(20.0)
    }
    
    # Test HTML report
    html = generate_html_report(sample_df, video_info, toxic_stats, sentiment_stats)
    print(f"✅ HTML report generated ({len(html)} characters)")
    
    # Test summary (with JSON serialization)
    import json
    summary = create_summary_dict(sample_df, video_info, toxic_stats, sentiment_stats)
    
    # This should NOT raise an error now
    json_str = json.dumps(summary, indent=2)
    print(f"✅ JSON summary created ({len(json_str)} characters)")
    print("\nSample JSON output:")
    print(json_str[:500] + "...")
    
    print("\n✅ Report generator test completed!")