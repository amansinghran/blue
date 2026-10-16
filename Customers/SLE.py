import pandas as pd

def SLE(uploaded_file):

    required_columns = ["Employee ID", "Employee Full Name", "Apply date", "Actual Hours"]
    
    df = pd.read_excel(uploaded_file, usecols=required_columns)
    df = df.rename(columns={"Actual Hours": "Hours"})
    
    df["Employee Name"] = df["Employee Full Name"].astype(str).str.strip("RSS - ")
    df["Employee ID"] = df["Employee ID"].astype(str)
    df["Date"] = pd.to_datetime(df["Apply date"], format="mixed", errors="coerce").dt.strftime("%m/%d/%Y")
    df = df.dropna(subset=["Date"])
    df = df[df["Hours"] != 0]
    
    df_aggregated = (
        df.groupby(["Employee ID", "Date"], as_index=False)
        .agg({"Hours": "sum", "Employee Name": "first"}))
    
    max_date = pd.to_datetime(df_aggregated["Date"], format="%m/%d/%Y").max()
    df_aggregated["Weekend"] = pd.offsets.Week(weekday=5).rollforward(max_date).strftime("%m%d%Y")
    
    df_aggregated = df_aggregated[["Employee ID", "Employee Name", "Date", "Hours", "Weekend"]]
    
    return df_aggregated