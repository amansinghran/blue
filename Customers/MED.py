import pandas as pd

def MED(uploaded_file):
    
    df_raw = pd.read_excel(uploaded_file, header=None)
    header_idx = df_raw[df_raw.isin(["ID #"]).any(axis=1)].index[0]
    df = pd.read_excel(uploaded_file, header=header_idx)

    df["notes"] = df["First Name"].astype(str).str.strip() + " " + df["Last Name"].astype(str).str.strip()
    df = df.melt(id_vars=["ID #", "notes"], var_name="work_date", value_name="hours")

    df["hours"] = pd.to_numeric(df["hours"], errors="coerce")
    df = df.dropna(subset=["ID #", "hours"])
    df = df[(df["hours"] != 0) & (~df["work_date"].astype(str).str.contains("Total|Name", case=False, na=False))]

    df["ID #"] = df["ID #"].astype(int).astype(str).str.zfill(11)
    df["work_date"] = pd.to_datetime(df["work_date"], format="mixed")

    df = df.groupby(["ID #", "work_date"], as_index=False).agg({"hours": "sum", "notes": "first"})
    df["cum_end"] = df.groupby("ID #")["hours"].cumsum()
    df["cum_start"] = df["cum_end"] - df["hours"]

    st = df.copy().assign(work_type="ST1", hours=(df["cum_end"].clip(upper=40) - df["cum_start"].clip(upper=40)))
    ot = df.copy().assign(work_type="OT1", hours=(df["cum_end"].clip(lower=40) - df["cum_start"].clip(lower=40)))

    df_final = pd.concat([st, ot]).query("hours > 0")
    df_final["work_date"] = df_final["work_date"].dt.strftime("%m/%d/%Y")

    df_final = df_final[["ID #", "notes", "work_date", "work_type", "hours"]]
    return df_final


# CreateUpload

def generate_tei_output(df_customer, query_file):

    df_query = pd.read_excel(query_file, header=1, dtype=str)

    query_id = df_query.columns[8]
    df_customer['ID #'] = (df_customer['ID #'].astype(str).str.split('.').str[0].str.strip())
    df_query[query_id] = (df_query[query_id].astype(str).str.split('.').str[0].str.strip())

    m = pd.merge(
        df_customer,
        df_query.drop_duplicates(subset=[query_id]),
        left_on='ID #',
        right_on=query_id,
        how='left')

    df_tei = pd.DataFrame({
        'contractor_id': m.get('Description 2_y', m.get('Description 2')),
        'notes': m['notes'],
        'work_date': pd.to_datetime(m['work_date'], errors='coerce').dt.strftime('%m/%d/%Y'),
        'accounting_code:code': m.get('Description 1_y', m.get('Description 1')),
        'work_type': m['work_type'],
        'hours': m['hours'].round(2),
        'status': 'Submitted'})

    df_tei = df_tei.sort_values(by=['notes', 'work_date'], ascending=True)
    return df_tei