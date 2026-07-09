import pandas as pd
from datetime import datetime

def generate_tei_output(df_iap, query_file):

    df_query = pd.read_excel(query_file)
    
    Custname = query_file.name[:3].upper()
    
    df_merged = pd.merge(
        df_iap, 
        df_query, 
        left_on='Employee ID', 
        right_on=df_query.columns[0], 
        how='left',
        indicator=True
    )

    error_mask = df_merged['_merge'] == 'left_only'
    df_errors = df_iap[error_mask][['Employee ID', 'Employee Name', 'Date', 'Hours']].copy()

    df_clean = df_merged[df_merged['_merge'] == 'both'].copy()

    def process_to_tei(df_input):
        if df_input.empty:
            return pd.DataFrame()
            
        temp_dates = pd.to_datetime(df_input['Date'], dayfirst=True)
        days_to_add = (6 - temp_dates.dt.weekday) % 7
        week_end_dates = temp_dates + pd.to_timedelta(days_to_add, unit='D')

        tei_data = {
            "BRANCH_NUMBER": df_input.iloc[:, 5],
            "PROCESS_DATE": datetime.now().strftime("%m%d%y"),
            "PROCESS_TIME": datetime.now().strftime("%H%M%S"),
            "CUSTOMER_CODE": df_input.iloc[:, 10],
            "TYPE4": "Type4",
            "EMPLOYEE_IDENTIFIER": df_input.iloc[:, 7],
            "ORDER_IDENTIFIER": df_input.iloc[:, 6],
            "DAY_DATE": temp_dates.dt.strftime('%m%d%Y'),
            "HOURS_DAY": (df_input['Hours'] * 100).round().astype(int),
            "EMPLOYEE_NAME": df_input['Employee Name'],
            "PAY_RATE": 0, "BILL_RATE": 0, "PAY_RATE_OT": 0,
            "BILL_RATE_OT": 0, "PAY_RATE_DT": 0, "BILL_RATE_DT": 0,
            "TIME_RPTG_CD": "", "EARNING_DEDUCTION": "",
            "FLAT_AMOUNT": 0, "MARKUP_PCT": 0, "OTH_EARN_DESCR": "",
            "WEEK_END_DATE": week_end_dates.dt.strftime('%m%d%Y')
        }
        return pd.DataFrame(tei_data)

    df_tei = process_to_tei(df_clean)

    return df_tei, df_errors, Custname