import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.model_selection import TimeSeriesSplit
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple, Any, Optional

class MLEconomicPredictor:
    """
    A unified Machine Learning Economic Forecasting Engine.
    Exposes scikit-learn algorithms tailored for time-series forecasting.
    Provides TimeSeriesSplit validation and diagnostic feature importances.
    """
    
    SUPPORTED_MODELS = {
        'random_forest': RandomForestRegressor,
        'gradient_boosting': GradientBoostingRegressor,
        'linear': LinearRegression,
        'ridge': Ridge,
        'lasso': Lasso
    }

    def __init__(self, model_type: str = 'random_forest', **kwargs: Any):
        """
        Initialize the ML predictor.
        
        Args:
            model_type (str): Type of ML model ('random_forest', 'gradient_boosting', 'linear', 'ridge', 'lasso')
            **kwargs: Hyperparameters to pass to the scikit-learn model constructor
        """
        if model_type not in self.SUPPORTED_MODELS:
            raise ValueError(f"Unsupported model type '{model_type}'. Choose from {list(self.SUPPORTED_MODELS.keys())}")
        
        self.model_type = model_type
        self.model_class = self.SUPPORTED_MODELS[model_type]
        self.model = self.model_class(**kwargs)
        self.scaler = StandardScaler()
        self.feature_names: List[str] = []
        
    def create_lags(self, df: pd.DataFrame, target_col: str, lags: List[int], date_col: str = 'date') -> pd.DataFrame:
        """
        Helper method to create lag features for supervised time-series forecasting.
        
        Args:
            df (DataFrame): Historical DataFrame
            target_col (str): Target column to forecast
            lags (list): List of lag integers (e.g. [1, 2, 4, 12])
            date_col (str): Date column name
            
        Returns:
            DataFrame: Engineered DataFrame containing lag features and target, with dropped NaNs.
        """
        df_lags = df.copy().sort_values(date_col)
        
        lag_cols = []
        for lag in lags:
            col_name = f"{target_col}_lag_{lag}"
            df_lags[col_name] = df_lags[target_col].shift(lag)
            lag_cols.append(col_name)
            
        return df_lags.dropna().reset_index(drop=True)

    def fit(self, X: pd.DataFrame, y: pd.Series, scale_features: bool = False):
        """
        Fit the ML model on training features and target.
        """
        self.feature_names = list(X.columns)
        
        if scale_features:
            X_fit = self.scaler.fit_transform(X)
        else:
            X_fit = X.values
            
        self.model.fit(X_fit, y.values)
        return self

    def predict(self, X: pd.DataFrame, scale_features: bool = False) -> np.ndarray:
        """
        Predict target values using fitted model.
        """
        if scale_features:
            X_pred = self.scaler.transform(X)
        else:
            X_pred = X.values
            
        return self.model.predict(X_pred)

    @staticmethod
    def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        Calculate key economic forecasting accuracy metrics.
        """
        # Avoid division by zero in MAPE
        mask = y_true != 0
        if np.any(mask):
            mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
        else:
            mape = np.nan
            
        rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
        mae = np.mean(np.abs(y_true - y_pred))
        
        # Calculate R-squared manually
        ss_res = np.sum((y_true - y_pred) ** 2)
        ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
        r2 = 1.0 - (ss_res / ss_tot) if ss_tot != 0 else np.nan
        
        return {
            'RMSE': float(rmse),
            'MAE': float(mae),
            'MAPE': float(mape),
            'R2': float(r2)
        }

    def evaluate_out_of_sample(self, X: pd.DataFrame, y: pd.Series, test_size: int = 12) -> Tuple[Dict[str, float], np.ndarray, np.ndarray]:
        """
        Train the model on historical data and evaluate on the final out-of-sample split.
        """
        if len(X) <= test_size:
            raise ValueError(f"Dataset length ({len(X)}) must be larger than test_size ({test_size})")
            
        split_idx = len(X) - test_size
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        self.fit(X_train, y_train)
        y_pred = self.predict(X_test)
        
        metrics = self.calculate_metrics(y_test.values, y_pred)
        return metrics, y_test.values, y_pred

    def cross_validate_time_series(self, X: pd.DataFrame, y: pd.Series, n_splits: int = 5) -> Dict[str, Any]:
        """
        Perform rigorous walk-forward (TimeSeriesSplit) cross-validation.
        """
        tscv = TimeSeriesSplit(n_splits=n_splits)
        
        cv_metrics = []
        for fold, (train_idx, test_idx) in enumerate(tscv.split(X), 1):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
            
            self.fit(X_train, y_train)
            y_pred = self.predict(X_test)
            
            metrics = self.calculate_metrics(y_test.values, y_pred)
            metrics['fold'] = fold
            cv_metrics.append(metrics)
            
        df_cv = pd.DataFrame(cv_metrics)
        avg_metrics = df_cv.mean().to_dict()
        
        return {
            'avg_metrics': avg_metrics,
            'folds_details': cv_metrics
        }

    def get_feature_diagnostics(self) -> Dict[str, float]:
        """
        Extract feature importances (or coefficients for linear models).
        """
        if not self.feature_names:
            return {}
            
        diagnostics = {}
        if hasattr(self.model, 'feature_importances_'):
            # Random Forest, Gradient Boosting
            importances = self.model.feature_importances_
            diagnostics = dict(zip(self.feature_names, importances))
        elif hasattr(self.model, 'coef_'):
            # Linear models, Ridge, Lasso
            coefs = self.model.coef_
            diagnostics = dict(zip(self.feature_names, coefs))
            
        # Sort by magnitude descending
        return dict(sorted(diagnostics.items(), key=lambda x: abs(x[1]), reverse=True))


class PCAReductionHelper:
    """
    A diagnostic helper to perform Dimensionality Reduction using PCA on
    macroeconomic indicator panels before fitting forecasting or nowcasting models.
    """
    
    @staticmethod
    def extract_latent_factors(df: pd.DataFrame, columns: List[str], n_components: int = 3, prefix: str = 'factor') -> Tuple[pd.DataFrame, List[float]]:
        """
        Extract common latent factors from high-dimensional indicators.
        
        Args:
            df (DataFrame): Macroeconomic indicators DataFrame
            columns (list): Names of columns to reduce
            n_components (int): Number of components/factors to retain
            prefix (str): Column name prefix for saved factors
            
        Returns:
            Tuple[DataFrame, list]: DataFrame with factors, and explained variance ratios
        """
        X = df[columns].copy()
        
        # PCA requires scaling features to zero mean & unit variance
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        pca = PCA(n_components=n_components)
        factors = pca.fit_transform(X_scaled)
        
        df_out = df.copy()
        factor_cols = []
        for idx in range(n_components):
            col_name = f"{prefix}_{idx+1}"
            df_out[col_name] = factors[:, idx]
            factor_cols.append(col_name)
            
        explained_variance = list(pca.explained_variance_ratio_)
        print(f"[PCA] Extracted {n_components} factors. Total explained variance: {sum(explained_variance)*100:.2f}%")
        
        return df_out, explained_variance
