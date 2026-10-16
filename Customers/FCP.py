import pandas as pd

def FCP(uploaded_file):

    df_raw = pd.read_excel(uploaded_file, header=None)
    
    # 1. Forward-fill dates and map 'Hours' sub-columns
    date_row, sub_row = df_raw.iloc[1], df_raw.iloc[3]
    col_map = {}
    curr_date = None
    
    for c in range(len(df_raw.columns)):
        if pd.notna(date_row[c]) and str(date_row[c]).strip() != "":
            curr_date = pd.to_datetime(date_row[c], errors="coerce")
        if str(sub_row[c]).strip().lower() == "hours" and pd.notnull(curr_date):
            col_map[c] = curr_date.strftime("%m/%d/%Y")
    
    # 2. Extract employee records
    records = []
    for _, row in df_raw.iloc[4:].iterrows():
        emp_name, emp_id = str(row[0]).strip(), str(row[1]).strip()
        if emp_id and emp_id.lower() not in ["nan", "none"]:
            for c, dt in col_map.items():
                hrs = pd.to_numeric(row[c], errors="coerce")
                if hrs > 0:
                    records.append({"Employee Name": emp_name, "Employee ID": emp_id, "Date": dt, "Hours": hrs})
    
    df = pd.DataFrame(records)
    
    df_aggregated = (
        df.groupby(["Employee ID", "Date"], as_index=False)
        .agg({"Hours": "sum", "Employee Name": "first"}))
    
    max_date = pd.to_datetime(df_aggregated["Date"], format="%m/%d/%Y").max()
    df_aggregated["Weekend"] = pd.offsets.Week(weekday=5).rollforward(max_date).strftime("%m%d%Y")
    
    df_aggregated = df_aggregated[["Employee ID", "Employee Name", "Date", "Hours", "Weekend"]]

    return df_aggregated