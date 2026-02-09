import numpy as np
from scipy.integrate import quad

class HestonModel:
    def __init__(self, s0, v0, kappa, theta, sigma, rho, r):
        """
        Initialize Heston Model parameters.

        Parameters:
        s0 (float): Initial stock price
        v0 (float): Initial variance
        kappa (float): Rate of mean reversion of variance
        theta (float): Long-term mean of variance
        sigma (float): Volatility of volatility
        rho (float): Correlation between asset and volatility
        r (float): Risk-free interest rate
        """
        self.s0 = s0
        self.v0 = v0
        self.kappa = kappa
        self.theta = theta
        self.sigma = sigma
        self.rho = rho
        self.r = r

    def simulate_paths(self, T, num_steps, num_paths):
        """
        Simulate asset price paths using the Euler-Maruyama method.

        Parameters:
        T (float): Time to maturity (in years)
        num_steps (int): Number of time steps
        num_paths (int): Number of simulated paths

        Returns:
        S (numpy.ndarray): Simulated stock price paths
        V (numpy.ndarray): Simulated variance paths
        """
        dt = T / num_steps
        S = np.zeros((num_steps + 1, num_paths))
        V = np.zeros((num_steps + 1, num_paths))

        S[0] = self.s0
        V[0] = self.v0

        for t in range(1, num_steps + 1):
            # Generate correlated random variables
            z1 = np.random.standard_normal(num_paths)
            z2 = np.random.standard_normal(num_paths)

            zv = z1
            zs = self.rho * z1 + np.sqrt(1 - self.rho**2) * z2

            # Update variance (Full Truncation to handle negative variance)
            v_prev = np.maximum(V[t-1], 0)
            V[t] = V[t-1] + self.kappa * (self.theta - v_prev) * dt + \
                   self.sigma * np.sqrt(v_prev * dt) * zv
            V[t] = np.maximum(V[t], 0)

            # Update stock price
            S[t] = S[t-1] * np.exp((self.r - 0.5 * v_prev) * dt + \
                                    np.sqrt(v_prev * dt) * zs)

        return S, V

    def characteristic_function(self, u, T):
        """
        Characteristic function for the Heston model (Albrecher et al. 2007 formulation).
        """
        # Parameters
        x = np.log(self.s0)
        a = self.kappa * self.theta
        b = self.kappa

        # d parameter
        d = np.sqrt((self.rho * self.sigma * u * 1j - b)**2 +
                    self.sigma**2 * (u * 1j + u**2))

        # g parameter
        g = (b - self.rho * self.sigma * u * 1j - d) / (b - self.rho * self.sigma * u * 1j + d)

        # Characteristic function
        term1 = self.r * u * 1j * T
        term2 = (a / self.sigma**2) * ((b - self.rho * self.sigma * u * 1j - d) * T -
                                         2 * np.log((1 - g * np.exp(-d * T)) / (1 - g)))
        term3 = (self.v0 / self.sigma**2) * (b - self.rho * self.sigma * u * 1j - d) * \
                (1 - np.exp(-d * T)) / (1 - g * np.exp(-d * T))

        return np.exp(term1 + term2 + term3 + u * 1j * x)

    def price_european_option(self, K, T, option_type='call'):
        """
        Price a European option using the Heston closed-form solution (Fourier Transform).

        Parameters:
        K (float): Strike price
        T (float): Time to maturity
        option_type (str): 'call' or 'put'

        Returns:
        price (float): Option price
        """
        def call_integrand(u):
            # Characteristic function for P2 (phi(u))
            phi = self.characteristic_function(u, T)
            # Characteristic function for P1 (phi(u-i))
            phi_minus_i = self.characteristic_function(u - 1j, T)

            # Using the relation:
            # P1 = 0.5 + 1/pi * integral( Re[ exp(-iu*lnK) * phi(u-i) / (iu * exp(rT) * S0) ] )
            # P2 = 0.5 + 1/pi * integral( Re[ exp(-iu*lnK) * phi(u) / (iu) ] )
            # Call = S0*P1 - K*exp(-rT)*P2

            p1_term = np.real(np.exp(-u * 1j * np.log(K)) * phi_minus_i / (u * 1j * self.s0 * np.exp(self.r * T)))
            p2_term = np.real(np.exp(-u * 1j * np.log(K)) * phi / (u * 1j))

            return self.s0 * p1_term - K * np.exp(-self.r * T) * p2_term

        # Integrate from 0 to infinity (using a large enough value or np.inf)
        # Using 1000 and dynamic limit for better precision
        integral_call, _ = quad(call_integrand, 0, np.inf, limit=100)
        call_price = 0.5 * (self.s0 - K * np.exp(-self.r * T)) + (1 / np.pi) * integral_call

        if option_type == 'call':
            return call_price
        else:
            # Put-Call Parity: C - P = S - K*exp(-rT) => P = C - S + K*exp(-rT)
            return call_price - self.s0 + K * np.exp(-self.r * T)
