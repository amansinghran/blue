import streamlit as st
from datetime import datetime
import importlib
from CreateUpload import generate_tei_output

st.set_page_config(page_title="r-Blue", layout="wide")
st.markdown("<h1 style='text-align:center;'> TEI Upload </h1>", unsafe_allow_html=True)

left_co, cent_co, right_co = st.columns([1, 2, 1])

with cent_co:

    customer_options = ["IAP", "CustomerAA", "CustomerBB"] # Add all your customer names here
    selected_customer = st.selectbox("Select Customer", options=customer_options)

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
            CustomerClass = getattr(customer_module, selected_customer)
        except ModuleNotFoundError:
            st.error(f"Could not find the module for {selected_customer}. Check your file structure.")
            st.stop()

        df_tei, df_err, custname = generate_tei_output(CustomerClass(source_file), query_file)
        ts = datetime.now().strftime("%m%d%y_%H%M%S")
        
        st.session_state.out = {
            "tei": df_tei.to_csv(index=False).encode('utf-8'),
            "err": df_err.to_csv(index=False).encode('utf-8') if not df_err.empty else None,
            "names": [f"TC_{custname}_{ts}.csv", f"TC_{custname}_{ts}_Error.csv"]
        }
        st.success(f"Files prepared for {custname}!")

    if st.session_state.out:
        col1, col2 = st.columns(2)
        col1.download_button("📥 Download Validated CSV", st.session_state.out["tei"], st.session_state.out["names"][0], "text/csv")
        
        if st.session_state.out["err"]:
            col2.download_button("⚠️ Download Error CSV", st.session_state.out["err"], st.session_state.out["names"][1], "text/csv")
        else:
            col2.info("No errors found.")