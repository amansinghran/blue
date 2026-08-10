import pandas as pd

def YKK(uploaded_file):
    
    required_columns = ["Grouped By Paycode Name", "Employee ID", "Employee Full Name", "Actual Total Apply Date", "Hours"]

    df = pd.read_excel(uploaded_file, usecols=required_columns)

    df = df.rename(columns={
        "Employee Full Name": "Employee Name",
        "Actual Total Apply Date": "Date"})
    
    df = df[~df["Grouped By Paycode Name"].astype(str).str.contains("absent", case=False, na=False)]
    df = df.dropna(subset=["Employee ID", "Date", "Hours"])
    df = df[df["Hours"] != 0]
    
    df["Employee ID"] = df["Employee ID"].astype(int)
    df["Date"] = pd.to_datetime(df["Date"], format="mixed").dt.strftime("%d/%m/%Y")
    
    df_aggregated = df.groupby(["Employee ID", "Date"], as_index=False).agg(
        {"Hours": "sum", "Employee Name": "first"})
    
    max_date = pd.to_datetime(df_aggregated["Date"], format="%d/%m/%Y").max()
    df_aggregated["Weekend"] = pd.offsets.Week(weekday=6).rollforward(max_date).strftime("%m%d%Y")
    
    df_aggregated = df_aggregated[["Employee ID", "Employee Name", "Date", "Hours", "Weekend"]]

    return df_aggregated