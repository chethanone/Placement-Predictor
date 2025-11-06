"""
Prediction Module for Placement Predictor
Load trained models and make predictions
"""

import pandas as pd
import numpy as np
import pickle
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class PlacementPredictorInference:
    """
    Inference class for making predictions with trained models
    """
    
    def __init__(self, model_path='models/best_model.pkl'):
        """
        Initialize predictor with trained model
        
        Args:
            model_path (str): Path to saved model
        """
        self.model = None
        self.metadata = None
        self.feature_columns = None
        self.load_model(model_path)
        
    def load_model(self, model_path):
        """
        Load trained model and metadata
        
        Args:
            model_path (str): Path to saved model
        """
        try:
            # Load model
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            print(f" Model loaded from: {model_path}")
            
            # Load metadata
            metadata_path = model_path.replace('.pkl', '_metadata.json')
            try:
                with open(metadata_path, 'r') as f:
                    self.metadata = json.load(f)
                self.feature_columns = self.metadata['feature_columns']
                print(f" Metadata loaded")
                print(f" Model: {self.metadata['model_name']}")
                print(f" Trained on: {self.metadata['train_date']}")
                print(f" Test Accuracy: {self.metadata['metrics']['test_accuracy']:.4f}")
            except FileNotFoundError:
                print(" Metadata file not found")
                
        except FileNotFoundError:
            print(f" Model file not found: {model_path}")
            raise
        except Exception as e:
            print(f" Error loading model: {str(e)}")
            raise
    
    def predict_single(self, input_data):
        """
        Make prediction for a single sample
        
        Args:
            input_data (dict): Dictionary with feature names and values
            
        Returns:
            dict: Prediction result with probability
        """
        # Convert to DataFrame
        df = pd.DataFrame([input_data])
        
        # Ensure correct column order
        if self.feature_columns:
            # Add missing columns with default value 0
            for col in self.feature_columns:
                if col not in df.columns:
                    df[col] = 0
            df = df[self.feature_columns]
        
        # Make prediction
        prediction = self.model.predict(df)[0]
        
        # Get probability if available
        try:
            probability = self.model.predict_proba(df)[0]
            prob_dict = {f'class_{i}': prob for i, prob in enumerate(probability)}
        except:
            prob_dict = None
        
        # Handle prediction label
        if isinstance(prediction, str):
            prediction_label = prediction
        else:
            prediction_label = 'Placed' if prediction == 1 else 'Not Placed'
        
        result = {
            'prediction': str(prediction),
            'prediction_label': prediction_label,
            'probabilities': prob_dict,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return result
    
    def predict_batch(self, input_file, output_file=None):
        """
        Make predictions for multiple samples from CSV
        
        Args:
            input_file (str): Path to input CSV file
            output_file (str): Path to save predictions (optional)
            
        Returns:
            pd.DataFrame: DataFrame with predictions
        """
        # Load data
        df = pd.read_csv(input_file)
        print(f" Loaded {len(df)} samples from {input_file}")
        
        # Ensure correct columns
        if self.feature_columns:
            for col in self.feature_columns:
                if col not in df.columns:
                    df[col] = 0
            df_features = df[self.feature_columns]
        else:
            df_features = df
        
        # Make predictions
        predictions = self.model.predict(df_features)
        
        # Get probabilities if available
        try:
            probabilities = self.model.predict_proba(df_features)
            df['prediction_probability'] = probabilities[:, 1]
        except:
            pass
        
        # Add predictions to dataframe
        df['prediction'] = predictions
        df['prediction_label'] = ['Placed' if p == 1 else 'Not Placed' for p in predictions]
        
        # Save if output file specified
        if output_file:
            df.to_csv(output_file, index=False)
            print(f" Predictions saved to: {output_file}")
        
        print(f" Predictions completed")
        print(f" Placed: {sum(predictions == 1)}")
        print(f" Not Placed: {sum(predictions == 0)}")
        
        return df
    
    def predict_from_input(self):
        """
        Interactive prediction from user input
        """
        print("\n" + "="*60)
        print("INTERACTIVE PREDICTION")
        print("="*60 + "\n")
        
        if not self.feature_columns:
            print(" Feature columns not available. Cannot proceed.")
            return
        
        print(f"Please provide values for the following features:")
        print(f"(Press Enter to use default value 0)\n")
        
        input_data = {}
        for feature in self.feature_columns:
            value = input(f"{feature}: ").strip()
            if value == '':
                input_data[feature] = 0
            else:
                try:
                    input_data[feature] = float(value)
                except ValueError:
                    input_data[feature] = value
        
        # Make prediction
        result = self.predict_single(input_data)
        
        # Display result
        print("\n" + "="*60)
        print("PREDICTION RESULT")
        print("="*60)
        print(f"Prediction: {result['prediction_label']}")
        if result['probabilities']:
            print(f"\nProbabilities:")
            for class_name, prob in result['probabilities'].items():
                print(f" {class_name}: {prob:.4f}")
        print(f"\nTimestamp: {result['timestamp']}")
        print("="*60 + "\n")
        
        return result
    
    def get_model_info(self):
        """
        Display model information
        """
        print("\n" + "="*60)
        print("MODEL INFORMATION")
        print("="*60)
        
        if self.metadata:
            print(f"Model Name: {self.metadata['model_name']}")
            print(f"Training Date: {self.metadata['train_date']}")
            print(f"\nPerformance Metrics:")
            for metric, value in self.metadata['metrics'].items():
                if metric not in ['confusion_matrix', 'best_params']:
                    if isinstance(value, (int, float)):
                        print(f" {metric}: {value:.4f}")
                    else:
                        print(f" {metric}: {value}")
            print(f"\nNumber of Features: {len(self.feature_columns)}")
        else:
            print("Metadata not available")
        
        print("="*60 + "\n")


def main():
    """
    Main prediction pipeline
    """
    import sys
    
    print("="*60)
    print("PLACEMENT PREDICTOR - INFERENCE")
    print("="*60 + "\n")
    
    # Initialize predictor
    predictor = PlacementPredictorInference(model_path='models/best_model.pkl')
    
    # Display model info
    predictor.get_model_info()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == 'batch' and len(sys.argv) > 2:
            # Batch prediction mode
            input_file = sys.argv[2]
            output_file = sys.argv[3] if len(sys.argv) > 3 else 'predictions.csv'
            
            print(f" Running batch prediction...")
            predictions_df = predictor.predict_batch(input_file, output_file)
            
        elif mode == 'single':
            # Single prediction mode with sample data
            sample_data = {
                # Add your feature names here with sample values
                # Example:
                # 'ssc_p': 67.00,
                # 'hsc_p': 91.00,
                # 'degree_p': 58.00,
                # 'workex': 0,
                # 'etest_p': 55.00,
                # 'specialisation': 1,
                # 'mba_p': 58.80
            }
            
            print(f" Making single prediction...")
            result = predictor.predict_single(sample_data)
            
            print("\n" + "="*60)
            print("PREDICTION RESULT")
            print("="*60)
            print(f"Prediction: {result['prediction_label']}")
            if result['probabilities']:
                print(f"\nProbabilities:")
                for class_name, prob in result['probabilities'].items():
                    print(f" {class_name}: {prob:.4f}")
            print("="*60 + "\n")
            
        else:
            print("Usage:")
            print(" python predict.py batch <input_file> [output_file]")
            print(" python predict.py single")
            print(" python predict.py interactive")
    else:
        # Interactive mode (default)
        predictor.predict_from_input()


if __name__ == "__main__":
    main()
