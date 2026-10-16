import pandas as pd
import datetime

def TSA(uploaded_file):

    df = pd.read_excel(uploaded_file, header=None)
    
    # Helper function to convert time/duration objects to decimal hours
    def parse_hours(val):
        if pd.isna(val) or val == "":
            return 0.0
        if isinstance(val, datetime.time):
            return round(val.hour + val.minute / 60.0, 2)
        val_str = str(val).strip()
        if ":" in val_str:
            h, m = map(float, val_str.split(":")[:2])
            return round(h + m / 60.0, 2)
        return pd.to_numeric(val, errors="coerce") or 0.0
    
    records = []
    emp_id, emp_name, date = None, None, None
    
    for _, r in df.iterrows():
        v0 = r.iloc[0] if len(r) > 0 and pd.notna(r.iloc[0]) else ""
        v2 = r.iloc[2] if len(r) > 2 and pd.notna(r.iloc[2]) else ""
        v3 = r.iloc[3] if len(r) > 3 and pd.notna(r.iloc[3]) else ""
        v4 = r.iloc[4] if len(r) > 4 and pd.notna(r.iloc[4]) else ""
    
        v0_str, v2_str = str(v0).strip(), str(v2).strip()
    
        # 1. Parse Employee Name & ID properly as strings (not lists)
        if "Name:" in v0_str:
            emp_name = v0_str.replace("Name:", "").strip()
            emp_id = v2_str.replace("ID#", "").strip()
            date = None
            continue
    
        # 2. Capture and forward-fill Date across split shifts
        if isinstance(v0, (datetime.datetime, pd.Timestamp)):
            date = v0.strftime("%m/%d/%Y")
        elif "/" in v0_str and "Weekly" not in v2_str:
            date = pd.to_datetime(v0_str, errors="coerce").strftime("%m/%d/%Y") # type: ignore
    
        # 3. Extract Hours and Action
        if emp_id and date and "Weekly" not in v2_str:
            hrs = parse_hours(v3)
            if hrs > 0:
                records.append({
                    "Employee ID": emp_id,
                    "Employee Name": emp_name,
                    "Date": date,
                    "Hours": hrs})
    
    df_aggregated = pd.DataFrame(records).groupby(["Employee ID", "Date"], as_index=False).agg(
        {"Hours": "sum", "Employee Name": "first"})
    
    max_date = pd.to_datetime(df_aggregated["Date"], format="%m/%d/%Y").max()
    df_aggregated["Weekend"] = pd.offsets.Week(weekday=6).rollforward(max_date).strftime("%m%d%Y")
    
    df_aggregated = df_aggregated[["Employee ID", "Employee Name", "Date", "Hours", "Weekend"]]

    return df_aggregated