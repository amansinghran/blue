import pandas as pd

def ADR(uploaded_file):

    required_columns = ["ID", "Name", "Date", "Totaled Amount"]

    df_raw = pd.read_excel(uploaded_file, header=None)
    header_idx = df_raw[df_raw.isin([required_columns[0]]).any(axis=1)].index[0]

    df = pd.read_excel(uploaded_file, header=header_idx, usecols=required_columns)

    df = df.rename(columns={
        "ID": "Employee ID",
        "Name": "Employee Name",
        "Totaled Amount": "Hours"})

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
