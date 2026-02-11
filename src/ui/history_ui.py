import streamlit as st
import pandas as pd

def render_history_ui():
    st.header("Trade History & Logic Trace")

    db = st.session_state.get('db')
    if db:
        history = db.get_trades()
    elif 'monitor' in st.session_state:
        history = st.session_state['monitor'].trade_history
    else:
        st.info("No monitor history found.")
        return

    if not history:
        st.info("No trades executed yet.")
    else:
        df_history = pd.DataFrame(history)
        st.subheader("Recent Trade Executions")
        st.dataframe(df_history.sort_values(by="timestamp", ascending=False))

        st.divider()
        st.subheader("Logic Trace Details")
        for trade in history: # Already sorted by timestamp desc in DB query
            ts = trade['timestamp']
            if isinstance(ts, str):
                ts_str = ts
            else:
                ts_str = ts.strftime('%Y-%m-%d %H:%M:%S')

            with st.expander(f"{ts_str} - {trade['symbol']} {trade['side']}"):
                st.write(f"**Status:** {trade['status']}")
                st.write(f"**Reason (Trigger):** {trade['reason']}")
                st.write("---")
                st.write("Current technical conditions at time of trade were evaluated by the active strategy.")
