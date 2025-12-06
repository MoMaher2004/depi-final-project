import joblib
import warnings

# Suppress potential version warnings during model loading
warnings.filterwarnings("ignore")

try:
    # 1. Load the Pipeline object (pcos.pkl)
    pcos_pipeline = joblib.load('./datasets/heart-failure/scaler_heart.pkl')
    
    # 2. Extract feature names from the fitted Pipeline
    # This attribute stores the exact names and order used during training.
    if hasattr(pcos_pipeline, 'feature_names_in_'):
        feature_names = pcos_pipeline.feature_names_in_.tolist()
        
        print("--- Definitive Feature List from the Trained Model ---")
        print("Please use this list EXACTLY (including spacing and order) in your FastAPI code.")
        print("------------------------------------------------------\n")
        
        # Print the list in a usable format
        for name in feature_names:
            print(f"'{name}',")
        
        print(f"\n------------------------------------------------------")
        print(f"Total Features: {len(feature_names)}")
    else:
        print("⚠️ Warning: 'feature_names_in_' attribute not found.")
        print("This typically means you are using an older scikit-learn version (< 1.0).")
        print("You must manually check your original training script for the columns of X_train.")

except FileNotFoundError:
    print("❌ Error: The file './datasets/pcos/pcos.pkl' was not found. Check the path.")
except Exception as e:
    print(f"An unexpected error occurred during model loading: {e}")