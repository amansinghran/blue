import streamlit as st
import pandas as pd
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
        "FSL - FLEX - Salt Lake City, UT - Spherion",
        "IAP - International Auto Processing, Inc",
        "MED - Medtronics",
        "MEI - MEI Corporation",
        "NSY - Nasoya Foods USA LLC",
        "PPI - Papa",
        "SCK - Saddle Creek",
        "SAS - Samsung",
        "SCS - Schutz Container Systems, Inc",
        "SWB - Smith & Wesson Brands, Inc",
        "YKK - YKK USA, Inc"]

    full_selection = st.selectbox("Select Customer", options=customer_options)
    selected_customer = full_selection.split("-")[0].strip().upper()

    source_file = None
    source_file_1 = None
    source_file_2 = None

    if selected_customer == "SCK":
        source_file_1 = st.file_uploader("Source File 1", type=["xls", "xlsx", "csv"], key="src1")
        source_file_2 = st.file_uploader("Source File 2", type=["xls", "xlsx", "csv"], key="src2")
        source_files_ready = source_file_1 is not None and source_file_2 is not None
    else:
        source_file = st.file_uploader("Source File", type=["xls", "xlsx", "csv"], key="src_single")
        source_files_ready = source_file is not None

    query_file = st.file_uploader("Query File", type=["xls", "xlsx", "csv"])

    if 'out' not in st.session_state:
        st.session_state.out = None

    btn_left, btn_center, btn_right = st.columns([1, 1, 1])

    with btn_center:
        submit_clicked = st.button('Submit', use_container_width=True)

    if submit_clicked and source_files_ready and query_file:
        try:
            customer_module = importlib.import_module(f"Customers.{selected_customer}")
            customer_parse_func = getattr(customer_module, selected_customer)
        except ModuleNotFoundError:
            st.error(f"Could not find the module for {selected_customer}. Check your file structure.")
            st.stop()
        except AttributeError:
            st.error(f"Module {selected_customer} found, but function '{selected_customer}' is missing inside it.")
            st.stop()

        CUSTOM_TEI_CUSTOMERS = {"FSL", "LPC"}

        df_parsed = pd.DataFrame()

        # Parse source files based on customer needs
        if selected_customer == "SCK":
            if source_file_1 is not None and source_file_2 is not None:
                df_parsed = customer_parse_func(source_file_1, source_file_2)
        else:
            if source_file is not None:
                df_parsed = customer_parse_func(source_file)

        # Generate TEI output
        if selected_customer in CUSTOM_TEI_CUSTOMERS:
            tei_generator = getattr(customer_module, "generate_tei_output")
            res = tei_generator(df_parsed, query_file)
        else:
            res = CSFgenerate_tei_output(df_parsed, query_file)

        if isinstance(res, (tuple, list)):
            df_tei = res[0]
            df_err = res[1] if len(res) > 1 else pd.DataFrame()
        else:
            df_tei = res
            df_err = pd.DataFrame()

        # Generate Time & Labor Form if available
        tl_form_bytes = None
        if hasattr(customer_module, "TimeAndLaborForm"):
            tl_func = getattr(customer_module, "TimeAndLaborForm")
            tl_form_buffer = tl_func(df_parsed, query_file)
            if tl_form_buffer:
                tl_form_bytes = tl_form_buffer.getvalue()

        ts = datetime.now().strftime("%m%d%y_%H%M%S")

        if selected_customer == "MED":
            names = [
                f"RAN_{selected_customer}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                f"RAN_{selected_customer}_{datetime.now().strftime('%Y%m%d_%H%M')}_Error.csv",
                f"RAN_{selected_customer}_Time_and_Labor_{datetime.now().strftime('%m.%d')}.xlsx"]
        else:
            names = [
                f"TC_{selected_customer}_{ts}.csv", 
                f"TC_{selected_customer}_{ts}_Error.csv",
                f"{selected_customer}_Time_&_Labor_Form_{datetime.now().strftime('%m.%d')}.xlsx"]

        st.session_state.out = {
            "tei": df_tei.to_csv(index=False).encode('utf-8'),  # type: ignore
            "err": df_err.to_csv(index=False).encode('utf-8') if not df_err.empty else None,
            "tl_form": tl_form_bytes,
            "names": names}
        
        st.success(f"Files available to download for {full_selection}!")

    if st.session_state.out:
        if st.session_state.out.get("tl_form"):
            col1, col2, col3 = st.columns(3)
        else:
            col1, col2 = st.columns(2)
            col3 = None

        col1.download_button("📥 Download Validated CSV", st.session_state.out["tei"], st.session_state.out["names"][0], "text/csv")
        
        if st.session_state.out["err"]:
            col2.download_button("⚠️ Download Error CSV", st.session_state.out["err"], st.session_state.out["names"][1], "text/csv")
        else:
            col2.info("No errors found.")

        # Display T&L Form download button if available
        if col3 and st.session_state.out.get("tl_form"):
            col3.download_button(
                "📋 Download Time & Labor Form",
                st.session_state.out["tl_form"],
                st.session_state.out["names"][2],
                "application/vnd.openpyxlformat-officedocument.spreadsheetml.sheet")