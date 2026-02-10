"""
Sentiment Analysis Module
"""

import pandas as pd
from typing import Dict, List
import re


class SentimentAnalyzer:
    """
    Analyzes sentiment in comments using word lists
    """
    
    def __init__(self):
        """
        Initialize with word lists
        """
        self.positive_words = {
            'love', 'awesome', 'great', 'amazing', 'excellent', 'good', 
            'wonderful', 'fantastic', 'helpful', 'thank', 'thanks', 'brilliant',
            'perfect', 'best', 'beautiful', 'nice', 'super', 'cool', 'useful',
            'interesting', 'clear', 'informative', 'well', 'like', 'enjoy',
            'incredible', 'outstanding', 'superb', 'terrific', 'marvelous'
        }
        
        self.negative_words = {
            'hate', 'terrible', 'awful', 'bad', 'worst', 'stupid', 'dumb',
            'boring', 'disgusting', 'ugly', 'annoying', 'useless', 'waste',
            'confused', 'difficult', 'wrong', 'misleading', 'fake', 'sucks',
            'horrible', 'trash', 'garbage', 'disappointed', 'confusing',
            'pathetic', 'ridiculous', 'pointless', 'frustrating'
        }
        
        self.intensifiers = {
            'very', 'really', 'so', 'extremely', 'absolutely', 'totally',
            'completely', 'highly', 'deeply', 'super', 'too', 'incredibly'
        }
        
        print("✅ Sentiment analyzer initialized!")
    
    def analyze_text(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of a single text
        """
        if not text or not isinstance(text, str):
            return {
                'positive_score': 0.0,
                'negative_score': 0.0,
                'neutral_score': 1.0,
                'compound_score': 0.0,
                'sentiment': 'neutral'
            }
        
        text_lower = text.lower()
        words = text_lower.split()
        
        positive_count = 0
        negative_count = 0
        
        for i, word in enumerate(words):
            clean_word = re.sub(r'[^\w\s]', '', word)
            
            if i > 0:
                prev_word = re.sub(r'[^\w\s]', '', words[i-1])
                intensifier = 1.5 if prev_word in self.intensifiers else 1.0
            else:
                intensifier = 1.0
            
            if clean_word in self.positive_words:
                positive_count += intensifier
            elif clean_word in self.negative_words:
                negative_count += intensifier
        
        total_words = max(len(words), 1)
        positive_score = min(positive_count / total_words, 1.0)
        negative_score = min(negative_count / total_words, 1.0)
        
        compound_score = positive_score - negative_score
        
        if compound_score > 0.1:
            sentiment = 'positive'
        elif compound_score < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        neutral_score = max(0, 1 - positive_score - negative_score)
        
        return {
            'positive_score': positive_score,
            'negative_score': negative_score,
            'neutral_score': neutral_score,
            'compound_score': compound_score,
            'sentiment': sentiment
        }
    
    def analyze_comments(self, comments: List[str]) -> pd.DataFrame:
        """
        Analyze sentiment of multiple comments
        """
        results = []
        
        for comment in comments:
            scores = self.analyze_text(comment)
            results.append(scores)
        
        return pd.DataFrame(results)
    
    def analyze_dataframe(self, df: pd.DataFrame, text_column: str = 'text') -> pd.DataFrame:
        """
        Analyze sentiment for comments in a DataFrame
        """
        if text_column not in df.columns:
            raise ValueError(f"Column '{text_column}' not found in DataFrame")
        
        comments = df[text_column].fillna('').tolist()
        sentiment_scores = self.analyze_comments(comments)
        
        df['sentiment'] = sentiment_scores['sentiment']
        df['sentiment_positive'] = sentiment_scores['positive_score']
        df['sentiment_negative'] = sentiment_scores['negative_score']
        df['sentiment_neutral'] = sentiment_scores['neutral_score']
        df['sentiment_compound'] = sentiment_scores['compound_score']
        
        return df
    
    def get_statistics(self, df: pd.DataFrame) -> Dict:
        """
        Calculate sentiment statistics
        """
        if 'sentiment' not in df.columns:
            return {}
        
        return {
            'total_comments': len(df),
            'positive_comments': (df['sentiment'] == 'positive').sum(),
            'negative_comments': (df['sentiment'] == 'negative').sum(),
            'neutral_comments': (df['sentiment'] == 'neutral').sum(),
            'positive_rate': (df['sentiment'] == 'positive').mean() * 100,
            'negative_rate': (df['sentiment'] == 'negative').mean() * 100,
            'neutral_rate': (df['sentiment'] == 'neutral').mean() * 100,
            'avg_compound_score': df['sentiment_compound'].mean(),
        }


if __name__ == "__main__":
    print("=" * 50)
    print("Testing Sentiment Analyzer")
    print("=" * 50)
    
    analyzer = SentimentAnalyzer()
    
    test_comments = [
        "This video is really helpful, thank you!",
        "I hate this so much, terrible content",
        "Not bad, could be better",
        "Absolutely amazing! Best tutorial ever!",
        "Boring and confusing",
    ]
    
    print("\n📝 Test Comments:")
    for i, comment in enumerate(test_comments, 1):
        print(f"{i}. {comment}")
    
    print("\n📊 Sentiment Analysis Results:")
    print("-" * 50)
    
    for comment in test_comments:
        result = analyzer.analyze_text(comment)
        
        emoji = {"positive": "😊", "negative": "😞", "neutral": "😐"}
        
        print(f"\nComment: {comment[:50]}...")
        print(f"Sentiment: {emoji[result['sentiment']]} {result['sentiment'].upper()}")
        print(f"Scores: Pos={result['positive_score']:.2f}, "
              f"Neg={result['negative_score']:.2f}, "
              f"Compound={result['compound_score']:.2f}")
    
    print("\n✅ Sentiment analyzer test completed!")