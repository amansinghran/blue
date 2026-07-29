import pandas as pd

def MEI(uploaded_file):
    
    required_columns = ["BADGE #", "EMPL NAME", "TRANS DATE", "ADJ. HRS"]

    df = pd.read_excel(uploaded_file, usecols=required_columns)

    df = df.rename(columns={
        "BADGE #": "Employee ID",
        "EMPL NAME": "Employee Name",
        "TRANS DATE": "Date",
        "ADJ. HRS": "Hours"
    })
    
    df = df.dropna(subset=["Employee ID", "Date", "Hours"])
    df = df[(df["Hours"] != 0) & (~df["Date"].astype(str).str.contains("Total", case=False, na=False))]
    
    df["Employee ID"] = df["Employee ID"].astype(int)
    df["Date"] = pd.to_datetime(df["Date"], format="mixed").dt.strftime("%d/%m/%Y")
    
    df_aggregated = df.groupby(["Employee ID", "Date"], as_index=False).agg(
        {"Hours": "sum", "Employee Name": "first"}
    )
    
    max_date = pd.to_datetime(df_aggregated["Date"], format="%d/%m/%Y").max()
    df_aggregated["Weekend"] = pd.offsets.Week(weekday=6).rollforward(max_date).strftime("%m%d%Y")
    
    df_aggregated = df_aggregated[["Employee ID", "Employee Name", "Date", "Hours", "Weekend"]]

    return df_aggregated