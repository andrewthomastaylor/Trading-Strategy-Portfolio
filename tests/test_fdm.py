import numpy as np
from scipy.stats import norm
from fdm.model import FiniteDifferenceModel

def black_scholes_price(S, K, T, r, sigma, option_type='call'):
    if T == 0:
        return max(S - K, 0) if option_type == 'call' else max(K - S, 0)
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if option_type == 'call':
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

def test_fdm_european_call():
    model = FiniteDifferenceModel(m=200, n=2000)
    S, K, T, r, sigma = 100, 100, 1, 0.05, 0.2
    fdm_price = model.price_option(S, K, T, r, sigma, option_type='call', exercise_style='european')
    bs_price = black_scholes_price(S, K, T, r, sigma, option_type='call')
    # Allow some tolerance for numerical approximation
    assert abs(fdm_price - bs_price) < 0.05

def test_fdm_european_put():
    model = FiniteDifferenceModel(m=200, n=2000)
    S, K, T, r, sigma = 100, 100, 1, 0.05, 0.2
    fdm_price = model.price_option(S, K, T, r, sigma, option_type='put', exercise_style='european')
    bs_price = black_scholes_price(S, K, T, r, sigma, option_type='put')
    assert abs(fdm_price - bs_price) < 0.05

def test_fdm_american_put():
    model = FiniteDifferenceModel(m=200, n=2000)
    S, K, T, r, sigma = 100, 100, 1, 0.05, 0.2
    euro_price = model.price_option(S, K, T, r, sigma, option_type='put', exercise_style='european')
    amer_price = model.price_option(S, K, T, r, sigma, option_type='put', exercise_style='american')
    assert amer_price >= euro_price

    # In-the-money case where early exercise is optimal
    S_itm = 70
    euro_price_itm = model.price_option(S_itm, K, T, r, sigma, option_type='put', exercise_style='european')
    amer_price_itm = model.price_option(S_itm, K, T, r, sigma, option_type='put', exercise_style='american')
    assert amer_price_itm > euro_price_itm
    # American put should be at least its intrinsic value
    assert amer_price_itm >= (K - S_itm)

def test_custom_payoff():
    # Test with a simple digital-like payoff: 1 if S > K else 0
    def digital_payoff(S_grid):
        return (S_grid > 100).astype(float)

    model = FiniteDifferenceModel(m=200, n=2000)
    S, K, T, r, sigma = 100, 100, 1, 0.05, 0.2
    price = model.price_option(S, K, T, r, sigma, payoff_func=digital_payoff)
    # Digital call price is exp(-rT) * N(d2)
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    expected = np.exp(-r * T) * norm.cdf(d2)
    assert abs(price - expected) < 0.05
