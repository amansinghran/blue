import pandas as pd

def BTD(uploaded_file):

    required_columns = ["Employee Number", "Employee Name", "Shift Date", "Paid Hours"]

    all_sheets = pd.read_excel(uploaded_file, sheet_name=None, nrows=0)

    target_sheet = None
    for sheet_name, sheet_df in all_sheets.items():
        if set(required_columns).issubset(sheet_df.columns):
            target_sheet = sheet_name
            break

    if target_sheet is None:
        raise ValueError("Could not find a sheet with all required columns.")

    df = pd.read_excel(uploaded_file, sheet_name=target_sheet, usecols=required_columns)

    
    df = df.rename(columns={
        "Employee Number": "Employee ID",
        "Shift Date": "Date",
        "Paid Hours": "Hours"})
    
    df = df.dropna(subset=["Date"])
    df = df[df["Hours"] != 0]
    df["Employee ID"] = df["Employee ID"].astype(int)
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%m/%d/%Y")
    
    df_aggregated = (df.groupby(["Employee ID", "Date"], as_index=False)
        .agg({"Hours": "sum", "Employee Name": "first"}))
    
    max_date = pd.to_datetime(df_aggregated["Date"], format="%m/%d/%Y").max()
    df_aggregated["Weekend"] = pd.offsets.Week(weekday=5).rollforward(max_date).strftime("%m%d%Y")
    
    df_aggregated = df_aggregated[["Employee ID", "Employee Name", "Date", "Hours", "Weekend"]]
    return df_aggregated
