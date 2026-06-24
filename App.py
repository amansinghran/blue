import streamlit as st
from datetime import datetime
from IAP import IAP
from CreateUpload import generate_tei_output

st.set_page_config(page_title="r-Blue", layout="wide")
st.markdown("<h1 style='text-align:center;'> TEI Upload </h1>", unsafe_allow_html=True)

source_file = st.file_uploader("Source File", type=["xls", "xlsx", "csv"])
query_file = st.file_uploader("Query File", type=["xls", "xlsx", "csv"])

if 'out' not in st.session_state: st.session_state.out = None

if st.button('Submit') and source_file and query_file:
    df_tei, df_err, custname = generate_tei_output(IAP(source_file), query_file)
    ts = datetime.now().strftime("%m%d%y_%H%M%S")
    
    st.session_state.out = {
        "tei": df_tei.to_csv(index=False).encode('utf-8'),
        "err": df_err.to_csv(index=False).encode('utf-8') if not df_err.empty else None,
        "names": [f"{custname}_{ts}.csv", f"{custname}_{ts}_Error.csv"]
    }
    st.success(f"Files prepared for {custname}!")

if st.session_state.out:
    col1, col2 = st.columns(2)
    col1.download_button("📥 Download Validated CSV", st.session_state.out["tei"], st.session_state.out["names"][0], "text/csv")
    
    if st.session_state.out["err"]:
        col2.download_button("⚠️ Download Error CSV", st.session_state.out["err"], st.session_state.out["names"][1], "text/csv")
    else:
        col2.info("No errors found.")