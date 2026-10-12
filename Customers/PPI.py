import pandas as pd

def PPI(uploaded_file):
    # 1
    required_columns = ["agency id", "Employee Name", "Date", "Clock In", "Clock Out"]

    df = pd.read_excel(uploaded_file, usecols=required_columns)

    df = df.rename(columns={"agency id": "Employee ID"})
    
    start_td = pd.to_timedelta(df["Clock In"].astype(str))
    end_td = pd.to_timedelta(df["Clock Out"].astype(str))
    df["Hours"] = (((end_td - start_td).dt.total_seconds().mod(86400)) / 3600).round(2)
    
    df = df.dropna(subset=["Date", "Hours"])
    df = df[df["Hours"] != 0]
    
    df["Employee ID"] = df["Employee ID"].astype(int)
    df["Date"] = pd.to_datetime(df["Date"], format="mixed").dt.strftime("%m/%d/%Y")
    
    df_aggregated = df.groupby(["Employee ID", "Date"], as_index=False).agg(
        {"Hours": "sum", "Employee Name": "first"})
    
    max_date = pd.to_datetime(df_aggregated["Date"], format="%m/%d/%Y").max()
    df_aggregated["Weekend"] = pd.offsets.Week(weekday=6).rollforward(max_date).strftime("%m%d%Y")
    
    df_aggregated = df_aggregated[["Employee ID", "Employee Name", "Date", "Hours", "Weekend"]]

    return df_aggregated