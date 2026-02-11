import streamlit as st
import pandas as pd
from src.utils.database import Database

def render_dashboard(db: Database):
    st.header("Live Monitoring Dashboard")

    col1, col2, col3 = st.columns(3)
    col1.metric("Status", "Running" if st.session_state.get('monitoring_active') else "Stopped")

    trades = db.get_trades(limit=10)
    st.subheader("Recent Signals & Trades")
    if trades:
        df = pd.DataFrame(trades, columns=['ID', 'Timestamp', 'Symbol', 'Side', 'Qty', 'Price', 'Reason'])
        st.dataframe(df.sort_values('Timestamp', ascending=False), use_container_width=True)
    else:
        st.info("No trades logged yet.")

    st.subheader("Logic Trace")
    st.write("Real-time signal breakdown will appear here during active monitoring.")
