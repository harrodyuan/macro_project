# Macro Event Trading Project

## Project Overview
This project analyzes the impact of economic events (CPI and Unemployment) on 2-Year and 10-Year Treasury Yields. We backtested intraday trading strategies to capitalize on the volatility following these releases.

## Key Findings
1.  **Trend Following vs. Reversion:**
    *   **Trend Following** (betting the initial move continues) generally **failed**.
    *   **Reversion** (fading the initial move) was historically profitable but has seen performance degrade in the last 18 months (flat PnL since Jan 2024).

2.  **The "Noise" Problem:**
    *   Trading every event leads to "churn" and losses on days with small data deviations.
    *   **Solution:** Filtering for **Significant Surprises** (e.g., `|Actual - Surveyed| >= 0.1%`) significantly improves the signal-to-noise ratio and restores profitability.

## Files Included
*   `economic_events_analysis.ipynb`: Initial data exploration and visualization of yield behavior around events.
*   `backtesting.ipynb`: The strategy engine. Contains the logic for Trend vs. Reversion and the "Significant Surprise" filter optimization.
*   `cleaned_cpi_data.csv` & `cleaned_unemployment_data.csv`: Processed intraday data used for the backtests.

## Next Steps: Neural Network Approach (NN)
To improve the strategy further, the next phase should involve **Machine Learning / Neural Networks**.

**Goal:** Predict the **probability of a Reversion** or the **Magnitude of the Move** before entering.

**Proposed Architecture:**
*   **Inputs (Features):**
    *   `Surprise_Magnitude` (Actual - Surveyed)
    *   `Pre_Event_Volatility` (Standard deviation of yields 1 hour before release)
    *   `Trend_Context` (Is the market already trending up/down on the daily timeframe?)
    *   `Previous_Event_Reaction` (How did the market react last month?)
*   **Target:**
    *   Binary Classification: `Will_Revert` (1 if Reversion PnL > 0, else 0)
    *   Regression: `Predicted_PnL`

**Teammate Action Items:**
1.  Review the "Optimization" section in `backtesting.ipynb`.
2.  Build a simple MLP (Multi-Layer Perceptron) using `PyTorch` or `TensorFlow`.
3.  Train on the `cleaned_*.csv` data to classify profitable reversion setups.
