import numpy as np
from scipy.integrate import quad

"""
Bates Model (1996) Implementation
---------------------------------
Dynamics:
dS_t = (r - q - lambda * k) * S_t * dt + sqrt(v_t) * S_t * dW_t^S + (J - 1) * S_t- * dN_t
dv_t = kappa * (theta - v_t) * dt + sigma_v * sqrt(v_t) * dW_t^v

Jump parameters:
- lambda: jump intensity
- mu_j: mean of log-jump size
- sigma_j: std dev of log-jump size
- k = exp(mu_j + 0.5 * sigma_j^2) - 1

Characteristic Function:
phi_bates(u, T) = phi_heston(u, T) * phi_jump(u, T)
"""

def heston_char_func(u, T, S0, r, q, v0, kappa, theta, sigma_v, rho):
    """
    Heston (1993) Characteristic Function (stable formulation).
    Returns E[exp(i * u * ln(S_T))].
    """
    i = 1j
    x0 = np.log(S0)

    alpha = -0.5 * u**2 - 0.5 * i * u
    beta = kappa - rho * sigma_v * i * u
    gamma = 0.5 * sigma_v**2

    d = np.sqrt(beta**2 - 4 * alpha * gamma)
    g = (beta - d) / (beta + d)

    # Stable version of the Heston characteristic function
    C = (r - q) * i * u * T + (kappa * theta / sigma_v**2) * (
        (beta - d) * T - 2 * np.log((1 - g * np.exp(-d * T)) / (1 - g))
    )
    D = (v0 / sigma_v**2) * (beta - d) * (
        (1 - np.exp(-d * T)) / (1 - g * np.exp(-d * T))
    )

    return np.exp(C + D + i * u * x0)

def merton_jump_char_func(u, T, lamb, mu_j, sigma_j):
    """
    Merton Log-Normal Jump Characteristic Function.
    Returns E[exp(i * u * J_comp_T)].
    """
    i = 1j
    k = np.exp(mu_j + 0.5 * sigma_j**2) - 1
    # Compound Poisson process CF for jumps in log-price
    # phi(u) = exp(lambda * T * (E[exp(i u ln J)] - 1 - i u k))
    phi_ln_j = np.exp(i * u * mu_j - 0.5 * sigma_j**2 * u**2)
    jump_comp = lamb * T * (phi_ln_j - 1 - i * u * k)
    return np.exp(jump_comp)

def bates_char_func(u, T, S0, r, q, v0, kappa, theta, sigma_v, rho, lamb, mu_j, sigma_j):
    """
    Combined Bates Characteristic Function.
    """
    phi_h = heston_char_func(u, T, S0, r, q, v0, kappa, theta, sigma_v, rho)
    phi_j = merton_jump_char_func(u, T, lamb, mu_j, sigma_j)
    return phi_h * phi_j

def price_option_bates(S0, K, T, r, q, v0, kappa, theta, sigma_v, rho, lamb, mu_j, sigma_j, option_type='call'):
    """
    Price European Options using Bates model via Gil-Pelaez inversion.
    """
    def integrand(u, p_type):
        i = 1j
        if p_type == 1:
            # P1 characteristic function
            # phi_1(u) = phi(u-i) / phi(-i)
            phi = bates_char_func(u - i, T, S0, r, q, v0, kappa, theta, sigma_v, rho, lamb, mu_j, sigma_j)
            phi_denom = bates_char_func(-i, T, S0, r, q, v0, kappa, theta, sigma_v, rho, lamb, mu_j, sigma_j)
            phi = phi / phi_denom
        else:
            # P2 characteristic function
            phi = bates_char_func(u, T, S0, r, q, v0, kappa, theta, sigma_v, rho, lamb, mu_j, sigma_j)

        res = np.real(np.exp(-i * u * np.log(K)) * phi / (i * u))
        return res

    # Numerical integration for P1 and P2
    # Increased upper limit for quad and handled possible warnings
    p1 = 0.5 + (1/np.pi) * quad(integrand, 1e-8, 200, args=(1,), limit=100)[0]
    p2 = 0.5 + (1/np.pi) * quad(integrand, 1e-8, 200, args=(2,), limit=100)[0]

    # Ensure probabilities are in [0, 1]
    p1 = np.clip(p1, 0, 1)
    p2 = np.clip(p2, 0, 1)

    if option_type == 'call':
        price = S0 * np.exp(-q * T) * p1 - K * np.exp(-r * T) * p2
    else:
        # Put-Call Parity
        call_price = S0 * np.exp(-q * T) * p1 - K * np.exp(-r * T) * p2
        price = call_price - S0 * np.exp(-q * T) + K * np.exp(-r * T)

    return max(price, 0)

def simulate_bates_path(S0, v0, T, dt, r, q, kappa, theta, sigma_v, rho, lamb, mu_j, sigma_j, steps, n_paths=1):
    """
    Simulate Bates model paths using Euler-Maruyama discretization.
    """
    S = np.zeros((steps + 1, n_paths))
    v = np.zeros((steps + 1, n_paths))
    S[0] = S0
    v[0] = v0

    k = np.exp(mu_j + 0.5 * sigma_j**2) - 1

    for t in range(steps):
        # Correlated Brownian motions
        z1 = np.random.normal(size=n_paths)
        z2 = np.random.normal(size=n_paths)
        dW_v = z1 * np.sqrt(dt)
        dW_S = (rho * z1 + np.sqrt(1 - rho**2) * z2) * np.sqrt(dt)

        # Variance process (CIR) - truncated at zero
        v_curr = np.maximum(v[t], 1e-8)
        v[t+1] = v_curr + kappa * (theta - v_curr) * dt + sigma_v * np.sqrt(v_curr) * dW_v
        v[t+1] = np.maximum(v[t+1], 1e-8)

        # Jump process
        n_jumps = np.random.poisson(lamb * dt, size=n_paths)
        total_jumps = np.zeros(n_paths)
        for i in range(n_paths):
            if n_jumps[i] > 0:
                total_jumps[i] = np.sum(np.random.normal(mu_j, sigma_j, size=n_jumps[i]))

        # Asset process (log-price discretization)
        drift = (r - q - lamb * k - 0.5 * v_curr) * dt
        diffusion = np.sqrt(v_curr) * dW_S

        S[t+1] = S[t] * np.exp(drift + diffusion + total_jumps)

    return S, v
