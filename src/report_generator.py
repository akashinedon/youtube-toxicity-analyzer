"""
Report Generator Module
Creates professional HTML and PDF reports
"""

import pandas as pd
from datetime import datetime
from typing import Dict, Optional
import base64


def generate_html_report(
    df: pd.DataFrame,
    video_info: Dict,
    toxic_stats: Dict,
    sentiment_stats: Dict,
    output_path: Optional[str] = None
) -> str:
    """
    Generate a professional HTML report
    """
    
    # Calculate additional stats
    total_comments = len(df)
    toxic_count = toxic_stats.get('toxic_comments', 0)
    avg_toxicity = toxic_stats.get('avg_toxicity', 0) * 100
    
    # Get top toxic comments
    top_toxic = df.nlargest(5, 'score_toxicity')[['author', 'text', 'score_toxicity']].to_dict('records')
    
    # Get top positive comments
    top_positive = df[df['sentiment'] == 'positive'].nlargest(5, 'like_count')[['author', 'text', 'like_count']].to_dict('records')
    
    # HTML template
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
            
            .video-info {{
                background: #ecf0f1;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 30px;
            }}
            
            .video-info h2 {{
                color: #2c3e50;
                margin-bottom: 15px;
            }}
            
            .video-info p {{
                margin: 8px 0;
                font-size: 1.1em;
            }}
            
            .metrics {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            
            .metric-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 25px;
                border-radius: 8px;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            
            .metric-card.danger {{
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            }}
            
            .metric-card.success {{
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            }}
            
            .metric-card.warning {{
                background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            }}
            
            .metric-card h3 {{
                font-size: 1.1em;
                margin-bottom: 10px;
                opacity: 0.9;
            }}
            
            .metric-card .value {{
                font-size: 2.5em;
                font-weight: bold;
                margin: 10px 0;
            }}
            
            .metric-card .description {{
                font-size: 0.9em;
                opacity: 0.8;
            }}
            
            .section {{
                margin: 40px 0;
            }}
            
            .section h2 {{
                color: #2c3e50;
                font-size: 1.8em;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 2px solid #3498db;
            }}
            
            .comment-list {{
                background: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
            }}
            
            .comment-item {{
                background: white;
                padding: 15px;
                margin-bottom: 15px;
                border-radius: 5px;
                border-left: 4px solid #e74c3c;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }}
            
            .comment-item.positive {{
                border-left-color: #2ecc71;
            }}
            
            .comment-item .author {{
                font-weight: bold;
                color: #3498db;
                margin-bottom: 8px;
            }}
            
            .comment-item .text {{
                color: #555;
                line-height: 1.5;
                margin-bottom: 8px;
            }}
            
            .comment-item .meta {{
                display: flex;
                justify-content: space-between;
                font-size: 0.9em;
                color: #7f8c8d;
            }}
            
            .badge {{
                display: inline-block;
                padding: 4px 10px;
                border-radius: 12px;
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
            
            .footer {{
                text-align: center;
                margin-top: 50px;
                padding-top: 20px;
                border-top: 2px solid #ecf0f1;
                color: #7f8c8d;
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
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎥 YouTube Toxicity Analysis Report</h1>
                <p class="subtitle">Comprehensive Analysis of Comment Toxicity and Sentiment</p>
                <p style="color: #95a5a6; margin-top: 10px;">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>
            
            <div class="video-info">
                <h2>📹 Video Information</h2>
                <p><strong>Title:</strong> {video_info.get('title', 'Unknown')}</p>
                <p><strong>Channel:</strong> {video_info.get('channel', 'Unknown')}</p>
                <p><strong>Views:</strong> {video_info.get('view_count', 0):,}</p>
                <p><strong>Total Comments:</strong> {video_info.get('comment_count', 0):,}</p>
            </div>
            
            <div class="metrics">
                <div class="metric-card">
                    <h3>Total Comments Analyzed</h3>
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
            
            <div class="section">
                <h2>🚨 Most Toxic Comments</h2>
                <div class="comment-list">
    """
    
    # Add toxic comments
    for comment in top_toxic:
        toxicity_percent = comment['score_toxicity'] * 100
        html_content += f"""
                    <div class="comment-item">
                        <div class="author">👤 {comment['author']}</div>
                        <div class="text">{comment['text'][:200]}...</div>
                        <div class="meta">
                            <span class="badge danger">Toxicity: {toxicity_percent:.1f}%</span>
                        </div>
                    </div>
        """
    
    html_content += """
                </div>
            </div>
            
            <div class="section">
                <h2>💚 Most Liked Positive Comments</h2>
                <div class="comment-list">
    """
    
    # Add positive comments
    for comment in top_positive:
        html_content += f"""
                    <div class="comment-item positive">
                        <div class="author">👤 {comment['author']}</div>
                        <div class="text">{comment['text'][:200]}...</div>
                        <div class="meta">
                            <span class="badge success">❤️ {comment['like_count']} likes</span>
                        </div>
                    </div>
        """
    
    html_content += f"""
                </div>
            </div>
            
            <div class="section">
                <h2>📊 Sentiment Breakdown</h2>
                <div class="comment-list">
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; text-align: center;">
                        <div>
                            <h3 style="color: #2ecc71;">😊 Positive</h3>
                            <p style="font-size: 2em; font-weight: bold;">{sentiment_stats.get('positive_rate', 0):.1f}%</p>
                            <p style="color: #7f8c8d;">{sentiment_stats.get('positive_comments', 0)} comments</p>
                        </div>
                        <div>
                            <h3 style="color: #e74c3c;">😞 Negative</h3>
                            <p style="font-size: 2em; font-weight: bold;">{sentiment_stats.get('negative_rate', 0):.1f}%</p>
                            <p style="color: #7f8c8d;">{sentiment_stats.get('negative_comments', 0)} comments</p>
                        </div>
                        <div>
                            <h3 style="color: #95a5a6;">😐 Neutral</h3>
                            <p style="font-size: 2em; font-weight: bold;">{sentiment_stats.get('neutral_rate', 0):.1f}%</p>
                            <p style="color: #7f8c8d;">{sentiment_stats.get('neutral_comments', 0)} comments</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <p><strong>YouTube Toxicity Analyzer</strong></p>
                <p>Powered by Detoxify AI and Natural Language Processing</p>
                <p style="margin-top: 10px; font-size: 0.9em;">
                    This report analyzes comment toxicity, sentiment, and engagement patterns<br>
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
    
    return html_content


def create_summary_dict(df: pd.DataFrame, video_info: Dict, toxic_stats: Dict, sentiment_stats: Dict) -> Dict:
    """
    Create a summary dictionary for easy sharing
    """
    return {
        'video': {
            'title': video_info.get('title', 'Unknown'),
            'channel': video_info.get('channel', 'Unknown'),
            'views': video_info.get('view_count', 0),
            'url': f"https://youtube.com/watch?v={video_info.get('video_id', '')}"
        },
        'analysis': {
            'total_comments': len(df),
            'toxic_comments': toxic_stats.get('toxic_comments', 0),
            'toxicity_rate': f"{toxic_stats.get('toxicity_rate', 0):.1f}%",
            'avg_toxicity': f"{toxic_stats.get('avg_toxicity', 0) * 100:.1f}%",
            'positive_rate': f"{sentiment_stats.get('positive_rate', 0):.1f}%",
            'negative_rate': f"{sentiment_stats.get('negative_rate', 0):.1f}%",
            'neutral_rate': f"{sentiment_stats.get('neutral_rate', 0):.1f}%"
        },
        'timestamp': datetime.now().isoformat()
    }


# Test the module
if __name__ == "__main__":
    print("Report generator module loaded successfully!")