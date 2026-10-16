import pandas as pd

def TWS(uploaded_file_1, uploaded_file_2=None):
    
    required_columns = ["Position ID", "First Name", "Last Name", "In Date", "Hours"]
    processed_dfs = []

    for file in filter(None, [uploaded_file_1, uploaded_file_2]):
        df_raw = pd.read_excel(file, header=None)
        matches = df_raw[df_raw.isin([required_columns[0]]).any(axis=1)].index
        
        if not matches.empty:
            if hasattr(file, "seek"): 
                file.seek(0)
            processed_dfs.append(pd.read_excel(file, header=matches[0], usecols=required_columns))

    df = pd.concat(processed_dfs, ignore_index=True) if processed_dfs else pd.DataFrame(columns=required_columns)

    df = df.rename(columns={"Position ID": "Employee ID"})
    
    df["Employee Name"] = df["Last Name"].astype(str).str.strip() + ", " + df["First Name"].astype(str).str.strip()
    df["Employee ID"] = df["Employee ID"].astype(str)
    df["Date"] = pd.to_datetime(df["In Date"], format="mixed", errors="coerce").dt.strftime("%m/%d/%Y")
    df = df.dropna(subset=["Date"])
    df = df[df["Hours"] != 0]
    
    df_aggregated = (
        df.groupby(["Employee ID", "Date"], as_index=False)
        .agg({"Hours": "sum", "Employee Name": "first"}))
    
    max_date = pd.to_datetime(df_aggregated["Date"], format="%m/%d/%Y").max()
    df_aggregated["Weekend"] = pd.offsets.Week(weekday=5).rollforward(max_date).strftime("%m%d%Y")
    
    df_aggregated = df_aggregated[["Employee ID", "Employee Name", "Date", "Hours", "Weekend"]]
    
    return df_aggregated