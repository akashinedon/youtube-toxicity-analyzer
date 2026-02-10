"""
Test if all requirements are installed correctly
"""

print("=" * 50)
print("Testing Installations")
print("=" * 50)

# Test 1: Python-dotenv
try:
    from dotenv import load_dotenv
    print("✅ python-dotenv: OK")
except ImportError as e:
    print(f"❌ python-dotenv: {e}")

# Test 2: Pandas
try:
    import pandas as pd
    print(f"✅ pandas: {pd.__version__}")
except ImportError as e:
    print(f"❌ pandas: {e}")

# Test 3: Google API
try:
    from googleapiclient.discovery import build
    print("✅ google-api-python-client: OK")
except ImportError as e:
    print(f"❌ google-api-python-client: {e}")

# Test 4: Detoxify
try:
    from detoxify import Detoxify
    print("✅ detoxify: OK")
except ImportError as e:
    print(f"❌ detoxify: {e}")

# Test 5: Streamlit
try:
    import streamlit
    print(f"✅ streamlit: {streamlit.__version__}")
except ImportError as e:
    print(f"❌ streamlit: {e}")

# Test 6: Plotly
try:
    import plotly
    print(f"✅ plotly: {plotly.__version__}")
except ImportError as e:
    print(f"❌ plotly: {e}")

# Test 7: tqdm
try:
    from tqdm import tqdm
    print("✅ tqdm: OK")
except ImportError as e:
    print(f"❌ tqdm: {e}")

print("\n" + "=" * 50)
print("✅ All tests completed!")
print("=" * 50)