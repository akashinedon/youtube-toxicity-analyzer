"""
Visualization Module
Creates beautiful charts using Plotly
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Optional


def create_toxicity_gauge(toxicity_rate: float) -> go.Figure:
    """
    Create a gauge chart showing overall toxicity rate
    """
    # Determine color based on toxicity level
    if toxicity_rate < 10:
        color = "green"
    elif toxicity_rate < 25:
        color = "yellow"
    elif toxicity_rate < 50:
        color = "orange"
    else:
        color = "red"
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=toxicity_rate,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Toxicity Rate (%)", 'font': {'size': 24}},
        number={'suffix': "%", 'font': {'size': 40}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 10], 'color': 'rgba(0, 255, 0, 0.3)'},
                {'range': [10, 25], 'color': 'rgba(255, 255, 0, 0.3)'},
                {'range': [25, 50], 'color': 'rgba(255, 165, 0, 0.3)'},
                {'range': [50, 100], 'color': 'rgba(255, 0, 0, 0.3)'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': toxicity_rate
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig


def create_sentiment_pie(sentiment_stats: Dict) -> go.Figure:
    """
    Create a pie chart showing sentiment distribution
    """
    labels = ['Positive', 'Negative', 'Neutral']
    values = [
        sentiment_stats.get('positive_comments', 0),
        sentiment_stats.get('negative_comments', 0),
        sentiment_stats.get('neutral_comments', 0)
    ]
    colors = ['#2ecc71', '#e74c3c', '#95a5a6']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=colors,
        textinfo='label+percent',
        textfont_size=14,
        hovertemplate="<b>%{label}</b><br>" +
                      "Count: %{value}<br>" +
                      "Percentage: %{percent}<extra></extra>"
    )])
    
    fig.update_layout(
        title={
            'text': "Sentiment Distribution",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 20}
        },
        height=350,
        margin=dict(l=20, r=20, t=60, b=20),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig


def create_toxicity_distribution(df: pd.DataFrame) -> go.Figure:
    """
    Create histogram showing toxicity score distribution
    """
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=df['score_toxicity'] * 100,
        nbinsx=20,
        marker_color='#3498db',
        opacity=0.75,
        hovertemplate="Toxicity: %{x:.1f}%<br>Count: %{y}<extra></extra>"
    ))
    
    # Add vertical line at 50% threshold
    fig.add_vline(
        x=50,
        line_dash="dash",
        line_color="red",
        annotation_text="Toxic Threshold (50%)",
        annotation_position="top"
    )
    
    fig.update_layout(
        title={
            'text': "Toxicity Score Distribution",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 20}
        },
        xaxis_title="Toxicity Score (%)",
        yaxis_title="Number of Comments",
        height=350,
        margin=dict(l=50, r=20, t=60, b=50),
        bargap=0.1
    )
    
    return fig


def create_toxicity_by_category(df: pd.DataFrame) -> go.Figure:
    """
    Create bar chart showing average toxicity by category
    """
    categories = ['toxicity', 'severe_toxicity', 'obscene', 
                  'identity_attack', 'insult', 'threat', 'sexual']
    
    # Calculate averages
    averages = []
    labels = []
    
    for cat in categories:
        col = f'score_{cat}'
        if col in df.columns:
            avg = df[col].mean() * 100
            averages.append(avg)
            # Make labels more readable
            label = cat.replace('_', ' ').title()
            labels.append(label)
    
    # Sort by value
    sorted_data = sorted(zip(labels, averages), key=lambda x: x[1], reverse=True)
    labels, averages = zip(*sorted_data) if sorted_data else ([], [])
    
    # Color based on value
    colors = ['#e74c3c' if v > 20 else '#f39c12' if v > 10 else '#3498db' for v in averages]
    
    fig = go.Figure(data=[go.Bar(
        x=list(labels),
        y=list(averages),
        marker_color=colors,
        text=[f'{v:.1f}%' for v in averages],
        textposition='outside',
        hovertemplate="<b>%{x}</b><br>Average: %{y:.2f}%<extra></extra>"
    )])
    
    fig.update_layout(
        title={
            'text': "Average Score by Toxicity Category",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 20}
        },
        xaxis_title="Category",
        yaxis_title="Average Score (%)",
        height=400,
        margin=dict(l=50, r=20, t=60, b=100),
        xaxis_tickangle=-45
    )
    
    return fig


def create_timeline_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create timeline chart showing toxicity over video timestamps
    """
    # Filter comments with timestamps
    timeline_df = df[df['timestamp'].notna()].copy()
    
    if timeline_df.empty:
        # Create empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            x=0.5, y=0.5,
            text="No comments with timestamps found",
            font=dict(size=20),
            showarrow=False,
            xref="paper", yref="paper"
        )
        fig.update_layout(
            height=350,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig
    
    # Convert timestamp to minutes
    timeline_df['timestamp_min'] = timeline_df['timestamp'] / 60
    
    # Bin by minute and calculate average toxicity
    timeline_df['minute_bin'] = timeline_df['timestamp_min'].astype(int)
    
    agg_df = timeline_df.groupby('minute_bin').agg({
        'score_toxicity': 'mean',
        'text': 'count'
    }).reset_index()
    
    agg_df.columns = ['minute', 'avg_toxicity', 'comment_count']
    agg_df['avg_toxicity'] = agg_df['avg_toxicity'] * 100
    
    fig = go.Figure()
    
    # Add toxicity line
    fig.add_trace(go.Scatter(
        x=agg_df['minute'],
        y=agg_df['avg_toxicity'],
        mode='lines+markers',
        name='Toxicity',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=8),
        hovertemplate="<b>Minute %{x}</b><br>" +
                      "Avg Toxicity: %{y:.1f}%<br>" +
                      "<extra></extra>"
    ))
    
    # Add threshold line
    fig.add_hline(
        y=50,
        line_dash="dash",
        line_color="red",
        annotation_text="Toxic Threshold",
        annotation_position="right"
    )
    
    fig.update_layout(
        title={
            'text': "Toxicity Across Video Timeline",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 20}
        },
        xaxis_title="Video Timeline (minutes)",
        yaxis_title="Average Toxicity (%)",
        height=350,
        margin=dict(l=50, r=20, t=60, b=50),
        yaxis=dict(range=[0, 100]),
        hovermode='x unified'
    )
    
    return fig


def create_top_toxic_table(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """
    Create a table of top toxic comments
    """
    toxic_df = df.nlargest(n, 'score_toxicity')[
        ['author', 'text', 'score_toxicity', 'like_count']
    ].copy()
    
    # Format toxicity as percentage
    toxic_df['score_toxicity'] = (toxic_df['score_toxicity'] * 100).round(1)
    
    # Truncate long text
    toxic_df['text'] = toxic_df['text'].str[:100] + '...'
    
    # Rename columns for display
    toxic_df.columns = ['Author', 'Comment', 'Toxicity (%)', 'Likes']
    
    return toxic_df


def create_word_frequency_chart(df: pd.DataFrame, sentiment: str = 'all') -> go.Figure:
    """
    Create bar chart showing most common words
    """
    import re
    from collections import Counter
    
    # Filter by sentiment if specified
    if sentiment != 'all':
        filtered_df = df[df['sentiment'] == sentiment]
    else:
        filtered_df = df
    
    # Combine all text
    all_text = ' '.join(filtered_df['text'].fillna('').tolist()).lower()
    
    # Remove common words and clean
    stop_words = {
        'the', 'a', 'an', 'is', 'it', 'to', 'and', 'of', 'in', 'for',
        'this', 'that', 'i', 'you', 'he', 'she', 'we', 'they', 'my',
        'your', 'his', 'her', 'its', 'our', 'their', 'what', 'which',
        'who', 'when', 'where', 'why', 'how', 'all', 'each', 'every',
        'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
        'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
        'very', 'just', 'can', 'will', 'should', 'now', 'im', 'dont',
        'was', 'are', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'but', 'if', 'or', 'because', 'as',
        'until', 'while', 'at', 'by', 'with', 'about', 'against',
        'between', 'into', 'through', 'during', 'before', 'after',
        'above', 'below', 'from', 'up', 'down', 'on', 'off', 'over',
        'under', 'again', 'further', 'then', 'once', 'here', 'there',
        'when', 'where', 'why', 'how', 'am', 'me', 'like', 'get',
        'got', 'would', 'could', 'one', 'know', 'think', 'see', 'come'
    }
    
    # Extract words
    words = re.findall(r'\b[a-z]{3,15}\b', all_text)
    
    # Filter and count
    filtered_words = [w for w in words if w not in stop_words]
    word_counts = Counter(filtered_words).most_common(15)
    
    if not word_counts:
        fig = go.Figure()
        fig.add_annotation(
            x=0.5, y=0.5,
            text="Not enough data for word analysis",
            font=dict(size=16),
            showarrow=False,
            xref="paper", yref="paper"
        )
        fig.update_layout(height=300)
        return fig
    
    words, counts = zip(*word_counts)
    
    # Choose color based on sentiment
    if sentiment == 'positive':
        color = '#2ecc71'
    elif sentiment == 'negative':
        color = '#e74c3c'
    else:
        color = '#3498db'
    
    fig = go.Figure(data=[go.Bar(
        x=list(counts),
        y=list(words),
        orientation='h',
        marker_color=color,
        text=list(counts),
        textposition='outside',
        hovertemplate="<b>%{y}</b><br>Count: %{x}<extra></extra>"
    )])
    
    title = f"Most Common Words"
    if sentiment != 'all':
        title += f" ({sentiment.title()} Comments)"
    
    fig.update_layout(
        title={
            'text': title,
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 18}
        },
        xaxis_title="Count",
        yaxis_title="Word",
        height=400,
        margin=dict(l=100, r=50, t=60, b=50),
        yaxis=dict(autorange="reversed")
    )
    
    return fig


def create_engagement_scatter(df: pd.DataFrame) -> go.Figure:
    """
    Create scatter plot showing toxicity vs engagement (likes)
    """
    fig = go.Figure()
    
    # Add scatter points colored by toxicity
    fig.add_trace(go.Scatter(
        x=df['like_count'],
        y=df['score_toxicity'] * 100,
        mode='markers',
        marker=dict(
            size=10,
            color=df['score_toxicity'],
            colorscale='RdYlGn_r',
            showscale=True,
            colorbar=dict(title="Toxicity"),
            opacity=0.7
        ),
        text=df['text'].str[:50] + '...',
        hovertemplate="<b>Likes: %{x}</b><br>" +
                      "Toxicity: %{y:.1f}%<br>" +
                      "Comment: %{text}<extra></extra>"
    ))
    
    fig.update_layout(
        title={
            'text': "Toxicity vs Engagement (Likes)",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 20}
        },
        xaxis_title="Number of Likes",
        yaxis_title="Toxicity Score (%)",
        height=400,
        margin=dict(l=50, r=50, t=60, b=50),
        yaxis=dict(range=[0, 100])
    )
    
    return fig


def create_comment_length_analysis(df: pd.DataFrame) -> go.Figure:
    """
    Create box plot comparing comment length by toxicity level
    """
    df_copy = df.copy()
    df_copy['comment_length'] = df_copy['text'].str.len()
    
    fig = go.Figure()
    
    toxicity_levels = ['low', 'moderate', 'high', 'very_high']
    colors = ['#2ecc71', '#f1c40f', '#e67e22', '#e74c3c']
    
    for level, color in zip(toxicity_levels, colors):
        level_data = df_copy[df_copy['toxicity_level'] == level]['comment_length']
        if not level_data.empty:
            fig.add_trace(go.Box(
                y=level_data,
                name=level.replace('_', ' ').title(),
                marker_color=color,
                boxpoints='outliers'
            ))
    
    fig.update_layout(
        title={
            'text': "Comment Length by Toxicity Level",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 20}
        },
        xaxis_title="Toxicity Level",
        yaxis_title="Comment Length (characters)",
        height=400,
        margin=dict(l=50, r=20, t=60, b=50),
        showlegend=False
    )
    
    return fig


# Test the visualizations
if __name__ == "__main__":
    print("Testing visualizations...")
    
    # Create sample data
    import numpy as np
    
    np.random.seed(42)
    n = 100
    
    sample_df = pd.DataFrame({
        'text': ['Sample comment ' + str(i) for i in range(n)],
        'author': ['User' + str(i) for i in range(n)],
        'like_count': np.random.randint(0, 1000, n),
        'score_toxicity': np.random.random(n) * 0.5,
        'score_severe_toxicity': np.random.random(n) * 0.1,
        'score_obscene': np.random.random(n) * 0.2,
        'score_identity_attack': np.random.random(n) * 0.1,
        'score_insult': np.random.random(n) * 0.3,
        'score_threat': np.random.random(n) * 0.05,
        'score_sexual': np.random.random(n) * 0.05,
        'sentiment': np.random.choice(['positive', 'negative', 'neutral'], n),
        'timestamp': np.random.choice([None, 60, 120, 180, 240], n),
        'toxicity_level': np.random.choice(['low', 'moderate', 'high', 'very_high'], n)
    })
    
    # Test each visualization
    fig1 = create_toxicity_gauge(15.5)
    print("✅ Toxicity gauge created")
    
    sentiment_stats = {
        'positive_comments': 30,
        'negative_comments': 10,
        'neutral_comments': 60
    }
    fig2 = create_sentiment_pie(sentiment_stats)
    print("✅ Sentiment pie chart created")
    
    fig3 = create_toxicity_distribution(sample_df)
    print("✅ Toxicity distribution created")
    
    fig4 = create_toxicity_by_category(sample_df)
    print("✅ Category bar chart created")
    
    fig5 = create_timeline_chart(sample_df)
    print("✅ Timeline chart created")
    
    fig6 = create_engagement_scatter(sample_df)
    print("✅ Engagement scatter created")
    
    fig7 = create_comment_length_analysis(sample_df)
    print("✅ Comment length analysis created")
    
    print("\n✅ All visualizations working!")