import streamlit as st
import json
from src.utils.database import Database

def render_strategy_editor(db: Database):
    st.header("Strategy Editor")

    st.subheader("Define Technical & Fundamental Logic")

    # Load existing strategies
    strategies = db.get_settings("strategies")
    strategy_list = json.loads(strategies) if strategies else {}

    with st.expander("Create New Strategy"):
        name = st.text_input("Strategy Name")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Technical Indicators")
            rsi_period = st.number_input("RSI Period", 1, 100, 14)
            sma_fast = st.number_input("SMA Fast", 1, 200, 50)
            sma_slow = st.number_input("SMA Slow", 1, 500, 200)

        with col2:
            st.markdown("### Fundamental Filters")
            min_pe = st.number_input("Min P/E Ratio", 0.0, 1000.0, 0.0)
            max_pe = st.number_input("Max P/E Ratio", 0.0, 1000.0, 50.0)
            min_roe = st.number_input("Min ROE (%)", -100.0, 100.0, 0.0)

        logic_json = st.text_area("Custom Signal Logic (Structured JSON)",
                             value='{"buy_conditions": [{"indicator": "rsi", "operator": "<", "value": 30}], "sell_conditions": [{"indicator": "rsi", "operator": ">", "value": 70}]}',
                             help="Define conditions using indicators: rsi, sma_fast, sma_slow, ema, macd, macd_signal, bb_upper, bb_lower, atr, adx")

        if st.button("Save Strategy"):
            try:
                parsed_logic = json.loads(logic_json)
                strategy_list[name] = {
                    "params": {
                        "rsi_period": rsi_period,
                        "sma_fast": sma_fast,
                        "sma_slow": sma_slow,
                        "min_pe": min_pe,
                        "max_pe": max_pe,
                        "min_roe": min_roe,
                        **parsed_logic
                    },
                    "logic": "custom"
                }
                db.save_setting("strategies", json.dumps(strategy_list))
                st.success(f"Strategy '{name}' saved!")
            except json.JSONDecodeError:
                st.error("Invalid JSON logic. Please check your syntax.")

    st.subheader("Existing Strategies")
    for s_name, s_data in strategy_list.items():
        st.write(f"**{s_name}**")
        st.json(s_data)
        if st.button(f"Delete {s_name}", key=f"del_{s_name}"):
            del strategy_list[s_name]
            db.save_setting("strategies", json.dumps(strategy_list))
            st.rerun()
