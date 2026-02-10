"""
Video Comparison Module
Compare toxicity across multiple videos
"""

import pandas as pd
import plotly.graph_objects as go
from typing import List, Dict


def compare_videos(analysis_results: List[Dict]) -> pd.DataFrame:
    """
    Compare multiple video analyses
    
    Args:
        analysis_results: List of dictionaries with analysis data
        
    Returns:
        DataFrame with comparison data
    """
    comparison_data = []
    
    for result in analysis_results:
        comparison_data.append({
            'Video': result['video_info'].get('title', 'Unknown')[:30] + '...',
            'Channel': result['video_info'].get('channel', 'Unknown'),
            'Comments Analyzed': result['total_comments'],
            'Toxicity Rate (%)': result['toxic_stats'].get('toxicity_rate', 0),
            'Avg Toxicity (%)': result['toxic_stats'].get('avg_toxicity', 0) * 100,
            'Positive (%)': result['sentiment_stats'].get('positive_rate', 0),
            'Negative (%)': result['sentiment_stats'].get('negative_rate', 0),
            'Neutral (%)': result['sentiment_stats'].get('neutral_rate', 0)
        })
    
    return pd.DataFrame(comparison_data)


def create_comparison_chart(comparison_df: pd.DataFrame) -> go.Figure:
    """
    Create a comparison bar chart
    """
    fig = go.Figure()
    
    # Add toxicity rate bars
    fig.add_trace(go.Bar(
        name='Toxicity Rate',
        x=comparison_df['Video'],
        y=comparison_df['Toxicity Rate (%)'],
        marker_color='#e74c3c',
        text=comparison_df['Toxicity Rate (%)'].round(1),
        textposition='outside',
        hovertemplate="<b>%{x}</b><br>Toxicity: %{y:.1f}%<extra></extra>"
    ))
    
    # Add positive sentiment bars
    fig.add_trace(go.Bar(
        name='Positive Sentiment',
        x=comparison_df['Video'],
        y=comparison_df['Positive (%)'],
        marker_color='#2ecc71',
        text=comparison_df['Positive (%)'].round(1),
        textposition='outside',
        hovertemplate="<b>%{x}</b><br>Positive: %{y:.1f}%<extra></extra>"
    ))
    
    fig.update_layout(
        title={
            'text': "Video Comparison: Toxicity vs Positive Sentiment",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 20}
        },
        xaxis_title="Video",
        yaxis_title="Percentage (%)",
        barmode='group',
        height=400,
        margin=dict(l=50, r=20, t=60, b=100),
        xaxis_tickangle=-45,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def create_radar_comparison(comparison_df: pd.DataFrame) -> go.Figure:
    """
    Create a radar chart comparing videos
    """
    fig = go.Figure()
    
    categories = ['Toxicity Rate', 'Avg Toxicity', 'Positive %', 'Negative %']
    
    for idx, row in comparison_df.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=[
                row['Toxicity Rate (%)'],
                row['Avg Toxicity (%)'],
                row['Positive (%)'],
                row['Negative (%)']
            ],
            theta=categories,
            fill='toself',
            name=row['Video']
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        title="Multi-Dimensional Video Comparison",
        height=500
    )
    
    return fig