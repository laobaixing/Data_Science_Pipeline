# Stock Analysis
> This project builds a pipeline to automatically update and analyze stock. It manages the whole data processing, analyzing and modeling through Luigi and demonstrates the results through Python Dash and other methods. Please note, the aim of the project is to provide a pipeline for general data science analysis instead of a solution for stock trading.


## Table of Contents
* [General Info](#general-information)
* [Technologies Used](#technologies-used)
* [Features](#features)
* [Screenshots](#screenshots)
* [Setup](#setup)
* [Usage](#usage)
* [Project Status](#project-status)
* [Room for Improvement](#room-for-improvement)



## General Information
- The aim of this project is to build a pipeline for automatic data science analysis. 
- It is used as an example for general data science analysis instead of a solution for stock trading.
- So optimizing the model performance on stock price is not the high priority.
- However, although it is not suitable for high frequency trading, it could be a good framework for people to manage their tools/metrics for mid term stock trading.




## Technologies Used
- Python 3.0
- Luigi
- Python Dash
- Statistical and machine learning
  - Linear regression
  - Mixed model
  - XGBoost
  - ARIMA (upload soon)
  - LSTM (upload soon)


## Work flow
- Data processing
  - Data extraction
  - Feature engineering
- Model building
- Model evaluation
- Visualization


## Screenshots
- Luigi management
<img src = ./img/luigi.png width=90% height=90%>
<img src = ./img/luigi_workflowD3.png width=90% height=90%>
- Exploratory data analysis by Python Dash
<img src = ./img/EDA.png width=90% height=90%>
- Residual plots demonstrated by Python Dash with Tabs <br />   
Apparently the model results are not good enough.
<img src =./img/Residuals.png width=90% height=90%>



## Setup
1. Clone the Github
2. Install the necessary packages



## Usage
1. Run: luigid --port 8082 in a terminal. This command line will start a Luigi. 
2. Run: python stock_analysis_pipeline.py in the stock_analyis folder
3. Look at:
   - Luigi at localhost:8082;
   - stock chart at localhost:8050;
   - model evaluation at localhost:8000


## Project Status
Project is: _in progress_. 


## Room for Improvement

Room for improvement:
- Add some exploratory data analysis (EDA)
- Upload the ARIMA code for Luigi
- Upload the LSTM code for Luigi

To do:
- Move the pipeline AWS or GCP
- Add more model evaluation methods
- Add NLP analysis on Stock 10-K, 10-Q report




