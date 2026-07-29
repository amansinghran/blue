import pandas as pd
from datetime import datetime

def CSFgenerate_tei_output(df_customer, query_file):

    df_query = pd.read_excel(query_file, header=1, dtype=str)
    
    df_customer['Employee ID'] = df_customer['Employee ID'].astype(str).str.split('.').str[0].str.strip()
    
    query_id_col = df_query.columns[0]
    df_query[query_id_col] = df_query[query_id_col].astype(str).str.split('.').str[0].str.strip()

    df_query_unique = df_query.drop_duplicates(subset=[query_id_col], keep='first')

    df_merged = pd.merge(
        df_customer,
        df_query_unique, 
        left_on='Employee ID', 
        right_on=query_id_col, 
        how='left',
        indicator=True
    )

    error_mask = df_merged['_merge'] == 'left_only'
    df_errors = df_merged.loc[error_mask, ['Employee ID', 'Employee Name', 'Date', 'Hours', 'Weekend']].copy()

    df_clean = df_merged[df_merged['_merge'] == 'both'].copy()

    def process_to_tei(df_input):
        if df_input.empty:
            return pd.DataFrame()
        tei_data = {
            "BRANCH_NUMBER": df_input["Unit"].astype(int),
            "PROCESS_DATE": datetime.now().strftime("%m%d%y"),
            "PROCESS_TIME": datetime.now().strftime("%H%M%S"),
            "CUSTOMER_CODE": df_input["Customer"].astype(int),
            "TYPE4": "Type4",
            "EMPLOYEE_IDENTIFIER": df_input["ID"].astype(str).str.split('.').str[0].str.zfill(11),
            "ORDER_IDENTIFIER": df_input["Order Id"].astype(int),
            "DAY_DATE": pd.to_datetime(df_input['Date']).dt.strftime('%d%m%Y'),
            "HOURS_DAY": (df_input['Hours'] * 100).round().astype(int),
            "EMPLOYEE_NAME": df_input['Employee Name'],
            "PAY_RATE": 0, "BILL_RATE": 0, "PAY_RATE_OT": 0,
            "BILL_RATE_OT": 0, "PAY_RATE_DT": 0, "BILL_RATE_DT": 0,
            "TIME_RPTG_CD": "", "EARNING_DEDUCTION": "",
            "FLAT_AMOUNT": 0, "MARKUP_PCT": 0, "OTH_EARN_DESCR": "",
            "WEEK_END_DATE": df_input['Weekend']
        }
        return pd.DataFrame(tei_data)

    df_tei = process_to_tei(df_clean)

    return df_tei, df_errors
