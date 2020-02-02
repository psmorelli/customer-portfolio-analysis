## Function for unifying weekly files into a single file

def transactions(input_file, output_file):
    import pandas as pd
    import numpy as np
    from os import path

    df = pd.read_csv(input_file, low_memory=False)

    # Lower case column names 
    df.columns = map(str.lower, list(df.columns))

    # Convert shop_date column type from INT to DATE
    df['shop_date'] = df['shop_date'].apply(lambda x: pd.to_datetime(str(x), format='%Y%m%d'))

    # Append rown to staging transactions file 
    if path.exists(output_file):
        df.to_csv(output_file, mode='a', header=False, index=False)
    else:
        df.to_csv(output_file, index=False)