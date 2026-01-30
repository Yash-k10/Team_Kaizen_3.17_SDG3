"""Machine Learning Model for Organ Donation Matching"""
import os
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, roc_auc_score, average_precision_score
import lightgbm as lgb
from database import DatabaseManager, Donor, Match, SOSCase, BloodGroup, OrganType, DonorType

class MLMatchingModel:
    def __init__(self, model_path="data/match_model.pkl"):
        self.model_path = model_path
        self.model = None
        self.feature_names = [
            'blood_compatible',
            'organ_match',
            'age_compatible',
            'distance_normalized',
            'urgency_weight',
            'reliability_score',
            'freshness_score',
            'compatibility_score'
        ]
    
    def generate_synthetic_training_data(self, n_samples=5000):
        """
        Generate synthetic training data for matching model
        
        Returns:
            X: Feature matrix
            y: Labels (1 for successful match, 0 for unsuccessful)
        """
        np.random.seed(42)
        
        data = []
        
        for _ in range(n_samples):
            # Generate features
            blood_compatible = np.random.choice([0, 1], p=[0.3, 0.7])
            organ_match = np.random.choice([0, 1], p=[0.2, 0.8])
            age_compatible = np.random.choice([0, 1], p=[0.3, 0.7])
            distance_normalized = np.random.beta(2, 5)  # Prefer closer distances
            urgency_weight = np.random.uniform(0.2, 1.0)
            reliability_score = np.random.beta(5, 2)  # Prefer higher reliability
            freshness_score = np.random.beta(3, 2)
            
            # Compatibility score (derived feature)
            compatibility_score = (
                blood_compatible * 0.4 +
                organ_match * 0.3 +
                age_compatible * 0.2 +
                (1 - distance_normalized) * 0.1
            )
            
            # Generate label based on features (with some noise)
            # High compatibility + urgency + reliability = likely success
            success_probability = (
                blood_compatible * 0.3 +
                organ_match * 0.25 +
                age_compatible * 0.15 +
                (1 - distance_normalized) * 0.1 +
                urgency_weight * 0.1 +
                reliability_score * 0.05 +
                freshness_score * 0.05
            )
            
            # Add noise
            success_probability = np.clip(success_probability + np.random.normal(0, 0.1), 0, 1)
            success = 1 if success_probability > 0.6 else 0
            
            data.append([
                blood_compatible,
                organ_match,
                age_compatible,
                distance_normalized,
                urgency_weight,
                reliability_score,
                freshness_score,
                compatibility_score,
                success
            ])
        
        df = pd.DataFrame(data, columns=self.feature_names + ['success'])
        X = df[self.feature_names].values
        y = df['success'].values
        
        return X, y
    
    def train(self, X=None, y=None):
        """
        Train LightGBM model for match prediction
        
        Args:
            X: Feature matrix (if None, generates synthetic data)
            y: Labels (if None, generates synthetic data)
        """
        print("🎯 Training ML Matching Model...")
        
        # Generate synthetic data if not provided
        if X is None or y is None:
            print("📊 Generating synthetic training data...")
            X, y = self.generate_synthetic_training_data(n_samples=5000)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"Training samples: {len(X_train)}, Test samples: {len(X_test)}")
        print(f"Positive rate (train): {y_train.mean():.2%}")
        
        # Train LightGBM model
        train_data = lgb.Dataset(X_train, label=y_train, feature_name=self.feature_names)
        test_data = lgb.Dataset(X_test, label=y_test, reference=train_data, feature_name=self.feature_names)
        
        params = {
            'objective': 'binary',
            'metric': 'auc',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.9,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': -1,
            'max_depth': 6,
            'min_child_samples': 20
        }
        
        self.model = lgb.train(
            params,
            train_data,
            num_boost_round=200,
            valid_sets=[train_data, test_data],
            valid_names=['train', 'test'],
            callbacks=[lgb.log_evaluation(period=50), lgb.early_stopping(stopping_rounds=20)]
        )
        
        # Evaluate
        self.evaluate(X_test, y_test)
        
        # Save model
        self.save_model()
        
        print("✅ Model training complete!")
    
    def evaluate(self, X_test, y_test, k_values=[5, 10, 20]):
        """Evaluate model performance"""
        print("\n📊 Model Evaluation:")
        print("=" * 50)
        
        # Predictions
        y_pred_proba = self.model.predict(X_test)
        y_pred = (y_pred_proba > 0.5).astype(int)
        
        # Basic metrics
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        avg_precision = average_precision_score(y_test, y_pred_proba)
        
        print(f"Precision: {precision:.4f}")
        print(f"Recall: {recall:.4f}")
        print(f"ROC-AUC: {roc_auc:.4f}")
        print(f"Average Precision (AP): {avg_precision:.4f}")
        
        # Precision@K and Recall@K
        print("\nRanking Metrics:")
        for k in k_values:
            if len(y_test) >= k:
                # Get top-k predictions
                top_k_indices = np.argsort(y_pred_proba)[-k:]
                precision_at_k = y_test[top_k_indices].mean()
                print(f"Precision@{k}: {precision_at_k:.4f}")
        
        # Feature importance
        print("\n🎯 Feature Importance:")
        importance = self.model.feature_importance(importance_type='gain')
        feature_importance = sorted(zip(self.feature_names, importance), key=lambda x: x[1], reverse=True)
        for feat, imp in feature_importance:
            print(f"{feat:25s}: {imp:8.2f}")
        
        print("=" * 50)
    
    def save_model(self):
        """Save trained model to disk"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        print(f"✅ Model saved to {self.model_path}")
    
    def load_model(self):
        """Load trained model from disk"""
        if os.path.exists(self.model_path):
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            print(f"✅ Model loaded from {self.model_path}")
            return True
        else:
            print(f"⚠️ Model file not found: {self.model_path}")
            return False
    
    def predict_proba(self, features):
        """
        Predict match probability
        
        Args:
            features: List or array of feature values
        
        Returns:
            Probability of successful match (0-1)
        """
        if self.model is None:
            raise ValueError("Model not trained or loaded")
        
        if isinstance(features, list):
            features = np.array(features).reshape(1, -1)
        
        proba = self.model.predict(features)
        return proba[0] if len(proba) == 1 else proba

def train_and_save_model():
    """Train and save the matching model"""
    model = MLMatchingModel()
    model.train()
    return model

if __name__ == "__main__":
    # Train model with synthetic data
    print("🚀 Starting ML Model Training...\n")
    model = train_and_save_model()
    print("\n✨ Training complete! Model ready for use.")
