import pandas as pd

def NSY(uploaded_file):
    
    required_columns = ["Employee Number2", "Employee Name", "Shift Date", "Hours Paid"]

    df = pd.read_excel(uploaded_file, usecols=required_columns)

    df = df.rename(columns={
        "Employee Number2": "Employee ID",
        "Shift Date": "Date",
        "Hours Paid": "Hours"})
    
    df = df.dropna(subset=["Date", "Hours"])
    df["Hours"] = (pd.to_timedelta(df["Hours"].astype(str) + ":00") / pd.Timedelta(hours=1)).round(2)
    
    df = df[df["Hours"] != 0]
    df["Employee ID"] = df["Employee ID"].astype(int)
    df["Date"] = pd.to_datetime(df["Date"], format="mixed").dt.strftime("%m/%d/%Y")
    
    df_aggregated = df.groupby(["Employee ID", "Date"], as_index=False).agg(
        {"Hours": "sum", "Employee Name": "first"})
    
    max_date = pd.to_datetime(df_aggregated["Date"], format="%m/%d/%Y").max()
    df_aggregated["Weekend"] = pd.offsets.Week(weekday=6).rollforward(max_date).strftime("%m%d%Y")
    
    df_aggregated = df_aggregated[["Employee ID", "Employee Name", "Date", "Hours", "Weekend"]]

    return df_aggregated