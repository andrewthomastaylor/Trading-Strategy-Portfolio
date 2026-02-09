import numpy as np

class TrinomialTreeModel:
    def __init__(self, S0, r, sigma):
        """
        Initialize Trinomial Tree Model parameters.

        Parameters:
        S0 (float): Initial stock price
        r (float): Risk-free interest rate
        sigma (float): Volatility of the underlying asset
        """
        self.S0 = S0
        self.r = r
        self.sigma = sigma

    def price_option(self, K, T, N, option_type='call', option_style='european'):
        """
        Price an option using the Trinomial Tree model.

        Parameters:
        K (float): Strike price
        T (float): Time to maturity
        N (int): Number of time steps
        option_type (str): 'call' or 'put'
        option_style (str): 'european' or 'american'

        Returns:
        float: Option price
        """
        dt = T / N
        u = np.exp(self.sigma * np.sqrt(2 * dt))
        d = 1 / u

        # Boyle (1986) probabilities
        a = np.exp(self.r * dt / 2)
        b = np.exp(self.sigma * np.sqrt(dt / 2))

        pu = ((a - 1/b) / (b - 1/b))**2
        pd = ((b - a) / (b - 1/b))**2
        pm = 1 - pu - pd

        # Initialize stock prices at maturity
        # After N steps, there are 2N + 1 nodes
        # S[j] = S0 * u^(j - N) for j = 0 to 2N
        j_values = np.arange(2 * N + 1)
        S = self.S0 * (u ** (j_values - N))

        # Option values at maturity
        if option_type == 'call':
            V = np.maximum(S - K, 0)
        elif option_type == 'put':
            V = np.maximum(K - S, 0)
        else:
            raise ValueError("option_type must be 'call' or 'put'")

        # Backward induction
        for i in range(N - 1, -1, -1):
            # Vectorized update of option values at step i
            # Node j at step i connects to j, j+1, j+2 at step i+1
            V[:2*i+1] = np.exp(-self.r * dt) * (pu * V[2:2*i+3] + pm * V[1:2*i+2] + pd * V[:2*i+1])

            if option_style == 'american':
                # Exercise value at step i
                j_vals_i = np.arange(2 * i + 1)
                S_nodes = self.S0 * (u ** (j_vals_i - i))
                if option_type == 'call':
                    V[:2*i+1] = np.maximum(V[:2*i+1], S_nodes - K)
                else:
                    V[:2*i+1] = np.maximum(V[:2*i+1], K - S_nodes)

        return V[0]
