import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler,MinMaxScaler,robust_scale
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier,AdaBoostClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report
import warnings
from sklearn.exceptions import ConvergenceWarning
import joblib

# --- Main Try-Except Block ---
try:

    # Use a specific try-except for file reading
    try:
        # Read the CSV file
        # df = pd.read_excel('./PCOS_data_without_infertility.xlsx',sheet_name='Full_new')
        df = pd.read_csv('./datasets/pcos/pcos_model.csv')
    except FileNotFoundError:
        print(f"--- File not found:  ---")
        print("--- Please ensure the file is in the correct path. ---")
        raise # Stop execution
    except pd.errors.EmptyDataError:
        print(f"--- The file  is empty. ---")
        raise # Stop execution

    print("\n--- Data loaded successfully ---")



    # --- 2. Data Preprocessing ---
    print("--- 2. Processing data... ---")



    # Clean column names (remove leading/trailing spaces)
    df.columns = df.columns.str.strip()

    # Define columns to drop
    cols_to_drop = ['Sl. No', 'Patient File No.', 'Unnamed: 44']

    # Ensure columns exist before dropping them
    cols_to_drop_existing = [col for col in cols_to_drop if col in df.columns]
    df = df.drop(columns=cols_to_drop_existing)

    # Convert object columns to numeric
    # (Corrected column name based on data info)
    obj_cols = ['II    beta-HCG(mIU/mL)', 'AMH(ng/mL)']
    for col in obj_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Fill missing values (NaN) with the column median
    for col in df.columns:
        if df[col].isnull().any():
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)



    print("--- Data processing complete. ---")



    # --- 3. Define Features (X) and Target (y) ---
    target_column = 'PCOS (Y/N)_yes'
    if target_column not in df.columns:
        print(f"--- Target column '{target_column}' not found in the file! ---")
    else:
        y = df[target_column]
        X = df.drop(columns=target_column)

        # --- 4. Split Data ---
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        print("--- 4. Data split into training and testing sets. ---")

        # --- 5. Define and Train Models ---
        print("--- 5. Starting model training and evaluation... ---\n")
        scaler = MinMaxScaler()

        models = {
            'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
            'Decision Tree': DecisionTreeClassifier(random_state=42,),
            'Random Forest': RandomForestClassifier(random_state=42),
            'SVM': SVC(random_state=42),
            'KNN': KNeighborsClassifier(),
            'Gradient Boosting': GradientBoostingClassifier(random_state=42),
            'AdaBoost': AdaBoostClassifier(random_state=42),
            'XGBoost': XGBClassifier(random_state=42, use_label_encoder=False,  eval_metric='logloss'),

        }

        results = {}

        # Suppress convergence warnings during training
        warnings.filterwarnings("ignore", category=ConvergenceWarning)
        warnings.filterwarnings("ignore", category=UserWarning)

        for name, model in models.items():
            try:
                # Create a pipeline with scaling and the model
                pipeline = Pipeline([
                    ('scaler', scaler),
                    ('model', model)
                ])

                # Train the pipeline
                pipeline.fit(X_train, y_train)

                # Predict on the test set
                y_pred = pipeline.predict(X_test)

                # Calculate accuracy
                accuracy = accuracy_score(y_test, y_pred)*100
                results[name] = {'accuracy': accuracy, 'model': pipeline}

                print(f"Model: {name}")
                print(f"Accuracy: {accuracy:.2f}%\n")
                report = classification_report(y_test, y_pred, target_names=['No PCOS (0)', 'PCOS (1)'])
                print(f"\n Detailed {name} Report :")
                print(report)
                print("-"*50)

            except Exception as model_error:
                print(f"--- Error training model {name}: {model_error} ---")
        
        print('Select model to save by number')
        model_names = list(results.keys())
        for i, model in enumerate(results.keys()):
            print(f"{i}. {model}")

        joblib.dump(results[model_names[int(input("Enter model number: "))]]['model'], 'pcos.pkl')

    print("--- standerscaler out --->91.7%,but recall=89% ---")



# --- General Exception Handling ---
except KeyError as e:
    print(f"--- FATAL ERROR: A required column is missing from the file: {e} ---")
    print("--- Please review the column names in your file. ---")

except ValueError as e:
    print(f"---  A data value error occurred (ValueError): {e} ---")
    print("--- This might be due to non-numeric data that could not be converted. ---")

except Exception as e:
    # Catch any other unexpected error
    print(f"--- An unexpected general error occurred: {e} ---")

print("\n--- Code execution finished. ---")



