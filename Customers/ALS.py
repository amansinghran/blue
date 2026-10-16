import pandas as pd

def ALS(uploaded_file):

    # 1. Read all sheets into memory
    all_sheets = pd.read_excel(uploaded_file, header=None, sheet_name=None)

    # 2. Find target sheet & header index, then slice header directly
    s_name, idx = next((s, df[df[0].astype(str).str.strip().eq("Name")].index[0]) 
                    for s, df in all_sheets.items()
                    if (df[0].astype(str).str.strip() == "Name").any())

    df = pd.read_excel(uploaded_file, sheet_name=s_name, header=idx)

    df = df.rename(columns={
        "Payroll ID": "Employee ID",
        "Name": "Employee Name"})

    # Clean Employee ID
    df["Employee ID"] = (df["Employee ID"].astype(str).str.replace(r"[\xa0\t]","",regex=True).str.strip())

    # Calculate Hours based on 'Role' ending with 'MO'
    df["Total paid hours"] = pd.to_numeric(df["Total paid hours"], errors="coerce").fillna(0)
    df["Unpaid breaks"] = pd.to_numeric(df["Unpaid breaks"], errors="coerce").fillna(0)

    is_mo = df["Role"].astype(str).str.strip().str.endswith("MO")
    df["Hours"] = (df["Total paid hours"] + df["Unpaid breaks"].where(is_mo, 0)).round(2)

    # Filter non-zero hours and reformat date
    df = df[df["Hours"] != 0].copy()
    df["Clock out date"] = pd.to_datetime(df["Clock out date"].str.strip(), format="%B %d %Y", errors="coerce")
    df = df.dropna(subset=["Clock out date"])
    df["Date"] = df["Clock out date"].dt.strftime("%m/%d/%Y")

    df_aggregated = (
        df.groupby(["Employee ID", "Date"], as_index=False)
        .agg({"Hours": "sum", "Employee Name": "first"}))

    max_date = pd.to_datetime(df_aggregated["Date"], format="%m/%d/%Y").max()
    df_aggregated["Weekend"] = pd.offsets.Week(weekday=6).rollforward(max_date).strftime("%m%d%Y")

    df_aggregated = df_aggregated[["Employee ID", "Employee Name", "Date", "Hours", "Weekend"]]

    return df_aggregated