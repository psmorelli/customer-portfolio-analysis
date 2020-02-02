# Customer Portfolio Analysis
## Project 4 | Data Analysis Bootcamp - Ironhack

## Purpose

    The purpose of this project is to demonstrate the application of data analysis to guide strategic decisions for client portfolio management.
    For this project, a transaction dataset from a supermarket chain provided by Dunnhumby, a Customer Data Science consultancy, was used.
    Throughout this project, python scripts were developed using Pandas to transform the data and create metrics and dimensions. Public Tableau for creating analysis, dashboards and stories.


## Project Structure

    data_structure/
    |    |
    |    |_ 01_landing
    |    |    |
    |    |    |_ transactions_200607.csv
    |    |    |_ transactions_200608.csv
    |    |    |_ ...
    |    |    |_ transactions_200818.csv
    |    |    |_ transactions_200819.csv
    |    |
    |    |_ 02_staging
    |    |    |_ stg_transactions.csv
    |    |    
    |    |_ 03_dm
    |        |_ dm_customers.csv
    |        |_ dm_monthly_portfolio.csv
    |        |_ dm_portfolio_waterfall.csv
    |        
    etl
    |    |_ dm.py
    |    |_ staging.py
    |
    tableau_analysis
    |    |_ customers_portfolio_analysis.twb
    |    |_ dm_monthly_portfolio.hyper
    |    |_ Waterfall.hyper
    |
    etl_workflow.ipynb
    README.md

## Workflow

    * Data Gathering (landing data)
    * Define dimensions and metrics
    * Data Wrangling (staging and dm)
    * Define storytelling of analysis 
    * Create Tableau analysis

## Data Gathering (landing data)
    
    The data used in this project were made available by consultancy Dunnhumby and represents a dataset with 2 years of purchases made in an English supermarket chain.
    This database contains information regarding shopping baskets, customer identification, segmentation of customer sensitivity to price and store data.
    More details about the dataset can be found in the PDF file provided by the consultancy.
    
    Data Source:
[Let’s Get Sort-of-Real: Dummy Data to Test Techniques and Algorithms](https://www.dunnhumby.com/careers/engineering/sourcefiles)
    
    117 arquivo particionadas por semana foram utilizados, apenas uma amostra destes arquivo está no diretório data_structure/01_landing.

## Define dimensions and metrics

    It was necessary to define some concepts:
    
    Active : customers who made purchases in the analyzed period
    
    Customer Portfolio : From the date of the first purchase, each customer becomes part of the portfolio forever.
    
    Recency : Months since the last purchase.
    
    Inactive : Customers who are already part of the portfolio and who did not make any purchases during the analysis period.
    
    Reactivated : Customers who were inactive and made a new purchase.

## Data Wrangling (staging and dm)

    To simplify the process of creating metrics and dimensions, the data wrangling process was divided into two stages:
    
    Staging: Intermediate file with data from 117 unified files.
    
    DM: Data transformed and summarized according to the needs of analysis.

        * dm_customers.csv : customer dataset with price sensitivity segmentation.
        * dm_monthly_portfolio : Main analysis dataset, containing all the necessary metrics and dimensions with customer/month granularity.
        * dm_portfolio_waterfall : Used to create the visualization of portfolio movement monthly.

## Define storytelling of analysis

    The following analysis sequence was defined:

         1 - Monthly evolution of the portfolio and active customers.
    
         2 - Monthly movement of active customers, how many are new, how many become inactive and how many reactivate.
    
         3 - Percentage of reactivation due to downtime in months.
    
         4 - % of customer reactivation due to downtime segmented by price sensitivity.
    
         5 - Segment recommendation for reactivation campaign

## Create Tableau analysis

    A story published on the Public Tableau cloud service containing the analysis with highlights of insights.

Tableau Story:
[Customer Portfolio Analysis](https://public.tableau.com/profile/psmorelli#!/vizhome/customers_portfolio_analysis/CustomerPortfolioAnalysis)

    