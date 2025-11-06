"""
Feature Engineering Module for Placement Predictor
Handles feature creation, selection, and transformation
"""

import pandas as pd
import numpy as np
from sklearn.feature_selection import SelectKBest, chi2, f_classif, mutual_info_classif
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
import warnings
warnings.filterwarnings('ignore')


class FeatureEngineer:
    """
    Feature engineering class for creating and selecting features
    """
    
    def __init__(self):
        self.feature_selector = None
        self.pca = None
        self.feature_importance = None
        
    def create_academic_features(self, df):
        """
        Create features related to academic performance
        
        Common features for placement datasets:
        - Average academic score
        - Academic consistency
        - Overall performance grade
        
        Args:
            df (pd.DataFrame): Input dataframe
            
        Returns:
            pd.DataFrame: Dataframe with new academic features
        """
        df_copy = df.copy()
        
        # Identify percentage/score columns (common patterns)
        score_columns = [col for col in df_copy.columns if any(
            keyword in col.lower() for keyword in ['percentage', 'cgpa', 'score', 'marks', 'gpa']
        )]
        
        if len(score_columns) >= 2:
            # Average academic performance
            df_copy['avg_academic_score'] = df_copy[score_columns].mean(axis=1)
            
            # Academic consistency (standard deviation)
            df_copy['academic_consistency'] = df_copy[score_columns].std(axis=1)
            
            # Academic improvement (if sequential scores available)
            if len(score_columns) >= 3:
                df_copy['academic_trend'] = df_copy[score_columns].diff(axis=1).mean(axis=1)
            
            print(f" Created academic features from {len(score_columns)} score columns")
        
        return df_copy
    
    def create_interaction_features(self, df, feature_pairs=None):
        """
        Create interaction features between pairs of columns
        
        Args:
            df (pd.DataFrame): Input dataframe
            feature_pairs (list): List of tuples with feature pairs to interact
            
        Returns:
            pd.DataFrame: Dataframe with interaction features
        """
        df_copy = df.copy()
        
        if feature_pairs is None:
            # Auto-detect numeric columns for interactions
            numeric_cols = df_copy.select_dtypes(include=['int64', 'float64']).columns.tolist()
            
            # Create interactions for first few numeric columns (avoid explosion)
            if len(numeric_cols) >= 2:
                feature_pairs = [(numeric_cols[i], numeric_cols[i+1]) 
                                for i in range(min(3, len(numeric_cols)-1))]
        
        if feature_pairs:
            for col1, col2 in feature_pairs:
                if col1 in df_copy.columns and col2 in df_copy.columns:
                    # Multiplication interaction
                    df_copy[f'{col1}_x_{col2}'] = df_copy[col1] * df_copy[col2]
                    
                    # Ratio interaction (avoid division by zero)
                    df_copy[f'{col1}_div_{col2}'] = df_copy[col1] / (df_copy[col2] + 1e-6)
            
            print(f" Created {len(feature_pairs) * 2} interaction features")
        
        return df_copy
    
    def create_polynomial_features(self, df, columns=None, degree=2):
        """
        Create polynomial features for numeric columns
        
        Args:
            df (pd.DataFrame): Input dataframe
            columns (list): Columns to create polynomial features for
            degree (int): Degree of polynomial
            
        Returns:
            pd.DataFrame: Dataframe with polynomial features
        """
        df_copy = df.copy()
        
        if columns is None:
            columns = df_copy.select_dtypes(include=['int64', 'float64']).columns.tolist()[:3]
        
        for col in columns:
            if col in df_copy.columns:
                for d in range(2, degree + 1):
                    df_copy[f'{col}_pow_{d}'] = df_copy[col] ** d
        
        print(f" Created polynomial features (degree {degree}) for {len(columns)} columns")
        
        return df_copy
    
    def create_binning_features(self, df, columns=None, n_bins=4):
        """
        Create binned/discretized versions of continuous features
        
        Args:
            df (pd.DataFrame): Input dataframe
            columns (list): Columns to bin
            n_bins (int): Number of bins
            
        Returns:
            pd.DataFrame: Dataframe with binned features
        """
        df_copy = df.copy()
        
        if columns is None:
            columns = df_copy.select_dtypes(include=['int64', 'float64']).columns.tolist()[:3]
        
        for col in columns:
            if col in df_copy.columns:
                df_copy[f'{col}_binned'] = pd.qcut(
                    df_copy[col], 
                    q=n_bins, 
                    labels=False, 
                    duplicates='drop'
                )
        
        print(f" Created binned features ({n_bins} bins) for {len(columns)} columns")
        
        return df_copy
    
    def create_aggregate_features(self, df, group_by_col=None):
        """
        Create aggregate features based on groupings
        
        Args:
            df (pd.DataFrame): Input dataframe
            group_by_col (str): Column to group by
            
        Returns:
            pd.DataFrame: Dataframe with aggregate features
        """
        df_copy = df.copy()
        
        if group_by_col and group_by_col in df_copy.columns:
            numeric_cols = df_copy.select_dtypes(include=['int64', 'float64']).columns.tolist()
            
            for col in numeric_cols[:3]:  # Limit to avoid too many features
                # Group-wise mean
                group_mean = df_copy.groupby(group_by_col)[col].transform('mean')
                df_copy[f'{col}_group_mean'] = group_mean
                
                # Difference from group mean
                df_copy[f'{col}_diff_from_group'] = df_copy[col] - group_mean
            
            print(f" Created aggregate features grouped by '{group_by_col}'")
        
        return df_copy
    
    def select_features_statistical(self, df, target_column, k=10, method='f_classif'):
        """
        Select top K features using statistical tests
        
        Args:
            df (pd.DataFrame): Input dataframe
            target_column (str): Name of target column
            k (int): Number of top features to select
            method (str): Selection method ('f_classif', 'chi2', 'mutual_info')
            
        Returns:
            tuple: (selected dataframe, list of selected features)
        """
        df_copy = df.copy()
        
        # Separate features and target
        X = df_copy.drop(columns=[target_column])
        y = df_copy[target_column]
        
        # Select scoring function
        if method == 'f_classif':
            score_func = f_classif
        elif method == 'chi2':
            score_func = chi2
            # chi2 requires non-negative features
            X = X - X.min() + 1e-6
        elif method == 'mutual_info':
            score_func = mutual_info_classif
        else:
            score_func = f_classif
        
        # Select features
        k = min(k, X.shape[1])  # Ensure k doesn't exceed number of features
        self.feature_selector = SelectKBest(score_func=score_func, k=k)
        X_selected = self.feature_selector.fit_transform(X, y)
        
        # Get selected feature names
        selected_features = X.columns[self.feature_selector.get_support()].tolist()
        
        # Create dataframe with selected features
        df_selected = pd.DataFrame(X_selected, columns=selected_features)
        df_selected[target_column] = y.values
        
        print(f" Selected top {k} features using '{method}' method")
        print(f" Selected features: {selected_features}")
        
        return df_selected, selected_features
    
    def select_features_importance(self, df, target_column, k=10):
        """
        Select features based on Random Forest feature importance
        
        Args:
            df (pd.DataFrame): Input dataframe
            target_column (str): Name of target column
            k (int): Number of top features to select
            
        Returns:
            tuple: (selected dataframe, list of selected features, importance dict)
        """
        df_copy = df.copy()
        
        # Separate features and target
        X = df_copy.drop(columns=[target_column])
        y = df_copy[target_column]
        
        # Train Random Forest to get feature importance
        rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        rf.fit(X, y)
        
        # Get feature importance
        importance = pd.DataFrame({
            'feature': X.columns,
            'importance': rf.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Select top K features
        k = min(k, len(importance))
        selected_features = importance.head(k)['feature'].tolist()
        
        # Create dataframe with selected features
        df_selected = df_copy[selected_features + [target_column]]
        
        self.feature_importance = importance
        
        print(f" Selected top {k} features using Random Forest importance")
        print(f" Top 5 features: {selected_features[:5]}")
        
        return df_selected, selected_features, importance.set_index('feature')['importance'].to_dict()
    
    def apply_pca(self, df, target_column=None, n_components=0.95):
        """
        Apply PCA for dimensionality reduction
        
        Args:
            df (pd.DataFrame): Input dataframe
            target_column (str): Name of target column to exclude
            n_components (float or int): Number of components or variance ratio
            
        Returns:
            pd.DataFrame: Dataframe with PCA components
        """
        df_copy = df.copy()
        
        # Separate features and target
        if target_column:
            X = df_copy.drop(columns=[target_column])
            y = df_copy[target_column]
        else:
            X = df_copy
            y = None
        
        # Apply PCA
        self.pca = PCA(n_components=n_components, random_state=42)
        X_pca = self.pca.fit_transform(X)
        
        # Create new dataframe
        pca_columns = [f'PC{i+1}' for i in range(X_pca.shape[1])]
        df_pca = pd.DataFrame(X_pca, columns=pca_columns)
        
        if y is not None:
            df_pca[target_column] = y.values
        
        explained_variance = sum(self.pca.explained_variance_ratio_) * 100
        print(f" PCA applied: {X_pca.shape[1]} components explain {explained_variance:.2f}% variance")
        
        return df_pca
    
    def get_feature_statistics(self, df, target_column=None):
        """
        Get comprehensive statistics about features
        
        Args:
            df (pd.DataFrame): Input dataframe
            target_column (str): Name of target column
            
        Returns:
            pd.DataFrame: Feature statistics
        """
        if target_column:
            features = df.drop(columns=[target_column])
        else:
            features = df
        
        stats = pd.DataFrame({
            'dtype': features.dtypes,
            'missing': features.isnull().sum(),
            'missing_pct': (features.isnull().sum() / len(features) * 100).round(2),
            'unique': features.nunique(),
            'mean': features.select_dtypes(include=['int64', 'float64']).mean(),
            'std': features.select_dtypes(include=['int64', 'float64']).std(),
            'min': features.select_dtypes(include=['int64', 'float64']).min(),
            'max': features.select_dtypes(include=['int64', 'float64']).max()
        })
        
        print("\n" + "="*60)
        print("FEATURE STATISTICS")
        print("="*60)
        print(stats)
        
        return stats
    
    def feature_engineering_pipeline(self, df, target_column, 
                                    create_academic=True,
                                    create_interactions=True,
                                    create_polynomial=False,
                                    create_binning=False,
                                    select_features=True,
                                    selection_method='importance',
                                    n_features=15):
        """
        Complete feature engineering pipeline
        
        Args:
            df (pd.DataFrame): Input dataframe
            target_column (str): Name of target column
            create_academic (bool): Create academic-related features
            create_interactions (bool): Create interaction features
            create_polynomial (bool): Create polynomial features
            create_binning (bool): Create binned features
            select_features (bool): Apply feature selection
            selection_method (str): Feature selection method
            n_features (int): Number of features to select
            
        Returns:
            tuple: (engineered dataframe, selected features list)
        """
        print("\n" + "="*60)
        print("STARTING FEATURE ENGINEERING PIPELINE")
        print("="*60 + "\n")
        
        df_engineered = df.copy()
        
        # Create new features
        if create_academic:
            df_engineered = self.create_academic_features(df_engineered)
        
        if create_interactions:
            df_engineered = self.create_interaction_features(df_engineered)
        
        if create_polynomial:
            df_engineered = self.create_polynomial_features(df_engineered, degree=2)
        
        if create_binning:
            numeric_cols = df_engineered.select_dtypes(include=['int64', 'float64']).columns.tolist()
            if target_column in numeric_cols:
                numeric_cols.remove(target_column)
            if numeric_cols:
                df_engineered = self.create_binning_features(df_engineered, columns=numeric_cols[:2])
        
        print(f"\n Feature engineering created {df_engineered.shape[1] - df.shape[1]} new features")
        print(f" Total features: {df_engineered.shape[1] - 1} (excluding target)")
        
        # Feature selection
        selected_features = None
        if select_features and df_engineered.shape[1] > n_features + 1:
            if selection_method == 'importance':
                df_engineered, selected_features, _ = self.select_features_importance(
                    df_engineered, target_column, k=n_features
                )
            else:
                df_engineered, selected_features = self.select_features_statistical(
                    df_engineered, target_column, k=n_features, method=selection_method
                )
        
        print("\n" + "="*60)
        print("FEATURE ENGINEERING COMPLETED")
        print("="*60 + "\n")
        
        return df_engineered, selected_features


if __name__ == "__main__":
    # Example usage
    engineer = FeatureEngineer()
    
    # Load processed data
    df = pd.read_csv('data/processed/placement_data_processed.csv')
    
    # Apply feature engineering
    df_engineered, selected_features = engineer.feature_engineering_pipeline(
        df,
        target_column='status',  # Change based on your target column
        create_academic=True,
        create_interactions=True,
        create_polynomial=False,
        select_features=True,
        selection_method='importance',
        n_features=15
    )
    
    # Save engineered features
    df_engineered.to_csv('data/processed/placement_data_featured.csv', index=False)
    print(" Feature-engineered data saved")
