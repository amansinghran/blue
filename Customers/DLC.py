import pandas as pd

def DLC(uploaded_file):
    
    df = pd.read_excel(uploaded_file)
    id_cols = ["Employee ID", "Employee Name"]
    date_cols = [col for col in df.columns if "daily hours" in str(col).lower()]
    
    # 2. Unpivot (melt) data from horizontal to vertical format
    df = df.melt(
        id_vars=id_cols, 
        value_vars=date_cols, 
        var_name="Date", 
        value_name="Hours")
    
    # 3. Remove "Daily Hours" text from the Date column & trim spaces
    df["Date"] = (
        df["Date"].astype(str)
        .str.replace(r"(?i)daily\s*hours", "", regex=True)  # Case-insensitive removal
        .str.strip())
    
    # 4. Convert Date column to standard Date format (MM/DD/YYYY)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.strftime("%m/%d/%Y")
    
    # 5. Filter out zero or empty hours
    df["Hours"] = pd.to_numeric(df["Hours"], errors="coerce").fillna(0)
    df = df[df["Hours"] != 0].reset_index(drop=True)
    
    df_aggregated = (
        df.groupby(["Employee ID", "Date"], as_index=False)
        .agg({"Hours": "sum", "Employee Name": "first"}))
    
    max_date = pd.to_datetime(df_aggregated["Date"], format="%m/%d/%Y").max()
    df_aggregated["Weekend"] = pd.offsets.Week(weekday=6).rollforward(max_date).strftime("%m%d%Y")
    
    df_aggregated = df_aggregated[["Employee ID", "Employee Name", "Date", "Hours", "Weekend"]]
    
    return df_aggregated