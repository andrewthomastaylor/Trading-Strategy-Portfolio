import numpy as np
from .model import price_option_bates, simulate_bates_path, bates_char_func
from scipy.integrate import quad

class Backtester:
    def __init__(self, market_params, model_params, S0, v0, r, q, T, dt, steps):
        self.market_params = market_params # True params for simulation
        self.model_params = model_params   # Trader's perceived params
        self.S0 = S0
        self.v0 = v0
        self.r = r
        self.q = q
        self.T = T
        self.dt = dt
        self.steps = steps

        # Simulation results
        self.S_path = None
        self.v_path = None

        # Portfolio state
        self.cash = 1000000.0 # Starting with 1M cash
        self.underlying_units = 0.0
        self.option_units = 0.0
        self.portfolio_value = []
        self.option_details = None # (K, type)

    def simulate_market(self):
        """Simulate the 'true' market path."""
        p = self.market_params
        self.S_path, self.v_path = simulate_bates_path(
            self.S0, self.v0, self.T, self.dt, self.r, self.q,
            p['kappa'], p['theta'], p['sigma_v'], p['rho'],
            p['lamb'], p['mu_j'], p['sigma_j'], self.steps
        )
        # Flatten paths to 1D
        self.S_path = self.S_path.flatten()
        self.v_path = self.v_path.flatten()

    def calculate_model_delta(self, S, K, t_rem, v):
        """Calculate Delta using the model's perceived parameters."""
        if t_rem <= 1e-5:
            return 1.0 if (S > K) else 0.0

        p = self.model_params

        def integrand(u):
            i = 1j
            # Delta is exp(-q * T) * P1
            # P1 CF is phi(u-i) / phi(-i)
            phi = bates_char_func(u - i, t_rem, S, self.r, self.q, v,
                                 p['kappa'], p['theta'], p['sigma_v'], p['rho'],
                                 p['lamb'], p['mu_j'], p['sigma_j'])
            phi_denom = bates_char_func(-i, t_rem, S, self.r, self.q, v,
                                       p['kappa'], p['theta'], p['sigma_v'], p['rho'],
                                       p['lamb'], p['mu_j'], p['sigma_j'])
            phi_p1 = phi / phi_denom
            res = np.real(np.exp(-i * u * np.log(K)) * phi_p1 / (i * u))
            return res

        p1 = 0.5 + (1/np.pi) * quad(integrand, 1e-8, 200, limit=100)[0]
        delta = np.exp(-self.q * t_rem) * np.clip(p1, 0, 1)
        return delta

    def run_backtest(self, K, option_type='call', threshold=0.01):
        """Run the trading strategy."""
        self.simulate_market()
        self.option_details = (K, option_type)

        p_model = self.model_params
        p_market = self.market_params

        for t in range(self.steps):
            S_curr = self.S_path[t]
            v_curr = self.v_path[t]
            t_rem = self.T - t * self.dt

            # 1. Theoretical Model Price
            theo_price = price_option_bates(
                S_curr, K, t_rem, self.r, self.q, v_curr,
                p_model['kappa'], p_model['theta'], p_model['sigma_v'], p_model['rho'],
                p_model['lamb'], p_model['mu_j'], p_model['sigma_j'], option_type
            )

            # 2. 'Market' Price (also using Bates but with market params)
            # In a real backtest this would be actual market data.
            market_price = price_option_bates(
                S_curr, K, t_rem, self.r, self.q, v_curr,
                p_market['kappa'], p_market['theta'], p_market['sigma_v'], p_market['rho'],
                p_market['lamb'], p_market['mu_j'], p_market['sigma_j'], option_type
            )

            # 3. Strategy Logic: Identify mispricing
            # We buy if market is cheap, sell if market is expensive relative to model
            if self.option_units == 0:
                if market_price < theo_price * (1 - threshold):
                    # Buy 1000 options
                    self.option_units = 1000.0
                    self.cash -= self.option_units * market_price
                elif market_price > theo_price * (1 + threshold):
                    # Sell 1000 options
                    self.option_units = -1000.0
                    self.cash -= self.option_units * market_price

            # 4. Delta Hedging
            if self.option_units != 0:
                delta = self.calculate_model_delta(S_curr, K, t_rem, v_curr)
                if option_type == 'put':
                    delta -= 1.0 # Delta of put = Delta of call - 1 (approx)

                target_underlying = -self.option_units * delta
                trade_units = target_underlying - self.underlying_units
                self.cash -= trade_units * S_curr
                self.underlying_units = target_underlying

            # 5. Portfolio Value Update
            current_opt_val = 0
            if self.option_units != 0:
                current_opt_val = self.option_units * market_price

            total_val = self.cash + self.underlying_units * S_curr + current_opt_val
            self.portfolio_value.append(total_val)

            # Update cash with interest
            self.cash *= np.exp(self.r * self.dt)

        return self.portfolio_value
