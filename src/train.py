"""
Model Training Module for Placement Predictor
Trains and evaluates multiple ML models
"""

import pandas as pd
import numpy as np
import pickle
import json
from datetime import datetime
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                             f1_score, confusion_matrix, classification_report,
                             roc_auc_score, roc_curve)
import warnings
warnings.filterwarnings('ignore')


class PlacementPredictor:
    """
    Model training and evaluation class
    """
    
    def __init__(self):
        self.models = {}
        self.results = {}
        self.best_model = None
        self.best_model_name = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        
    def load_data(self, filepath, target_column):
        """
        Load and split data
        
        Args:
            filepath (str): Path to processed data
            target_column (str): Name of target column
            
        Returns:
            tuple: X_train, X_test, y_train, y_test
        """
        df = pd.read_csv(filepath)
        print(f" Data loaded: {df.shape[0]} rows, {df.shape[1]} columns")
        
        # Separate features and target
        X = df.drop(columns=[target_column])
        y = df[target_column]
        
        # Train-test split
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f" Train set: {self.X_train.shape[0]} samples")
        print(f" Test set: {self.X_test.shape[0]} samples")
        
        return self.X_train, self.X_test, self.y_train, self.y_test
    
    def initialize_models(self):
        """
        Initialize multiple ML models
        """
        self.models = {
            'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
            'Decision Tree': DecisionTreeClassifier(random_state=42),
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
            'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
            'AdaBoost': AdaBoostClassifier(n_estimators=100, random_state=42),
            'Support Vector Machine': SVC(kernel='rbf', probability=True, random_state=42),
            'K-Nearest Neighbors': KNeighborsClassifier(n_neighbors=5),
            'Naive Bayes': GaussianNB()
        }
        
        print(f" Initialized {len(self.models)} models")
        
    def train_model(self, model_name, model):
        """
        Train a single model and evaluate it
        
        Args:
            model_name (str): Name of the model
            model: Model instance
            
        Returns:
            dict: Evaluation metrics
        """
        # Train model
        model.fit(self.X_train, self.y_train)
        
        # Predictions
        y_train_pred = model.predict(self.X_train)
        y_test_pred = model.predict(self.X_test)
        
        # Probabilities (if available)
        try:
            y_test_proba = model.predict_proba(self.X_test)[:, 1]
        except:
            y_test_proba = None
        
        # Calculate metrics
        metrics = {
            'train_accuracy': accuracy_score(self.y_train, y_train_pred),
            'test_accuracy': accuracy_score(self.y_test, y_test_pred),
            'precision': precision_score(self.y_test, y_test_pred, average='weighted', zero_division=0),
            'recall': recall_score(self.y_test, y_test_pred, average='weighted', zero_division=0),
            'f1_score': f1_score(self.y_test, y_test_pred, average='weighted', zero_division=0),
            'confusion_matrix': confusion_matrix(self.y_test, y_test_pred).tolist()
        }
        
        # Add ROC AUC for binary classification
        if len(np.unique(self.y_train)) == 2 and y_test_proba is not None:
            metrics['roc_auc'] = roc_auc_score(self.y_test, y_test_proba)
        
        # Cross-validation score
        cv_scores = cross_val_score(model, self.X_train, self.y_train, cv=5, scoring='accuracy')
        metrics['cv_mean'] = cv_scores.mean()
        metrics['cv_std'] = cv_scores.std()
        
        return metrics
    
    def train_all_models(self):
        """
        Train all initialized models
        """
        print("\n" + "="*60)
        print("TRAINING MODELS")
        print("="*60 + "\n")
        
        for model_name, model in self.models.items():
            print(f"Training {model_name}...")
            metrics = self.train_model(model_name, model)
            self.results[model_name] = metrics
            
            print(f" Test Accuracy: {metrics['test_accuracy']:.4f}")
            print(f" F1 Score: {metrics['f1_score']:.4f}")
            print(f" CV Score: {metrics['cv_mean']:.4f} (+/- {metrics['cv_std']:.4f})")
            print()
        
        # Find best model
        best_model_name = max(self.results.keys(), 
                            key=lambda k: self.results[k]['test_accuracy'])
        self.best_model = self.models[best_model_name]
        self.best_model_name = best_model_name
        
        print("="*60)
        print(f"BEST MODEL: {self.best_model_name}")
        print(f"Test Accuracy: {self.results[best_model_name]['test_accuracy']:.4f}")
        print("="*60 + "\n")
    
    def get_results_summary(self):
        """
        Get summary of all model results
        
        Returns:
            pd.DataFrame: Results summary
        """
        results_df = pd.DataFrame(self.results).T
        results_df = results_df.drop(columns=['confusion_matrix'])
        results_df = results_df.sort_values('test_accuracy', ascending=False)
        
        print("\n" + "="*60)
        print("MODEL COMPARISON")
        print("="*60)
        print(results_df.round(4))
        print()
        
        return results_df
    
    def hyperparameter_tuning(self, model_name, param_grid):
        """
        Perform hyperparameter tuning on a specific model
        
        Args:
            model_name (str): Name of the model to tune
            param_grid (dict): Parameter grid for GridSearchCV
            
        Returns:
            dict: Best parameters and score
        """
        print(f"\n Hyperparameter tuning for {model_name}...")
        
        model = self.models[model_name]
        grid_search = GridSearchCV(
            model, param_grid, cv=5, scoring='accuracy', 
            n_jobs=-1, verbose=1
        )
        
        grid_search.fit(self.X_train, self.y_train)
        
        # Update model with best parameters
        self.models[model_name] = grid_search.best_estimator_
        
        # Retrain and evaluate
        metrics = self.train_model(model_name, grid_search.best_estimator_)
        self.results[model_name] = metrics
        
        print(f" Best parameters: {grid_search.best_params_}")
        print(f" Best CV score: {grid_search.best_score_:.4f}")
        print(f" Test accuracy: {metrics['test_accuracy']:.4f}")
        
        return {
            'best_params': grid_search.best_params_,
            'best_score': grid_search.best_score_,
            'test_accuracy': metrics['test_accuracy']
        }
    
    def get_feature_importance(self, top_n=10):
        """
        Get feature importance from best model (if available)
        
        Args:
            top_n (int): Number of top features to display
            
        Returns:
            pd.DataFrame: Feature importance
        """
        if not hasattr(self.best_model, 'feature_importances_'):
            print(" Best model doesn't support feature importance")
            return None
        
        importance_df = pd.DataFrame({
            'feature': self.X_train.columns,
            'importance': self.best_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\n" + "="*60)
        print(f"TOP {top_n} IMPORTANT FEATURES ({self.best_model_name})")
        print("="*60)
        print(importance_df.head(top_n))
        print()
        
        return importance_df
    
    def get_classification_report(self):
        """
        Get detailed classification report for best model
        """
        y_pred = self.best_model.predict(self.X_test)
        
        print("\n" + "="*60)
        print(f"CLASSIFICATION REPORT ({self.best_model_name})")
        print("="*60)
        print(classification_report(self.y_test, y_pred))
        print("\nConfusion Matrix:")
        print(confusion_matrix(self.y_test, y_pred))
        print()
    
    def save_model(self, model_name=None, filepath='models/best_model.pkl'):
        """
        Save trained model to file
        
        Args:
            model_name (str): Name of model to save (None = best model)
            filepath (str): Path to save the model
        """
        if model_name is None:
            model_to_save = self.best_model
            model_name = self.best_model_name
        else:
            model_to_save = self.models[model_name]
        
        # Save model
        with open(filepath, 'wb') as f:
            pickle.dump(model_to_save, f)
        
        # Save metadata
        metadata = {
            'model_name': model_name,
            'train_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'metrics': self.results[model_name],
            'feature_columns': self.X_train.columns.tolist()
        }
        
        metadata_path = filepath.replace('.pkl', '_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=4)
        
        print(f" Model saved to: {filepath}")
        print(f" Metadata saved to: {metadata_path}")
    
    def save_results(self, filepath='models/training_results.json'):
        """
        Save all training results to JSON file
        
        Args:
            filepath (str): Path to save results
        """
        results_to_save = {}
        for model_name, metrics in self.results.items():
            results_to_save[model_name] = {
                k: v for k, v in metrics.items() 
                if k != 'confusion_matrix'
            }
        
        with open(filepath, 'w') as f:
            json.dump(results_to_save, f, indent=4)
        
        print(f" Training results saved to: {filepath}")


def main():
    """
    Main training pipeline
    """
    print("="*60)
    print("PLACEMENT PREDICTOR - MODEL TRAINING")
    print("="*60 + "\n")
    
    # Initialize predictor
    predictor = PlacementPredictor()
    
    # Load data
    predictor.load_data(
        filepath='data/processed/placement_data_featured.csv',
        target_column='status'  # Change based on your target column
    )
    
    # Initialize and train models
    predictor.initialize_models()
    predictor.train_all_models()
    
    # Get results summary
    results_df = predictor.get_results_summary()
    
    # Get feature importance
    predictor.get_feature_importance(top_n=10)
    
    # Get classification report
    predictor.get_classification_report()
    
    # Optional: Hyperparameter tuning for best model
    if predictor.best_model_name == 'Random Forest':
        param_grid = {
            'n_estimators': [100, 200],
            'max_depth': [10, 20, None],
            'min_samples_split': [2, 5]
        }
        predictor.hyperparameter_tuning('Random Forest', param_grid)
    
    # Save best model
    predictor.save_model(filepath='models/best_model.pkl')
    predictor.save_results(filepath='models/training_results.json')
    
    print("\n Training pipeline completed successfully!")


if __name__ == "__main__":
    main()
