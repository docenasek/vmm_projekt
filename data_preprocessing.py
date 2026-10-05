import pandas as pd

def data_preprocessing(df):

    # Handle missing values
    df.ffill()
    
    # Convert categorical columns to numerical
    #categorical_cols = df.select_dtypes(include=['object']).columns
    #df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

    return df

if __name__ == "__main__":
    processed_df = data_preprocessing(pd.read_csv('shots_outcome_Final.csv'))
    print(processed_df.head())