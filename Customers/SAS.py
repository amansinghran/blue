import pandas as pd
import re

def SAS(uploaded_file):
    
    df = pd.read_excel(uploaded_file, header=None)

    data, emp_name, emp_id = [], None, None
    
    for _, row in df.iterrows():
        first_val = str(row[0]).strip()
    
        if first_val == "Employee Name":
            for val in row.dropna():
                match = re.search(r"^(.*?)\s*\((.*?)\)$", str(val).strip())
                if match:
                    emp_name, emp_id = match.group(1).strip(), int(match.group(2).strip())
                    break
            continue
    
        date_val = pd.to_datetime(row[0], errors="coerce")
        if pd.notna(date_val) and pd.notna(row[10]):
            try:
                hours = float(row[10])
                if hours != 0:
                    data.append({
                        "Employee ID": emp_id,
                        "Employee Name": emp_name,
                        "Date": date_val.strftime("%d/%m/%Y"),
                        "Hours": hours
                    })
            except ValueError:
                pass
    
    df_aggregated = pd.DataFrame(data).groupby(["Employee ID", "Date"], as_index=False).agg(
        {"Hours": "sum", "Employee Name": "first"})
    
    max_date = pd.to_datetime(df_aggregated["Date"], format="%d/%m/%Y").max()
    df_aggregated["Weekend"] = pd.offsets.Week(weekday=6).rollforward(max_date).strftime("%m%d%Y")
    df_aggregated = df_aggregated[["Employee ID", "Employee Name", "Date", "Hours", "Weekend"]]

    return df_aggregated