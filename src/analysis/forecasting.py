import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller
from pmdarima import auto_arima
from arch import arch_model
from statsforecast import StatsForecast
from statsforecast.models import AutoARIMA, AutoETS
from statsmodels.tsa.api import VAR
from statsmodels.tsa.ardl import ARDL, ardl_select_order

class EconometricAnalyst:
    """
    Utility class for econometric analysis and time-series forecasting.
    """
    
    @staticmethod
    def check_stationarity(series):
        """Perform Augmented Dickey-Fuller test."""
        res = adfuller(series.dropna())
        return {
            'adf_stat': res[0],
            'p_value': res[1],
            'critical_values': res[4],
            'is_stationary': res[1] < 0.05
        }

    @staticmethod
    def fit_ardl(endog, exog, max_p=4, max_q=4, selection_criterion='aic'):
        """Fit an ARDL model with automatic lag selection."""
        sel_res = ardl_select_order(
            endog, max_p, exog, max_q, ic=selection_criterion, trend='c'
        )
        model = sel_res.model
        results = model.fit()
        return results, (sel_res.ar_lags, sel_res.dl_lags)

    @staticmethod
    def fit_var(df, maxlags=15, criterion='aic'):
        """Fit a Vector Autoregression (VAR) model."""
        model = VAR(df)
        results = model.fit(maxlags=maxlags, ic=criterion)
        return results

    @staticmethod
    def auto_arima_forecast(series, periods=12):
        """Fit Auto-ARIMA and forecast."""
        model = auto_arima(series, seasonal=True, stepwise=True, suppress_warnings=True)
        forecast, conf_int = model.predict(n_periods=periods, return_conf_int=True)
        return forecast, conf_int, model.summary()

    @staticmethod
    def fit_garch(series, p=1, q=1):
        """Fit GARCH model."""
        model = arch_model(series.dropna(), vol='Garch', p=p, q=q)
        res = model.fit(disp='off')
        return res

    @staticmethod
    def fast_batch_forecast(df, freq, h=12, models=None):
        """High-performance batch forecasting using StatsForecast."""
        if models is None:
            models = [AutoARIMA(season_length=12), AutoETS(season_length=12)]
        
        sf = StatsForecast(
            models=models,
            freq=freq,
            n_jobs=-1
        )
        forecast_df = sf.forecast(df=df, h=h)
        return forecast_df
