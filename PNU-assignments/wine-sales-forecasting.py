# -*- coding: utf-8 -*-
"""assignment2 (1).ipynb

    Wine Sales Forecasting
    Time-series analysis of monthly wine sales in Australia. Built a linear trend and seasonal regression model with residual correction using ARIMA. 
    Forecasts and results visualized with training/test data split.

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Ytv8oBGcm77xrn77jXmiRFqRnhM9cYXv
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.formula.api as sm
from statsmodels.tsa import tsatools
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.tsa.arima.model import ARIMA

wine_df = pd.read_csv('AustralianWines.csv')
wine_df['Month'] = pd.to_datetime(wine_df['Month'], format='%Y-%m')
wine_df.set_index('Month', inplace=True)
wine_df.head()

fig, axes = plt.subplots(nrows=6, ncols=1, figsize=(10, 12), sharex=True)
for i, col in enumerate(wine_df.columns):
    axes[i].plot(wine_df.index, wine_df[col])
    axes[i].set_ylabel(f'{col} sales')
    axes[i].set_xlabel('Time')
plt.tight_layout()
plt.show()

fortified_ts = pd.Series(wine_df['Fortified'].values, index=wine_df.index, name='Fortified')
fortified_df = tsatools.add_trend(fortified_ts, trend='ct')
fortified_df['Month'] = fortified_df.index.month

fortified_lm = sm.ols('Fortified ~ trend', data=fortified_df).fit()

ax = fortified_ts.plot(label='Fortified wine sales', figsize=(10, 4))
fortified_lm.predict(fortified_df).plot(ax=ax, label='Trend line', color='orange')
ax.set_xlabel('Time')
ax.set_ylabel('Fortified wine sales')
ax.legend()
plt.show()

train_df = fortified_df[:'1993-12-01']
valid_df = fortified_df['1994-01-01':]

model = sm.ols('Fortified ~ trend + C(Month)', data=train_df).fit()
print(model.summary())

fortified_lm = sm.ols(formula='Fortified ~ trend + C(Month)', data=train_df).fit()

ax = train_df.plot(y='Fortified', color='C0', linewidth=0.75, label='Training', figsize=(10, 4))
valid_df.plot(y='Fortified', ax=ax, color='C0', linestyle='dashed', linewidth=0.75, label='Validation')

fortified_lm.predict(train_df).plot(ax=ax, color='C1', label='Fit')
fortified_lm.predict(valid_df).plot(ax=ax, color='C1', linestyle='dashed', label='Forecast')

ax.set_xlabel('Time')
ax.set_ylabel('Fortified wine sales')
ax.legend()
plt.show()

last_trend = fortified_df['trend'].iloc[-1]

future_df = pd.DataFrame({
    'trend': [last_trend + 1, last_trend + 2],
    'Month': [8, 9]
}, index=[pd.Timestamp('1995-08-01'), pd.Timestamp('1995-09-01')])

fortified_lm_full = sm.ols('Fortified ~ trend + C(Month)', data=fortified_df).fit()

forecast = fortified_lm_full.predict(future_df)

print(f"Forecast August 1995: {forecast.loc['1995-08-01']:.2f}")
print(f"Forecast September 1995: {forecast.loc['1995-09-01']:.2f}")

residuals = fortified_lm_full.resid
plot_acf(residuals, lags=12)
plt.show()

ar_model = ARIMA(residuals, order=(12,0,0), freq='MS', trend='n').fit()
ar_model.summary()

forecast_reg = fortified_lm_full.predict(future_df)
aug_reg = forecast_reg.loc['1995-08-01']
sep_reg = forecast_reg.loc['1995-09-01']

resid_forecast = ar_model.forecast(steps=2)
aug_corr = resid_forecast.iloc[0]
sep_corr = resid_forecast.iloc[1]

aug_final = aug_reg + aug_corr
sep_final = sep_reg + sep_corr

print(f"Corrected forecast for August 1995: {aug_final:.2f}")
print(f"Corrected forecast for September 1995: {sep_final:.2f}")
