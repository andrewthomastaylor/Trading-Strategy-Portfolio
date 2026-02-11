import streamlit as st
from src.strategies.indicator_strategy import IndicatorStrategy

def render_strategy_editor():
    st.header("Strategy Editor")

    st.subheader("Technical Indicators & Logic")

    logic_type = st.selectbox("Strategy Logic", ["rsi_sma", "sma_cross", "custom"])

    col1, col2 = st.columns(2)

    with col1:
        rsi_period = st.number_input("RSI Period", value=14)
        rsi_oversold = st.number_input("RSI Oversold", value=30)
        rsi_overbought = st.number_input("RSI Overbought", value=70)

    with col2:
        sma_fast = st.number_input("SMA Fast Period", value=50)
        sma_slow = st.number_input("SMA Slow Period", value=200)
        ema_period = st.number_input("EMA Period", value=20)

    buy_conditions = []
    sell_conditions = []
    if logic_type == "custom":
        indicator_list = ["rsi", "sma_fast", "sma_slow", "ema", "close", "pe_ratio", "forward_pe", "dividend_yield"]

        st.subheader("Buy Conditions (ANDed)")
        num_buy = st.number_input("Number of Buy Conditions", min_value=1, max_value=5, value=1)
        for i in range(int(num_buy)):
            c1, c2, c3 = st.columns(3)
            with c1: ind = st.selectbox(f"Indicator {i+1}", indicator_list, key=f"buy_ind_{i}")
            with c2: op = st.selectbox(f"Operator {i+1}", ["<", ">", "==", "cross_above", "cross_below"], key=f"buy_op_{i}")
            with c3: val = st.number_input(f"Value {i+1}", value=30.0, key=f"buy_val_{i}")
            buy_conditions.append({"indicator": ind, "operator": op, "value": val})

        st.subheader("Sell Conditions (ANDed)")
        num_sell = st.number_input("Number of Sell Conditions", min_value=1, max_value=5, value=1)
        for i in range(int(num_sell)):
            c1, c2, c3 = st.columns(3)
            with c1: ind_s = st.selectbox(f"Indicator {i+1}", indicator_list, key=f"sell_ind_{i}")
            with c2: op_s = st.selectbox(f"Operator {i+1}", ["<", ">", "==", "cross_above", "cross_below"], key=f"sell_op_{i}")
            with c3: val_s = st.number_input(f"Value {i+1}", value=70.0, key=f"sell_val_{i}")
            sell_conditions.append({"indicator": ind_s, "operator": op_s, "value": val_s})

    if st.button("Save Strategy"):
        params = {
            'logic': logic_type,
            'rsi_period': rsi_period,
            'rsi_oversold': rsi_oversold,
            'rsi_overbought': rsi_overbought,
            'sma_fast': sma_fast,
            'sma_slow': sma_slow,
            'ema_period': ema_period,
            'buy_conditions': buy_conditions,
            'sell_conditions': sell_conditions
        }
        st.session_state['strategy_params'] = params
        st.session_state['current_strategy'] = IndicatorStrategy(params=params)
        st.success("Strategy saved!")

    if 'current_strategy' in st.session_state:
        st.info(f"Current Strategy: {st.session_state['current_strategy'].name}")
        st.json(st.session_state['strategy_params'])
