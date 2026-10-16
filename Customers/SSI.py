import pandas as pd

def SSI(uploaded_file):
    
    df = pd.read_excel(uploaded_file, header=None)
    
    records = []
    emp_id, emp_name, date = None, None, None
    
    for _, r in df.iterrows():
        v1 = str(r.iloc[1]).strip() if len(r) > 1 and pd.notna(r.iloc[1]) else ""
        v4 = str(r.iloc[4]).strip() if len(r) > 4 and pd.notna(r.iloc[4]) else ""
        v21 = str(r.iloc[21]).strip() if len(r) > 21 and pd.notna(r.iloc[21]) else ""
    
        # Detect Employee Name & ID
        if " - " in v1 and "Date" not in v1:
            emp_name, emp_id = [x.strip() for x in v1.split(" - ")]
        elif "/" in v4:
            date = v4
    
        # Extract Hours from Column V (O/S - index 21)
        if emp_id and date and v21 and "Totals" not in str(r.iloc[12] if len(r) > 12 else ""):
            hrs = 0.0
            if ":" in v21:
                h, m = map(float, v21.split(":"))
                hrs = round(h + m / 60, 2)
            else:
                hrs = pd.to_numeric(v21, errors="coerce") or 0.0
    
            if hrs > 0:
                records.append({
                    "Employee ID": emp_id,
                    "Employee Name": emp_name,
                    "Date": pd.to_datetime(date).strftime("%m/%d/%Y"),
                    "Hours": hrs})
    
    df_aggregated = pd.DataFrame(records).groupby(["Employee ID", "Date"], as_index=False).agg(
        {"Hours": "sum", "Employee Name": "first"})
    
    max_date = pd.to_datetime(df_aggregated["Date"], format="%m/%d/%Y").max()
    df_aggregated["Weekend"] = pd.offsets.Week(weekday=6).rollforward(max_date).strftime("%m%d%Y")
    
    df_aggregated = df_aggregated[["Employee ID", "Employee Name", "Date", "Hours", "Weekend"]]

    return df_aggregated