import pandas as pd

def SCK(uploaded_file):
    
    required_columns = ["Employee ID", "Last Name", "First Name", "Apply Date", "TTime"]

    df_raw = pd.read_excel(uploaded_file, header=None)
    header_idx = df_raw[df_raw.isin([required_columns[0]]).any(axis=1)].index[0]
    df = pd.read_excel(uploaded_file, usecols=required_columns, header=header_idx)
    
    df = df[required_columns].rename(columns={"Apply Date": "Date", "TTime": "Hours"})
    
    df["Employee Name"] = df["Last Name"].astype(str).str.strip() + ", " + df["First Name"].astype(str).str.strip()
    df = df.dropna(subset=["Employee ID", "Date", "Hours"])
    df = df[df["Hours"] != 0]
    
    df["Employee ID"] = df["Employee ID"].astype(int)
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%d/%m/%Y")
    
    df_aggregated = df.groupby(["Employee ID", "Date"], as_index=False).agg(
        {"Hours": "sum", "Employee Name": "first"}
    )
    
    max_date = pd.to_datetime(df_aggregated["Date"], format="%d/%m/%Y").max()
    df_aggregated["Weekend"] = pd.offsets.Week(weekday=6).rollforward(max_date).strftime("%m%d%Y")
    
    df_aggregated = df_aggregated[["Employee ID", "Employee Name", "Date", "Hours", "Weekend"]]

    return df_aggregated