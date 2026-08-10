import pandas as pd

def ARN(uploaded_file):

    df = pd.read_excel(uploaded_file,header=[0, 1])

    df.columns = [
        str(c2).strip() if "Unnamed:" in str(c1) else str(c1).strip() 
        for c1, c2 in df.columns]
    
    df = df.loc[:, df.columns.astype(str).str.strip() != ""]
    
    df = df.rename(columns={"Worker": "Employee Name"})
    df = df.melt(id_vars=["Employee ID", "Employee Name"], var_name="Date", value_name="Hours")
    
    df = df.dropna(subset=["Employee ID", "Hours"])
    df = df[(df["Hours"] != 0) & (~df["Date"].astype(str).str.contains("Total", case=False, na=False))]
    
    df["Employee ID"] = df["Employee ID"].astype(int)
    df["Employee Name"] = df["Employee Name"].astype(str).str.strip()
    df["Date"] = pd.to_datetime(df["Date"], format="mixed").dt.strftime("%d/%m/%Y")
    
    df_aggregated = df.groupby(["Employee ID", "Date"], as_index=False).agg(
        {"Hours": "sum", "Employee Name": "first"})
    
    max_date = pd.to_datetime(df_aggregated["Date"], format="%d/%m/%Y").max()
    df_aggregated["Weekend"] = pd.offsets.Week(weekday=6).rollforward(max_date).strftime("%m%d%Y")
    
    df_aggregated = df_aggregated[["Employee ID", "Employee Name", "Date", "Hours", "Weekend"]]

    return df_aggregated