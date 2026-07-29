import pandas as pd

def IAP(uploaded_file):
    
    required_columns = ["EmployeeNumber", "FullName", "Date", "Duration"]
    
    df = pd.read_excel(uploaded_file, usecols=required_columns)
    
    df = df.rename(columns={
        "EmployeeNumber": "Employee ID",
        "FullName": "Employee Name",
        "Duration": "Hours"
    })
    
    df = df.dropna(subset=["Date", "Hours"])
    df = df[df["Hours"] != 0]
    
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%d/%m/%Y")
    
    df_aggregated = df.groupby(["Employee ID", "Date"], as_index=False).agg(
        {"Hours": "sum", "Employee Name": "first"}
    )
    
    max_date = pd.to_datetime(df_aggregated["Date"], format="%d/%m/%Y").max()
    df_aggregated["Weekend"] = pd.offsets.Week(weekday=6).rollforward(max_date).strftime("%m%d%Y")
    
    df_aggregated = df_aggregated[["Employee ID", "Employee Name", "Date", "Hours", "Weekend"]]

    return df_aggregated