import streamlit as st
from datetime import datetime
import importlib
from CSFCreateUpload import CSFgenerate_tei_output

st.set_page_config(page_title="r-Blue", layout="wide")
st.markdown("<h1 style='text-align:center;'> TEI Upload </h1>", unsafe_allow_html=True)

left_co, cent_co, right_co = st.columns([1, 2, 1])

with cent_co:

    customer_options = [
        "ADL - Adler Pelzer",
        "ARN - Ariens Company",
        "BTD - Barrett Distribution",
        "DHL - DHL_Spherion",
        "IAP - International Auto Processing, Inc",
        "MEI - MEI Corporation",
        "NSY - Nasoya Foods USA LLC",
        "PPI - Papa",
        "SCK - Saddle Creek",
        "SAS - Samsung",
        "SCS - Schutz Container Systems, Inc",
        "SWB - Smith & Wesson Brands, Inc",
        "YKK - YKK USA, Inc",
        ]

    full_selection = st.selectbox("Select Customer", options=customer_options)
    selected_customer = full_selection[:3].upper()

    source_file = st.file_uploader("Source File", type=["xls", "xlsx", "csv"])
    query_file = st.file_uploader("Query File", type=["xls", "xlsx", "csv"])

    if 'out' not in st.session_state: 
        st.session_state.out = None

    # Creating 3 columns inside cent_co to center the button
    btn_left, btn_center, btn_right = st.columns([1, 1, 1])
    
    with btn_center:
        submit_clicked = st.button('Submit', use_container_width=True)
    # ------------------------------

    if submit_clicked and source_file and query_file:
        
        try:
            customer_module = importlib.import_module(f"Customers.{selected_customer}")
            customer_parse_func = getattr(customer_module, selected_customer)
        except ModuleNotFoundError:
            st.error(f"Could not find the module for {selected_customer}. Check your file structure.")
            st.stop()
        except AttributeError:
            st.error(f"Module {selected_customer} found, but function '{selected_customer}' is missing inside it.")
            st.stop()

        df_tei, df_err = CSFgenerate_tei_output(customer_parse_func(source_file), query_file)
        ts = datetime.now().strftime("%m%d%y_%H%M%S")
        
        st.session_state.out = {
            "tei": df_tei.to_csv(index=False).encode('utf-8'),
            "err": df_err.to_csv(index=False).encode('utf-8') if not df_err.empty else None,
            "names": [f"TC_{selected_customer}_{ts}.csv", f"TC_{selected_customer}_{ts}_Error.csv"]
        }
        st.success(f"Files available to download for {full_selection}!")

    if st.session_state.out:
        col1, col2 = st.columns(2)
        col1.download_button("📥 Download Validated CSV", st.session_state.out["tei"], st.session_state.out["names"][0], "text/csv")
        
        if st.session_state.out["err"]:
            col2.download_button("⚠️ Download Error CSV", st.session_state.out["err"], st.session_state.out["names"][1], "text/csv")
        else:
            col2.info("No errors found.")
