"""
Toxicity Detection Module using Detoxify
"""

from detoxify import Detoxify
import pandas as pd
from typing import Dict, List
import time
from tqdm import tqdm


class ToxicityAnalyzer:
    """
    Analyzes toxicity in text using Detoxify models
    """
    
    def __init__(self, model_type: str = 'original'):
        """
        Initialize toxicity detector
        """
        print(f"Loading Detoxify model: {model_type}")
        print("Note: First time will download ~400MB model file...")
        
        start_time = time.time()
        self.model = Detoxify(model_type)
        load_time = time.time() - start_time
        
        print(f"✅ Model loaded successfully in {load_time:.2f} seconds!")
        
        # FIXED: Correct category names from Detoxify
        # The actual categories are: toxicity, severe_toxicity, obscene, 
        # identity_attack, insult, threat, sexual (not sexual_explicit)
        self.categories = [
            'toxicity',
            'severe_toxicity', 
            'obscene',
            'identity_attack',
            'insult',
            'threat',
            'sexual'  # FIXED: Changed from 'sexual_explicit' to 'sexual'
        ]
    
    def analyze_text(self, text: str) -> Dict[str, float]:
        """
        Analyze toxicity of a single text
        """
        if not text or not isinstance(text, str):
            return {cat: 0.0 for cat in self.categories}
        
        if len(text) > 1000:
            text = text[:1000]
        
        try:
            results = self.model.predict(text)
            # The model returns 'sexual_explicit' but we'll rename it to 'sexual' for consistency
            if 'sexual_explicit' in results and 'sexual' not in results:
                results['sexual'] = results['sexual_explicit']
            return results
        except Exception as e:
            print(f"Error analyzing text: {e}")
            return {cat: 0.0 for cat in self.categories}
    
    def analyze_comments(self, comments: List[str], batch_size: int = 100) -> pd.DataFrame:
        """
        Analyze toxicity of multiple comments
        """
        results = []
        
        print(f"\n🔍 Analyzing {len(comments)} comments for toxicity...")
        
        for i in tqdm(range(0, len(comments), batch_size), desc="Processing"):
            batch = comments[i:i+batch_size]
            
            for comment in batch:
                scores = self.analyze_text(comment)
                # Ensure we have the right column names
                result_dict = {}
                for category in self.categories:
                    if category == 'sexual':
                        # Handle both 'sexual' and 'sexual_explicit' keys
                        result_dict['sexual'] = scores.get('sexual', scores.get('sexual_explicit', 0.0))
                    else:
                        result_dict[category] = scores.get(category, 0.0)
                results.append(result_dict)
        
        df_scores = pd.DataFrame(results)
        return df_scores
    
    def analyze_dataframe(self, df: pd.DataFrame, text_column: str = 'text') -> pd.DataFrame:
        """
        Analyze toxicity for comments in a DataFrame
        """
        if text_column not in df.columns:
            raise ValueError(f"Column '{text_column}' not found in DataFrame")
        
        comments = df[text_column].fillna('').tolist()
        toxicity_scores = self.analyze_comments(comments)
        
        for category in self.categories:
            if category in toxicity_scores.columns:
                df[f'score_{category}'] = toxicity_scores[category]
            else:
                print(f"Warning: Category '{category}' not found in results")
                df[f'score_{category}'] = 0.0
        
        df['is_toxic'] = df['score_toxicity'] >= 0.5
        
        df['toxicity_level'] = pd.cut(
            df['score_toxicity'],
            bins=[0, 0.3, 0.5, 0.7, 1.0],
            labels=['low', 'moderate', 'high', 'very_high']
        )
        
        return df
    
    def get_toxic_comments(self, df: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
        """
        Filter DataFrame to show only toxic comments
        """
        toxic_df = df[df['score_toxicity'] >= threshold].copy()
        toxic_df = toxic_df.sort_values('score_toxicity', ascending=False)
        return toxic_df
    
    def get_statistics(self, df: pd.DataFrame) -> Dict:
        """
        Calculate toxicity statistics
        """
        stats = {
            'total_comments': len(df),
            'toxic_comments': df['is_toxic'].sum() if 'is_toxic' in df.columns else 0,
            'toxicity_rate': df['is_toxic'].mean() * 100 if 'is_toxic' in df.columns else 0,
            'avg_toxicity': df['score_toxicity'].mean() if 'score_toxicity' in df.columns else 0,
            'max_toxicity': df['score_toxicity'].max() if 'score_toxicity' in df.columns else 0,
        }
        
        for category in self.categories:
            col = f'score_{category}'
            if col in df.columns:
                stats[f'avg_{category}'] = df[col].mean()
                stats[f'max_{category}'] = df[col].max()
                stats[f'high_{category}_count'] = (df[col] >= 0.5).sum()
        
        return stats


if __name__ == "__main__":
    print("=" * 50)
    print("Testing Toxicity Analyzer")
    print("=" * 50)
    
    analyzer = ToxicityAnalyzer()
    
    test_comments = [
        "This video is really helpful, thank you!",
        "I hate this so much, you're terrible",
        "Great content, keep it up!",
        "This is stupid and you should feel bad",
        "Love the explanation at 2:30",
    ]
    
    print("\n📝 Test Comments:")
    for i, comment in enumerate(test_comments, 1):
        print(f"{i}. {comment}")
    
    print("\n📊 Analysis Results:")
    print("-" * 50)
    
    for comment in test_comments:
        scores = analyzer.analyze_text(comment)
        toxicity = scores.get('toxicity', 0)
        
        if toxicity < 0.3:
            label = "✅ Non-toxic"
        elif toxicity < 0.5:
            label = "⚠️ Slightly toxic"
        elif toxicity < 0.7:
            label = "⛔ Toxic"
        else:
            label = "🚫 Very toxic"
        
        print(f"\nComment: {comment[:50]}...")
        print(f"Toxicity Score: {toxicity:.2%} - {label}")
        
        # Show high-scoring categories
        for category in ['severe_toxicity', 'obscene', 'identity_attack', 'insult', 'threat', 'sexual']:
            score = scores.get(category, scores.get('sexual_explicit' if category == 'sexual' else category, 0))
            if score > 0.3:
                print(f"  - {category}: {score:.2%}")
    
    print("\n✅ Toxicity analyzer test completed!")