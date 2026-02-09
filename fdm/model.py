import numpy as np
from scipy.interpolate import interp1d
from scipy.linalg import solve_banded

class FiniteDifferenceModel:
    def __init__(self, s_max_mult=3, m=100, n=1000):
        """
        Initialize Finite Difference Model parameters.

        Parameters:
        s_max_mult (float): Multiplier for S_max relative to strike price.
        m (int): Number of price steps.
        n (int): Number of time steps.
        """
        self.s_max_mult = s_max_mult
        self.m = m
        self.n = n

    def price_option(self, s0, k, t, r, sigma, option_type='call', exercise_style='european', payoff_func=None):
        """
        Price an option using the Implicit Finite Difference Method.

        Parameters:
        s0 (float): Initial stock price
        k (float): Strike price
        t (float): Time to maturity
        r (float): Risk-free interest rate
        sigma (float): Volatility
        option_type (str): 'call' or 'put'
        exercise_style (str): 'european' or 'american'
        payoff_func (callable): Custom payoff function. If None, uses standard call/put payoff.

        Returns:
        float: Option price
        """
        # Grid parameters
        s_max = k * self.s_max_mult
        ds = s_max / self.m
        dt = t / self.n

        s_grid = np.linspace(0, s_max, self.m + 1)

        # Pre-calculate payoff
        if payoff_func is None:
            if option_type == 'call':
                payoff = np.maximum(s_grid - k, 0)
            else:
                payoff = np.maximum(k - s_grid, 0)
        else:
            payoff = payoff_func(s_grid)

        # Initial value at T is the payoff
        v = payoff.copy()

        # Matrix setup for implicit scheme: A * V_i = V_{i+1}
        # PDE: dV/dt + 0.5 * sigma^2 * S^2 * d^2V/dS^2 + r * S * dV/dS - r * V = 0
        # Let tau = T - t, then dV/dtau = 0.5 * sigma^2 * S^2 * d^2V/dS^2 + r * S * dV/dS - r * V

        # Discretization:
        # (v_j^{i+1} - v_j^i) / dt = 0.5 * sigma^2 * (j*ds)^2 * (v_{j+1}^i - 2*v_j^i + v_{j-1}^i) / ds^2
        #                           + r * (j*ds) * (v_{j+1}^i - v_{j-1}^i) / (2*ds) - r * v_j^i

        # Rearranging to: a_j * v_{j-1}^i + b_j * v_j^i + c_j * v_{j+1}^i = v_j^{i+1}

        j = np.arange(1, self.m)
        a = 0.5 * dt * (r * j - sigma**2 * j**2)
        b = 1 + dt * (sigma**2 * j**2 + r)
        c = -0.5 * dt * (r * j + sigma**2 * j**2)

        # Setup for solve_banded (tridiagonal matrix)
        # Row 0: upper diagonal (c[0] to c[M-3])
        # Row 1: main diagonal (b[0] to b[M-2])
        # Row 2: lower diagonal (a[1] to a[M-2])
        ab = np.zeros((3, self.m - 1))
        ab[0, 1:] = c[:-1] # upper diagonal
        ab[1, :] = b       # main diagonal
        ab[2, :-1] = a[1:] # lower diagonal

        is_american = exercise_style.lower() == 'american'

        # Time stepping
        for i in range(self.n):
            rhs = v[1:-1].copy()

            # Boundary conditions at time i+1 (tau = (i+1)*dt)
            tau = (i + 1) * dt

            if option_type == 'call':
                v_0 = 0
                v_m = s_max - k * np.exp(-r * tau)
            else:
                v_0 = k * np.exp(-r * tau)
                v_m = 0

            # Adjust rhs for Dirichlet boundary conditions
            rhs[0] -= a[0] * v_0
            rhs[-1] -= c[-1] * v_m

            # Solve A * v_new = rhs using solve_banded for O(M) performance
            v_new = solve_banded((1, 1), ab, rhs)

            v[1:-1] = v_new
            v[0] = v_0
            v[-1] = v_m

            # For American options, apply early exercise constraint
            if is_american:
                v = np.maximum(v, payoff)

        # Interpolate to find price at s0
        f = interp1d(s_grid, v, kind='cubic')

        # Handle cases where s0 is outside the grid
        s0_clipped = np.clip(s0, 0, s_max)
        return float(f(s0_clipped))
