import pandas as pd

def IPC(uploaded_file):
    
    required_columns = ["Badge", "Firstname", "Lastname", "InPunchTime", "OutPunchTime", "EarnHours"]
    
    df = pd.read_excel(uploaded_file, usecols=required_columns)
    df = df.rename(columns={"Badge": "Employee ID", "EarnHours": "Hours"})
    
    df["Employee Name"] = df["Lastname"].astype(str).str.strip() + ", " + df["Firstname"].astype(str).str.strip()
    df["Employee ID"] = df["Employee ID"].astype(str)
    
    # Filter out 0 hours first
    df = df[df["Hours"] != 0].copy()
    
    # Parse timestamps
    df["InPunchTime"] = pd.to_datetime(df["InPunchTime"], format="mixed", errors="coerce")
    df["OutPunchTime"] = pd.to_datetime(df["OutPunchTime"], format="mixed", errors="coerce")
    df = df.dropna(subset=["InPunchTime"]).sort_values(by=["Employee ID", "InPunchTime"]).reset_index(drop=True)
    
    # Identify shifts: a gap > 4 hours from previous out-punch indicates a new shift
    prev_out = df.groupby("Employee ID")["OutPunchTime"].shift(1)
    is_new_shift = (df["InPunchTime"] - prev_out > pd.Timedelta(hours=4)) | prev_out.isna()
    df["Shift_ID"] = is_new_shift.cumsum()
    
    # Assign the shift's starting date to all punches in that shift (formatted as M/D/YYYY without leading zeros)
    shift_start_dt = df.groupby("Shift_ID")["InPunchTime"].transform("first")
    df["Date"] = shift_start_dt.apply(lambda d: f"{d.month}/{d.day}/{d.year}")
    df["Hours"] = pd.to_numeric(df["Hours"], errors="coerce").fillna(0)
    df = df[df["Hours"] != 0]
    
    df_aggregated = (
        df.groupby(["Employee ID", "Date"], as_index=False)
        .agg({"Hours": "sum", "Employee Name": "first"}))
    
    max_date = pd.to_datetime(df_aggregated["Date"], format="%m/%d/%Y").max()
    df_aggregated["Weekend"] = pd.offsets.Week(weekday=5).rollforward(max_date).strftime("%m%d%Y")
    
    df_aggregated = df_aggregated[["Employee ID", "Employee Name", "Date", "Hours", "Weekend"]]
    
    return df_aggregated