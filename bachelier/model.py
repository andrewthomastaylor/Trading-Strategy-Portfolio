import numpy as np
from scipy.stats import norm

class BachelierModel:
    def __init__(self, s0, sigma, r):
        """
        Initialize Bachelier Model parameters.

        Parameters:
        s0 (float): Initial stock price
        sigma (float): Normal volatility (absolute price volatility per sqrt(year))
        r (float): Risk-free interest rate
        """
        self.s0 = s0
        self.sigma = sigma
        self.r = r

    def simulate_paths(self, T, num_steps, num_paths):
        """
        Simulate asset price paths using Arithmetic Brownian Motion.
        The process is assumed to be dS_t = mu*dt + sigma*dW_t
        where mu is chosen such that E[S_T] = S0 * exp(r*T).
        """
        dt = T / num_steps
        # Drift to match the risk-neutral expectation at time T
        mu = self.s0 * (np.exp(self.r * T) - 1) / T if T > 0 else 0

        S = np.zeros((num_steps + 1, num_paths))
        S[0] = self.s0

        for t in range(1, num_steps + 1):
            z = np.random.standard_normal(num_paths)
            S[t] = S[t-1] + mu * dt + self.sigma * np.sqrt(dt) * z

        return S

    def price_european_option(self, K, T, option_type='call'):
        """
        Price a European option using the Bachelier formula.

        Formula:
        C = e^{-rT} * [(F - K) * N(d) + sigma * sqrt(T) * n(d)]
        P = e^{-rT} * [(K - F) * N(-d) + sigma * sqrt(T) * n(d)]
        where F = S0 * e^{rT} and d = (F - K) / (sigma * sqrt(T))

        Parameters:
        K (float): Strike price
        T (float): Time to maturity
        option_type (str): 'call' or 'put'

        Returns:
        float: Option price
        """
        if T <= 0:
            if option_type == 'call':
                return np.maximum(self.s0 - K, 0)
            else:
                return np.maximum(K - self.s0, 0)

        F = self.s0 * np.exp(self.r * T)
        sigma_sqrt_T = self.sigma * np.sqrt(T)

        if sigma_sqrt_T == 0:
            if option_type == 'call':
                return np.exp(-self.r * T) * np.maximum(F - K, 0)
            else:
                return np.exp(-self.r * T) * np.maximum(K - F, 0)

        d = (F - K) / sigma_sqrt_T

        if option_type == 'call':
            price = np.exp(-self.r * T) * ((F - K) * norm.cdf(d) + sigma_sqrt_T * norm.pdf(d))
        else:
            price = np.exp(-self.r * T) * ((K - F) * norm.cdf(-d) + sigma_sqrt_T * norm.pdf(d))

        return price
