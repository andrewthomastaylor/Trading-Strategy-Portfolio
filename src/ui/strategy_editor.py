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
        st.subheader("Buy Conditions")
        c1, c2, c3 = st.columns(3)
        with c1: ind = st.selectbox("Indicator", ["rsi", "sma_fast", "sma_slow", "ema", "close"], key="buy_ind")
        with c2: op = st.selectbox("Operator", ["<", ">", "==", "cross_above", "cross_below"], key="buy_op")
        with c3: val = st.number_input("Value", value=30.0, key="buy_val")
        buy_conditions.append({"indicator": ind, "operator": op, "value": val})

        st.subheader("Sell Conditions")
        c1, c2, c3 = st.columns(3)
        with c1: ind_s = st.selectbox("Indicator", ["rsi", "sma_fast", "sma_slow", "ema", "close"], key="sell_ind")
        with c2: op_s = st.selectbox("Operator", ["<", ">", "==", "cross_above", "cross_below"], key="sell_op")
        with c3: val_s = st.number_input("Value", value=70.0, key="sell_val")
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
