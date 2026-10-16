import pandas as pd

def USL(uploaded_file):
    
    required_columns = ["Position ID", "Payroll Name", "In Date", "Tot Hrs Worked"]
    
    df = pd.read_excel(uploaded_file, usecols=required_columns)
    
    df = df.rename(columns={"Position ID": "Employee ID",
                           "Payroll Name": "Employee Name",
                           "In Date": "Date",
                           "Tot Hrs Worked": "Hours"})
    
    df = df.dropna(subset=["Date"])
    df["Hours"] = pd.to_numeric(df["Hours"], errors="coerce").fillna(0)
    df = df[df["Hours"] != 0]
    df["Employee ID"] = df["Employee ID"].astype(str)
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%m/%d/%Y")
    
    df_aggregated = (
        df.groupby(["Employee ID", "Date"], as_index=False)
        .agg({"Hours": "sum", "Employee Name": "first"}))
    
    max_date = pd.to_datetime(df_aggregated["Date"], format="%m/%d/%Y").max()
    df_aggregated["Weekend"] = pd.offsets.Week(weekday=5).rollforward(max_date).strftime("%m%d%Y")
    
    df_aggregated = df_aggregated[["Employee ID", "Employee Name", "Date", "Hours", "Weekend"]]

    return df_aggregated