import streamlit as st
import pandas as pd

def render_history_ui():
    st.header("Trade History & Logic Trace")

    if 'monitor' not in st.session_state:
        st.info("No active monitor history found. Start monitoring to see trade logs.")
        return

    history = st.session_state['monitor'].trade_history

    if not history:
        st.info("No trades executed yet.")
    else:
        df_history = pd.DataFrame(history)
        st.subheader("Recent Trade Executions")
        st.dataframe(df_history.sort_values(by="timestamp", ascending=False))

        st.divider()
        st.subheader("Logic Trace Details")
        for trade in reversed(history):
            with st.expander(f"{trade['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} - {trade['symbol']} {trade['side']}"):
                st.write(f"**Status:** {trade['status']}")
                st.write(f"**Reason (Trigger):** {trade['reason']}")
                st.write("---")
                st.write("Current technical conditions at time of trade were evaluated by the active strategy.")
