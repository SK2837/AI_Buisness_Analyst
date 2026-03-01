import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Any, List, Optional, Tuple

class StatsEngine:
    """
    Service for performing statistical analysis on data.
    """

    @staticmethod
    def calculate_trend(df: pd.DataFrame, date_col: str, value_col: str) -> Dict[str, Any]:
        """
        Calculate linear trend for a time series.
        
        Args:
            df: DataFrame containing the data
            date_col: Name of the date column
            value_col: Name of the value column
            
        Returns:
            Dictionary containing trend direction, slope, r_squared, and description.
        """
        if df.empty or len(df) < 2:
            return {
                "direction": "insufficient_data",
                "slope": 0,
                "r_squared": 0,
                "description": "Not enough data to calculate trend"
            }
            
        # Ensure date column is datetime
        try:
            dates = pd.to_datetime(df[date_col])
            # Convert dates to ordinal for regression
            x = dates.map(pd.Timestamp.toordinal)
            y = df[value_col]
            
            # Perform linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            # Determine direction
            if slope > 0:
                direction = "increasing"
            elif slope < 0:
                direction = "decreasing"
            else:
                direction = "stable"
                
            # Calculate percent change over the period based on the trend line
            start_val = slope * x.min() + intercept
            end_val = slope * x.max() + intercept
            
            if start_val != 0:
                pct_change = ((end_val - start_val) / abs(start_val)) * 100
            else:
                pct_change = 0
                
            return {
                "direction": direction,
                "slope": float(slope),
                "r_squared": float(r_value ** 2),
                "pct_change": float(pct_change),
                "description": f"Trend is {direction} with a {pct_change:.1f}% change over the period (R²={r_value**2:.2f})"
            }
            
        except Exception as e:
            return {
                "direction": "error",
                "error": str(e),
                "description": "Failed to calculate trend"
            }

    @staticmethod
    def detect_anomalies(df: pd.DataFrame, value_col: str, method: str = 'zscore', threshold: float = 3.0) -> List[Dict[str, Any]]:
        """
        Detect anomalies in a data series.
        
        Args:
            df: DataFrame containing the data
            value_col: Name of the value column
            method: 'zscore' or 'iqr'
            threshold: Z-score threshold or IQR multiplier
            
        Returns:
            List of dictionaries representing anomalous rows
        """
        if df.empty:
            return []
            
        anomalies = []
        values = df[value_col].dropna()
        
        if method == 'zscore':
            z_scores = np.abs(stats.zscore(values))
            anomaly_indices = np.where(z_scores > threshold)[0]
            
            for idx in anomaly_indices:
                # Map back to original dataframe index
                original_idx = values.index[idx]
                row = df.loc[original_idx].to_dict()
                row['anomaly_score'] = float(z_scores[idx])
                row['anomaly_reason'] = f"Z-score: {z_scores[idx]:.2f} (> {threshold})"
                anomalies.append(row)
                
        elif method == 'iqr':
            Q1 = values.quantile(0.25)
            Q3 = values.quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            
            anomaly_mask = (values < lower_bound) | (values > upper_bound)
            anomaly_indices = values[anomaly_mask].index
            
            for idx in anomaly_indices:
                row = df.loc[idx].to_dict()
                val = values[idx]
                if val < lower_bound:
                    score = (lower_bound - val) / IQR
                    reason = f"Value {val} is below lower bound {lower_bound:.2f}"
                else:
                    score = (val - upper_bound) / IQR
                    reason = f"Value {val} is above upper bound {upper_bound:.2f}"
                    
                row['anomaly_score'] = float(score)
                row['anomaly_reason'] = reason
                anomalies.append(row)
                
        return anomalies

    @staticmethod
    def calculate_summary_stats(df: pd.DataFrame, numeric_cols: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Calculate summary statistics for numeric columns.
        
        Args:
            df: DataFrame
            numeric_cols: List of columns to analyze (optional, defaults to all numeric)
            
        Returns:
            Dictionary of statistics per column
        """
        if df.empty:
            return {}
            
        if numeric_cols is None:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
        stats_dict = {}
        for col in numeric_cols:
            if col not in df.columns:
                continue
                
            series = df[col].dropna()
            if series.empty:
                continue
                
            stats_dict[col] = {
                "mean": float(series.mean()),
                "median": float(series.median()),
                "min": float(series.min()),
                "max": float(series.max()),
                "std_dev": float(series.std()),
                "sum": float(series.sum()),
                "count": int(series.count())
            }
            
        return stats_dict
