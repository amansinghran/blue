import pandas as pd

def IAP(uploaded_file):
    required_columns = ["EmployeeNumber", "FullName", "Date", "Duration"]
    
    df = pd.read_excel(uploaded_file, usecols=required_columns)
    
    rename_map = {
        "EmployeeNumber": "Employee ID",
        "FullName": "Employee Name",
        "Date": "Date",
        "Duration": "Hours"
    }
    
    df = df.rename(columns=rename_map)
    
    df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%d/%m/%Y')
    
    df_aggregated = df.groupby(['Employee ID', 'Date'], as_index=False).agg(
        {
            'Hours': 'sum',
            'Employee Name': 'first',
        }
    )    

    df_aggregated = df_aggregated[['Employee ID', 'Employee Name', 'Date', 'Hours']]
    
    return df_aggregated