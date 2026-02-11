import talib
import pandas as pd
import numpy as np
from src.strategies.base_strategy import BaseStrategy

class IndicatorStrategy(BaseStrategy):
    def __init__(self, name="CustomIndicatorStrategy", params=None):
        super().__init__(name, params)
        # Default params if none provided
        if not self.params:
            self.params = {
                'rsi_period': 14,
                'rsi_oversold': 30,
                'rsi_overbought': 70,
                'sma_fast': 50,
                'sma_slow': 200,
                'logic': 'rsi_cross_under_oversold' # Example logic key
            }

    def get_indicators(self, data: pd.DataFrame):
        df = data.copy()
        close = df['close'].values

        # Calculate some common indicators
        df['rsi'] = talib.RSI(close, timeperiod=self.params.get('rsi_period', 14))
        df['sma_fast'] = talib.SMA(close, timeperiod=self.params.get('sma_fast', 50))
        df['sma_slow'] = talib.SMA(close, timeperiod=self.params.get('sma_slow', 200))
        df['ema'] = talib.EMA(close, timeperiod=self.params.get('ema_period', 20))

        macd, macdsignal, macdhist = talib.MACD(close)
        df['macd'] = macd
        df['macd_signal'] = macdsignal
        df['macd_hist'] = macdhist

        upper, middle, lower = talib.BBANDS(close)
        df['bb_upper'] = upper
        df['bb_middle'] = middle
        df['bb_lower'] = lower

        return df

    def generate_signals(self, data: pd.DataFrame, fundamentals: dict = None):
        df = self.get_indicators(data)

        # Merge fundamentals into dataframe as constant columns for condition evaluation
        if fundamentals:
            for key, val in fundamentals.items():
                if val is not None:
                    df[key] = val
                else:
                    df[key] = np.nan

        signals = pd.Series(0, index=df.index)
        self.logic_trace = []

        logic = self.params.get('logic', 'custom')

        if logic == 'rsi_sma':
            buy_mask = (df['rsi'] < self.params.get('rsi_oversold', 30)) & (df['close'] > df['sma_fast'])
            sell_mask = (df['rsi'] > self.params.get('rsi_overbought', 70))
            signals[buy_mask] = 1
            signals[sell_mask] = -1

        elif logic == 'sma_cross':
            buy_mask = (df['sma_fast'] > df['sma_slow']) & (df['sma_fast'].shift(1) <= df['sma_slow'].shift(1))
            sell_mask = (df['sma_fast'] < df['sma_slow']) & (df['sma_fast'].shift(1) >= df['sma_slow'].shift(1))
            signals[buy_mask] = 1
            signals[sell_mask] = -1

        elif logic == 'custom':
            # Structured logic instead of eval
            buy_conditions = self.params.get('buy_conditions', [])
            sell_conditions = self.params.get('sell_conditions', [])

            signals[self._evaluate_structured_conditions(df, buy_conditions)] = 1
            signals[self._evaluate_structured_conditions(df, sell_conditions)] = -1

        return signals

    def _evaluate_structured_conditions(self, df, conditions):
        if not conditions:
            return pd.Series(False, index=df.index)

        final_mask = pd.Series(True, index=df.index)
        for cond in conditions:
            ind = cond.get('indicator')
            op = cond.get('operator')
            val = cond.get('value')

            if ind not in df.columns:
                continue

            if op == '<':
                mask = df[ind] < val
            elif op == '>':
                mask = df[ind] > val
            elif op == '==':
                mask = df[ind] == val
            elif op == 'cross_above':
                other = cond.get('other_indicator')
                if other in df.columns:
                    mask = (df[ind] > df[other]) & (df[ind].shift(1) <= df[other].shift(1))
                else:
                    mask = (df[ind] > val) & (df[ind].shift(1) <= val)
            elif op == 'cross_below':
                other = cond.get('other_indicator')
                if other in df.columns:
                    mask = (df[ind] < df[other]) & (df[ind].shift(1) >= df[other].shift(1))
                else:
                    mask = (df[ind] < val) & (df[ind].shift(1) >= val)
            else:
                mask = pd.Series(True, index=df.index)

            final_mask &= mask

        return final_mask
