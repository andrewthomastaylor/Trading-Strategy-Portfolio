import numpy as np
from bates_strategy.model import price_option_bates
from scipy.stats import norm

def black_scholes_price(S0, K, T, r, q, sigma, option_type='call'):
    d1 = (np.log(S0 / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if option_type == 'call':
        return S0 * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        return K * np.exp(-r * T) * norm.cdf(-d2) - S0 * np.exp(-q * T) * norm.cdf(-d1)

def test_bs_convergence():
    # Parameters for BS convergence
    S0, K, T, r, q = 100, 100, 1.0, 0.05, 0.02
    sigma = 0.2

    # Bates params to simulate BS
    v0 = sigma**2
    kappa = 1.0
    theta = sigma**2
    sigma_v = 0.0001 # Almost zero vol-of-vol
    rho = 0.0
    lamb = 0.0       # No jumps
    mu_j = 0.0
    sigma_j = 0.0001

    bs_p = black_scholes_price(S0, K, T, r, q, sigma)
    bates_p = price_option_bates(S0, K, T, r, q, v0, kappa, theta, sigma_v, rho, lamb, mu_j, sigma_j)

    print(f"BS Price: {bs_p:.4f}")
    print(f"Bates Price (BS limit): {bates_p:.4f}")

    assert np.abs(bs_p - bates_p) < 1e-3, f"Difference too large: {np.abs(bs_p - bates_p)}"

def test_heston_limit():
    # Ensure it prices correctly without jumps
    S0, K, T, r, q = 100, 100, 0.5, 0.03, 0.01
    v0, kappa, theta, sigma_v, rho = 0.04, 2.0, 0.04, 0.3, -0.7

    bates_p_no_jumps = price_option_bates(S0, K, T, r, q, v0, kappa, theta, sigma_v, rho, 0.0, 0.0, 0.0)
    print(f"Bates (Heston limit) Price: {bates_p_no_jumps:.4f}")
    assert bates_p_no_jumps > 0

if __name__ == "__main__":
    print("Running test_bs_convergence...")
    test_bs_convergence()
    print("Running test_heston_limit...")
    test_heston_limit()
    print("All tests passed!")
