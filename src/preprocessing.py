"""
Data Preprocessing Module for Placement Predictor
Handles data cleaning, missing values, outliers, and encoding
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler
from sklearn.impute import SimpleImputer
import warnings
warnings.filterwarnings('ignore')


class DataPreprocessor:
    """
    Comprehensive data preprocessing class for placement prediction
    """
    
    def __init__(self):
        self.label_encoders = {}
        self.scaler = None
        self.imputer_numeric = None
        self.imputer_categorical = None
        
    def load_data(self, filepath):
        """
        Load data from CSV file
        
        Args:
            filepath (str): Path to the CSV file
            
        Returns:
            pd.DataFrame: Loaded dataframe
        """
        try:
            df = pd.read_csv(filepath)
            print(f" Data loaded successfully: {df.shape[0]} rows, {df.shape[1]} columns")
            return df
        except Exception as e:
            print(f" Error loading data: {str(e)}")
            return None
    
    def explore_data(self, df):
        """
        Print basic information about the dataset
        
        Args:
            df (pd.DataFrame): Input dataframe
        """
        print("\n" + "="*60)
        print("DATA OVERVIEW")
        print("="*60)
        print(f"\nShape: {df.shape}")
        print(f"\nColumn Names and Types:")
        print(df.dtypes)
        print(f"\nMissing Values:")
        print(df.isnull().sum())
        print(f"\nBasic Statistics:")
        print(df.describe())
        print(f"\nFirst few rows:")
        print(df.head())
        
    def handle_missing_values(self, df, numeric_strategy='mean', categorical_strategy='most_frequent'):
        """
        Handle missing values in the dataset
        
        Args:
            df (pd.DataFrame): Input dataframe
            numeric_strategy (str): Strategy for numeric columns ('mean', 'median', 'constant')
            categorical_strategy (str): Strategy for categorical columns ('most_frequent', 'constant')
            
        Returns:
            pd.DataFrame: Dataframe with missing values handled
        """
        df_copy = df.copy()
        
        # Identify numeric and categorical columns
        numeric_cols = df_copy.select_dtypes(include=['int64', 'float64']).columns
        categorical_cols = df_copy.select_dtypes(include=['object']).columns
        
        # Handle numeric missing values
        if len(numeric_cols) > 0 and df_copy[numeric_cols].isnull().sum().sum() > 0:
            self.imputer_numeric = SimpleImputer(strategy=numeric_strategy)
            df_copy[numeric_cols] = self.imputer_numeric.fit_transform(df_copy[numeric_cols])
            print(f" Numeric missing values handled using '{numeric_strategy}' strategy")
        
        # Handle categorical missing values
        if len(categorical_cols) > 0 and df_copy[categorical_cols].isnull().sum().sum() > 0:
            self.imputer_categorical = SimpleImputer(strategy=categorical_strategy)
            df_copy[categorical_cols] = self.imputer_categorical.fit_transform(df_copy[categorical_cols])
            print(f" Categorical missing values handled using '{categorical_strategy}' strategy")
        
        return df_copy
    
    def remove_duplicates(self, df):
        """
        Remove duplicate rows from the dataset
        
        Args:
            df (pd.DataFrame): Input dataframe
            
        Returns:
            pd.DataFrame: Dataframe without duplicates
        """
        initial_rows = df.shape[0]
        df_clean = df.drop_duplicates()
        removed_rows = initial_rows - df_clean.shape[0]
        
        if removed_rows > 0:
            print(f" Removed {removed_rows} duplicate rows")
        else:
            print(" No duplicate rows found")
            
        return df_clean
    
    def handle_outliers(self, df, columns=None, method='iqr', threshold=1.5):
        """
        Handle outliers in numeric columns
        
        Args:
            df (pd.DataFrame): Input dataframe
            columns (list): List of columns to check for outliers (None = all numeric)
            method (str): Method to use ('iqr', 'zscore')
            threshold (float): Threshold for outlier detection
            
        Returns:
            pd.DataFrame: Dataframe with outliers handled
        """
        df_copy = df.copy()
        
        if columns is None:
            columns = df_copy.select_dtypes(include=['int64', 'float64']).columns.tolist()
        
        outliers_count = 0
        
        for col in columns:
            if method == 'iqr':
                Q1 = df_copy[col].quantile(0.25)
                Q3 = df_copy[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                outliers = ((df_copy[col] < lower_bound) | (df_copy[col] > upper_bound)).sum()
                outliers_count += outliers
                
                # Cap outliers instead of removing
                df_copy[col] = df_copy[col].clip(lower=lower_bound, upper=upper_bound)
                
            elif method == 'zscore':
                z_scores = np.abs((df_copy[col] - df_copy[col].mean()) / df_copy[col].std())
                outliers = (z_scores > threshold).sum()
                outliers_count += outliers
                
                # Cap outliers
                mean = df_copy[col].mean()
                std = df_copy[col].std()
                df_copy[col] = df_copy[col].clip(
                    lower=mean - threshold * std,
                    upper=mean + threshold * std
                )
        
        if outliers_count > 0:
            print(f" Handled {outliers_count} outliers using '{method}' method")
        else:
            print(" No outliers detected")
            
        return df_copy
    
    def encode_categorical(self, df, columns=None, encoding_type='label'):
        """
        Encode categorical variables
        
        Args:
            df (pd.DataFrame): Input dataframe
            columns (list): List of columns to encode (None = all categorical)
            encoding_type (str): Type of encoding ('label', 'onehot')
            
        Returns:
            pd.DataFrame: Dataframe with encoded categorical variables
        """
        df_copy = df.copy()
        
        if columns is None:
            columns = df_copy.select_dtypes(include=['object']).columns.tolist()
        
        if encoding_type == 'label':
            for col in columns:
                if col in df_copy.columns:
                    self.label_encoders[col] = LabelEncoder()
                    df_copy[col] = self.label_encoders[col].fit_transform(df_copy[col].astype(str))
            print(f" Label encoding applied to {len(columns)} categorical columns")
                    
        elif encoding_type == 'onehot':
            df_copy = pd.get_dummies(df_copy, columns=columns, drop_first=True)
            print(f" One-hot encoding applied to {len(columns)} categorical columns")
        
        return df_copy
    
    def scale_features(self, df, columns=None, method='standard'):
        """
        Scale numeric features
        
        Args:
            df (pd.DataFrame): Input dataframe
            columns (list): List of columns to scale (None = all numeric)
            method (str): Scaling method ('standard', 'minmax')
            
        Returns:
            pd.DataFrame: Dataframe with scaled features
        """
        df_copy = df.copy()
        
        if columns is None:
            columns = df_copy.select_dtypes(include=['int64', 'float64']).columns.tolist()
        
        if method == 'standard':
            self.scaler = StandardScaler()
        elif method == 'minmax':
            self.scaler = MinMaxScaler()
        
        if len(columns) > 0:
            df_copy[columns] = self.scaler.fit_transform(df_copy[columns])
            print(f" {method.capitalize()} scaling applied to {len(columns)} numeric columns")
        
        return df_copy
    
    def preprocess_pipeline(self, df, target_column=None, handle_outliers_flag=True, 
                           encoding_type='label', scaling_method='standard'):
        """
        Complete preprocessing pipeline
        
        Args:
            df (pd.DataFrame): Input dataframe
            target_column (str): Name of the target column to exclude from scaling
            handle_outliers_flag (bool): Whether to handle outliers
            encoding_type (str): Type of categorical encoding
            scaling_method (str): Type of feature scaling
            
        Returns:
            pd.DataFrame: Fully preprocessed dataframe
        """
        print("\n" + "="*60)
        print("STARTING PREPROCESSING PIPELINE")
        print("="*60 + "\n")
        
        # Step 1: Remove duplicates
        df = self.remove_duplicates(df)
        
        # Step 2: Handle missing values
        df = self.handle_missing_values(df)
        
        # Step 3: Encode categorical variables (before outlier handling)
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        if target_column and target_column in categorical_cols:
            # Encode target separately if needed
            other_categorical = [col for col in categorical_cols if col != target_column]
            if other_categorical:
                df = self.encode_categorical(df, columns=other_categorical, encoding_type=encoding_type)
        else:
            if categorical_cols:
                df = self.encode_categorical(df, columns=categorical_cols, encoding_type=encoding_type)
        
        # Step 4: Handle outliers (only numeric columns)
        if handle_outliers_flag:
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            if target_column and target_column in numeric_cols:
                numeric_cols.remove(target_column)
            if numeric_cols:
                df = self.handle_outliers(df, columns=numeric_cols)
        
        # Step 5: Scale features (exclude target column)
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        if target_column and target_column in numeric_cols:
            numeric_cols.remove(target_column)
        if numeric_cols:
            df = self.scale_features(df, columns=numeric_cols, method=scaling_method)
        
        print("\n" + "="*60)
        print("PREPROCESSING COMPLETED")
        print("="*60 + "\n")
        
        return df
    
    def save_processed_data(self, df, filepath):
        """
        Save processed dataframe to CSV
        
        Args:
            df (pd.DataFrame): Processed dataframe
            filepath (str): Path to save the file
        """
        try:
            df.to_csv(filepath, index=False)
            print(f" Processed data saved to: {filepath}")
        except Exception as e:
            print(f" Error saving data: {str(e)}")


if __name__ == "__main__":
    # Example usage
    preprocessor = DataPreprocessor()
    
    # Load data
    df = preprocessor.load_data('data/raw/placement_data.csv')
    
    if df is not None:
        # Explore data
        preprocessor.explore_data(df)
        
        # Preprocess data
        df_processed = preprocessor.preprocess_pipeline(
            df, 
            target_column='status',  # Change based on your target column
            handle_outliers_flag=True,
            encoding_type='label',
            scaling_method='standard'
        )
        
        # Save processed data
        preprocessor.save_processed_data(df_processed, 'data/processed/placement_data_processed.csv')
