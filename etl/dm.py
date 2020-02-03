#Function for extracting and transforming customer data

def customers(input_file, output_file):

    import pandas as pd
    import numpy as np
    from os import path

    df = pd.read_csv(input_file, low_memory=False)

    # Lower case column names 
    df.columns = map(str.lower, list(df.columns))

    df = df[['cust_code','cust_price_sensitivity','cust_lifestage']].drop_duplicates()

    # Price Sencitivity

    df['cust_price_sensitivity'] = np.where((df['cust_price_sensitivity'] == 'LA'),'Less Affluent' , df['cust_price_sensitivity'])
    df['cust_price_sensitivity'] = np.where((df['cust_price_sensitivity'] == 'MM'),'Mid Market' , df['cust_price_sensitivity'])
    df['cust_price_sensitivity'] = np.where((df['cust_price_sensitivity'] == 'UM'),'Up Market' , df['cust_price_sensitivity'])
    df['cust_price_sensitivity'] = np.where((df['cust_price_sensitivity'] == 'XX'),'unclassified' , df['cust_price_sensitivity'])

    # Life Stage
    
    df['cust_lifestage'] = np.where((df['cust_lifestage'] == 'YA'),'Young Adults' , df['cust_lifestage'])
    df['cust_lifestage'] = np.where((df['cust_lifestage'] == 'OA'),'Older Adults' , df['cust_lifestage'])
    df['cust_lifestage'] = np.where((df['cust_lifestage'] == 'YF'),'Young Families' , df['cust_lifestage'])
    df['cust_lifestage'] = np.where((df['cust_lifestage'] == 'OF'),'Older Families' , df['cust_lifestage'])
    df['cust_lifestage'] = np.where((df['cust_lifestage'] == 'PE'),'Pensioners' , df['cust_lifestage'])
    df['cust_lifestage'] = np.where((df['cust_lifestage'] == 'OT'),'Other' , df['cust_lifestage'])
    df['cust_lifestage'] = np.where((df['cust_lifestage'] == 'XX'),'unclassified' , df['cust_lifestage'])

    # Save file
    if path.exists(output_file):
        df.to_csv(output_file, mode='a', header=False, index=False)
    else:
        df.to_csv(output_file, index=False)

    print(input_file + ' already processed into ' + output_file)


#Function used for the creation of the customer portfolio and calculations of metrics and dimensions.

def monthly_portfolio(input_file, output_file):

    import pandas as pd
    import numpy as np

    df = pd.read_csv(input_file, low_memory=False)

    df['shop_month'] = pd.to_datetime(df['shop_date']).dt.to_period('M').dt.to_timestamp()

    df_monthly = (df.groupby(['shop_month','cust_code'])
    .agg({'basket_id' : 'nunique', 'spend' : 'sum'})
    .reset_index()
    .rename(columns={'basket_id' : 'frequency', 'spend' : 'value'}))

    df_monthly['active'] = 1

    months = list(pd.DataFrame(df_monthly['shop_month'].value_counts()).index)
    months.sort()

    col_names =  ['cust_code', 'shop_month']
    col_types = {'cust_code' : 'int64', 'shop_month' : 'datetime64'}

    df_monthly_portfolio = pd.DataFrame(columns = col_names)
    df_monthly_portfolio = df_monthly_portfolio.astype(col_types)

    for month in months:
        df_past = pd.DataFrame(df_monthly_portfolio['cust_code'].unique(), columns=['cust_code'])
        df_current = pd.DataFrame(df_monthly[df_monthly['shop_month'] == month]['cust_code'].unique(), columns=['cust_code'])
        df_ever = pd.concat([df_past,df_current]).drop_duplicates(keep='first')
        df_ever['shop_month'] = month
        df_monthly_portfolio = pd.concat([df_monthly_portfolio,df_ever], sort=False)
        df_monthly_portfolio.reset_index()

    df_monthly_portfolio = df_monthly_portfolio.merge(right=df_monthly,
                                                how='left',
                                                on=['cust_code','shop_month'])

    values = {'active': 0, 'purchase_frequency': 0, 'purchase_value': 0}
    df_monthly_portfolio = df_monthly_portfolio.fillna(value=values)

    # Customer vintage

    df_customer_vintage = (df_monthly_portfolio.groupby(['cust_code'])
    .agg({'shop_month' : 'min'})
    .reset_index()
    .rename(columns={'shop_month' : 'customer_vintage'}))

    df_monthly_portfolio = df_monthly_portfolio.merge(right=df_customer_vintage,
                                            how='left',
                                            on='cust_code')

    # Calculate customer MoB (Months on Book)

    months = pd.DataFrame(df_monthly_portfolio['shop_month'].unique(), columns=['shop_month'])
    months['shop_month_no'] = months['shop_month'].rank()

    months_vintage = pd.DataFrame(df_monthly_portfolio['shop_month'].unique(), columns=['customer_vintage'])
    months_vintage['vintage_month_no'] = months_vintage['customer_vintage'].rank()

    df_monthly_portfolio = df_monthly_portfolio.merge(right=months,
                                                how='left',
                                                on=['shop_month'])

    df_monthly_portfolio = df_monthly_portfolio.merge(right=months_vintage,
                                                how='left',
                                                on=['customer_vintage'])

    df_monthly_portfolio['customer_mob'] = df_monthly_portfolio['shop_month_no'] - df_monthly_portfolio['vintage_month_no']

    # Calculate customer Recency

    months = list(pd.DataFrame(df_monthly_portfolio['shop_month'].value_counts()).index)
    months.sort()

    # Return month before or after a specific month
    def month_lag_lead(date,operation):
        from datetime import datetime
        from dateutil.relativedelta import relativedelta
        
        if operation == 'lag':
            return date - relativedelta(months=1)
        elif operation == 'lead':
            return date + relativedelta(months=1)

    #function to calc recency
    def recency(active, recency_lag):

        if active == 1 and recency_lag > 0:
            return recency_lag + 1

        if active == 1 and recency_lag < 0:
            return 1

        if active == 0 and recency_lag > 0:
            return -1

        if active == 0 and recency_lag < 0:
            return recency_lag - 1
        
        else:
            return 1

    col_names =  ['cust_code','shop_month','recency']
    col_types = {'cust_code' : 'int64', 'shop_month' : 'datetime64', 'recency' : 'int64'}

    df_recency = pd.DataFrame(columns = col_names)
    df_recency = df_recency.astype(col_types)

    for month in months:
        
        df_lag_recency = df_recency[df_recency['shop_month'] == month_lag_lead(month,'lag')][['cust_code','recency']]
        df_active = df_monthly_portfolio[df_monthly_portfolio['shop_month'] == month][['cust_code','shop_month','active']]
        df_active = df_active.merge(right=df_lag_recency,
                                                    how='left',
                                                    on=['cust_code'])
        df_active['recency'] = df_active.apply(lambda x: recency(x['active'],x['recency']),axis=1)
        
        df_recency = pd.concat([df_recency,df_active[['cust_code','shop_month','recency']]], sort=False)
        df_recency.reset_index()

    df_monthly_portfolio = df_monthly_portfolio.merge(right=df_recency,
                                                how='left',
                                                on=['cust_code','shop_month'])

    # Recency Lag (1 month)

    df_recency_lag = df_monthly_portfolio[['cust_code','shop_month','recency']]
    df_recency_lag['shop_month'] = df_recency_lag.apply(lambda x: month_lag_lead(x['shop_month'],'lead'),axis=1)
    df_recency_lag.columns = ['cust_code','shop_month','recency_lag']

    df_monthly_portfolio = df_monthly_portfolio.merge(right=df_recency_lag,
                                                how='left',
                                                on=['cust_code','shop_month']
                                                )

    # Customer Price Sensitivity and Life Stage

    df_customer = pd.read_csv('data_structure/03_dm/dm_customers.csv')

    df_monthly_portfolio = df_monthly_portfolio.merge(right=df_customer,
                                            how='left',
                                            on=['cust_code']
                                            )

    # Save file
    df_monthly_portfolio.to_csv(output_file, index=False)


#Function to calc indicators of portfolio moviment

def portfolio_waterfall(input_file, output_file):

    import pandas as pd
    import numpy as np

    df = pd.read_csv(input_file, low_memory=False)

    # Calc customers active last month
    df_active_last_month = (df[df['recency_lag'] > 0].groupby(['shop_month'])
    .agg({'cust_code' : 'nunique'})
    .reset_index()
    .rename(columns={'cust_code' : 'active_last_month'}))

    # Calc new active customers
    df_new_customers = (df[df['customer_mob'] == 0].groupby(['shop_month'])
    .agg({'cust_code' : 'nunique'})
    .reset_index()
    .rename(columns={'cust_code' : 'new_customers'}))

    # Calc reactivate customers
    df_reactive = (df[(df['recency_lag'] < 0) & (df['recency'] > 0)].groupby(['shop_month'])
    .agg({'cust_code' : 'nunique'})
    .reset_index()
    .rename(columns={'cust_code' : 'reactive'}))

    # Calc inactive customers
    df_inactive = (df[(df['recency_lag'] > 0) & (df['recency'] < 0)].groupby(['shop_month'])
    .agg({'cust_code' : 'nunique'})
    .reset_index()
    .rename(columns={'cust_code' : 'inactive'}))

    # Calc current active customers
    df_active_current = (df[df['active'] == 1].groupby(['shop_month'])
    .agg({'cust_code' : 'nunique'})
    .reset_index()
    .rename(columns={'cust_code' : 'current_active'}))

    # Merge all indicators
    df_waterfall = df_active_last_month.merge(right=df_new_customers,
                                            how='left',
                                            on=['shop_month']
                                            )

    df_waterfall = df_waterfall.merge(right=df_reactive,
                                            how='left',
                                            on=['shop_month']
                                            )

    df_waterfall = df_waterfall.merge(right=df_inactive,
                                            how='left',
                                            on=['shop_month']
                                            )

    df_waterfall = df_waterfall.merge(right=df_active_current,
                                            how='left',
                                            on=['shop_month']
                                            )

    # Create a column to identify values rows
    df_waterfall['type'] = 'values'


    # Calc aux values to facilitate waterfall visualization on Tableau
    df_waterfall_aux = df_waterfall[['shop_month']] 

    df_waterfall_aux['active_last_month'] = 0

    df_waterfall_aux['new_customers'] = df_waterfall['active_last_month'] 

    df_waterfall_aux['reactive'] = df_waterfall['active_last_month'] + df_waterfall['new_customers']

    df_waterfall_aux['inactive'] = df_waterfall['active_last_month'] + df_waterfall['new_customers'] + df_waterfall['reactive'] - df_waterfall['inactive']

    df_waterfall_aux['current_active'] = 0

    df_waterfall_aux['type'] = 'aux'

    df_waterfall = pd.concat([df_waterfall,df_waterfall_aux], sort=False)

    # Save file
    df_waterfall.to_csv(output_file, index=False)