import streamlit as st
from src.api.alpaca_wrapper import AlpacaClient
from src.monitoring.monitor import LiveMonitor
from src.notifications.email_service import EmailService

def render_monitor_ui():
    st.header("Live Monitoring")

    if 'alpaca_api_key' not in st.session_state:
        st.warning("Please configure Alpaca API keys in Settings.")
        return

    col1, col2 = st.columns(2)

    client = AlpacaClient(
        st.session_state.get('alpaca_api_key'),
        st.session_state.get('alpaca_secret_key'),
        paper=st.session_state.get('paper_mode', True)
    )

    if not client.trading_client:
        st.error("Alpaca Trading Client not initialized. Please check your API keys in Settings.")
        return

    with col1:
        reopt_enabled = st.toggle("Enable Dynamic Re-optimization", value=False)
        reopt_ticks = st.number_input("Re-optimize every N ticks", min_value=10, max_value=1000, value=100) if reopt_enabled else 0

        if st.button("Start Monitoring"):
            if 'monitor' not in st.session_state or not st.session_state['monitor'].running:
                email_svc = EmailService(
                    sender_email=st.session_state.get('email_sender'),
                    app_password=st.session_state.get('email_password')
                )
                monitor = LiveMonitor(client, email_svc, db=st.session_state.get('db'))

                if 'current_strategy' in st.session_state:
                    monitor.add_strategy(st.session_state['current_strategy'], st.session_state.get('symbols', ["AAPL"]))
                    monitor.reoptimize_interval = reopt_ticks
                    monitor.start(interval_minutes=st.session_state.get('interval', 1))
                    st.session_state['monitor'] = monitor
                    st.success("Monitoring started!")
                else:
                    st.error("Please define a strategy first.")
            else:
                st.info("Monitor is already running.")

    with col2:
        if st.button("Stop Monitoring"):
            if 'monitor' in st.session_state and st.session_state['monitor'].running:
                st.session_state['monitor'].stop()
                st.warning("Monitoring stopped.")
            else:
                st.info("Monitor is not running.")

    if 'monitor' in st.session_state and st.session_state['monitor'].running:
        monitor = st.session_state['monitor']
        st.status("Monitoring in progress...")
        st.write(f"Tracking symbols: {', '.join(monitor.symbols)}")

        st.subheader("Real-time Logic Trace")
        if monitor.latest_status:
            status_list = []
            for sym, stat in monitor.latest_status.items():
                row = {"Symbol": sym, "Last Signal": stat['signal'], "Timestamp": stat['timestamp']}
                # Add some key indicators to the table
                inds = stat['indicators']
                for k in ['rsi', 'sma_fast', 'sma_slow', 'close']:
                    if k in inds:
                        row[k.upper()] = f"{inds[k]:.2f}"
                status_list.append(row)
            st.table(pd.DataFrame(status_list))
        else:
            st.info("Waiting for first tick results...")

    st.divider()

    st.subheader("Current Portfolio")
    try:
        positions = client.get_positions()
        if positions:
            st.dataframe([p.__dict__ for p in positions])
        else:
            st.info("No open positions.")

        st.subheader("Recent Orders")
        orders = client.get_orders(status='all')
        if orders:
            st.dataframe([o.__dict__ for o in orders[:10]]) # Show last 10
        else:
            st.info("No recent orders.")
    except Exception as e:
        st.error(f"Error fetching portfolio data: {e}")
