import pandas as pd

def QEP(uploaded_file):

    df_raw = pd.read_excel(uploaded_file, header=None)
    
    records = []
    emp_id, emp_name, curr_date = None, None, None
    
    for _, row in df_raw.iterrows():
        val0 = str(row[0]).strip() if pd.notna(row[0]) else ""
        val2 = str(row[2]).strip() if pd.notna(row[2]) else ""
        val3 = str(row[3]).strip() if pd.notna(row[3]) else ""
        val4 = str(row[4]).strip() if pd.notna(row[4]) else ""
        val18 = row[18] if pd.notna(row[18]) else 0
    
        # Store Employee ID & Name header block (matches digits or non-empty ID)
        if val0 and val3 and val0 not in ["Employee Number", "Code"]:
            emp_id, emp_name = val0, val3
            curr_date = None
            continue
    
        # Forward-fill date across daily entries
        if val2 not in ["", "Date"]:
            curr_date = val2
    
        # Extract valid line items with non-zero Hours
        if curr_date and val4 not in ["", "Action"] and emp_id:
            try:
                hrs = float(val18)
                if hrs > 0:
                    records.append({
                        "Employee ID": emp_id,
                        "Employee Name": emp_name,
                        "Action": val4,
                        "Date": curr_date,
                        "Hours": hrs,})
            except (ValueError, TypeError):
                continue
    
    cols = ["Employee ID", "Employee Name", "Action", "Date", "Hours"]
    df = pd.DataFrame(records, columns=cols)
    
    # Clean & Format Date and Employee ID
    df["Employee ID"] = df["Employee ID"].astype(str)
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%m/%d/%Y")
    df["Hours"] = df["Hours"].round(2)
    df = df[df["Hours"] != 0]
    
    # Group & Aggregate including Action
    df_aggregated = (
        df.groupby(["Employee ID", "Action", "Date"], as_index=False)
        .agg({"Hours": "sum", "Employee Name": "first"}))
    
    # Calculate Weekend date (Legacy logic)
    max_date = pd.to_datetime(df_aggregated["Date"], format="%m/%d/%Y").max()
    df_aggregated["Weekend"] = pd.offsets.Week(weekday=5).rollforward(max_date).strftime("%m%d%Y")
    
    df_aggregated = df_aggregated[["Employee ID", "Employee Name", "Date", "Hours", "Weekend"]]

    return df_aggregated