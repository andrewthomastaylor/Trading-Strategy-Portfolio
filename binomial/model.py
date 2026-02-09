import numpy as np

class BinomialModel:
    def __init__(self, s0, r, sigma):
        """
        Initialize Binomial Model parameters.

        Parameters:
        s0 (float): Initial stock price
        r (float): Risk-free interest rate
        sigma (float): Volatility of the underlying asset
        """
        self.s0 = s0
        self.r = r
        self.sigma = sigma

    def price_option(self, K, T, N, option_type='call', exercise_style='european'):
        """
        Price an option using the Cox-Ross-Rubinstein (CRR) binomial tree.

        Parameters:
        K (float): Strike price
        T (float): Time to maturity (in years)
        N (int): Number of steps in the binomial tree
        option_type (str): 'call' or 'put'
        exercise_style (str): 'european' or 'american'

        Returns:
        price (float): Option price
        """
        dt = T / N
        u = np.exp(self.sigma * np.sqrt(dt))
        d = 1 / u
        p = (np.exp(self.r * dt) - d) / (u - d)

        # Initialize asset prices at maturity
        # S[j] will store the price after j up-moves and (N-j) down-moves
        S = np.zeros(N + 1)
        for j in range(N + 1):
            S[j] = self.s0 * (u**j) * (d**(N - j))

        # Initialize option values at maturity
        if option_type == 'call':
            V = np.maximum(S - K, 0)
        elif option_type == 'put':
            V = np.maximum(K - S, 0)
        else:
            raise ValueError("option_type must be 'call' or 'put'")

        # Step back through the tree
        for i in range(N - 1, -1, -1):
            for j in range(i + 1):
                # Expected value under risk-neutral measure
                V[j] = np.exp(-self.r * dt) * (p * V[j + 1] + (1 - p) * V[j])

                if exercise_style == 'american':
                    # Early exercise check
                    S_i_j = self.s0 * (u**j) * (d**(i - j))
                    if option_type == 'call':
                        V[j] = np.maximum(V[j], S_i_j - K)
                    else:
                        V[j] = np.maximum(V[j], K - S_i_j)
                elif exercise_style != 'european':
                    raise ValueError("exercise_style must be 'european' or 'american'")

        return V[0]
