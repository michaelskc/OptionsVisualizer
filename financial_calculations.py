import math
import numpy as np

#
# American Option Simulator (CRR / Binomial Tree)
#

def american_option_price_binomial(S, K, r, q, sigma, T, N, option_type="call"):
    """
    Prices an American option using a Cox-Ross-Rubinstein (CRR) binomial tree model.
    """
    if N <= 0:
        N = 1  # Avoid zero or negative steps

    dt = T / N
    if dt <= 0:
        dt = 0.00001

    # Up and down factors
    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u
    # Risk-neutral probability adjusted for dividend yield
    R_q = np.exp((r - q) * dt)
    p = (R_q - d) / (u - d)

    # Terminal prices
    stock_prices = np.array([S * (u**j) * (d**(N - j)) for j in range(N + 1)])

    # Terminal option payoff
    if option_type.lower() == "call":
        option_values = np.maximum(0, stock_prices - K)
    else:
        option_values = np.maximum(0, K - stock_prices)

    # Iterate backwards
    for i in reversed(range(N)):
        for j in range(i + 1):
            stock_price_ij = S * (u ** j) * (d ** (i - j))
            cont_value = (p * option_values[j + 1] + (1 - p) * option_values[j]) / np.exp(r * dt)
            if option_type.lower() == "call":
                exercise_value = max(0, stock_price_ij - K)
            else:
                exercise_value = max(0, K - stock_price_ij)
            # For American option: max of continuation vs immediate exercise
            option_values[j] = max(cont_value, exercise_value)

    return option_values[0]


def calculate_option_greeks(S, K, r, q, sigma, T, N, option_type="call"):
    h = 0.5
    price_up = american_option_price_binomial(S + h, K, r, q, sigma, T, N, option_type)
    price_down = american_option_price_binomial(S - h, K, r, q, sigma, T, N, option_type)
    price_mid = american_option_price_binomial(S, K, r, q, sigma, T, N, option_type)

    delta = (price_up - price_down) / (2.0 * h)
    gamma = (price_up - 2.0 * price_mid + price_down) / (h ** 2)
    return delta, gamma


def calculate_theta_over_time(S, K, r, q, sigma, days, option_type="call"):
    T = days / 365.0
    time_points, prices, deltas, gammas, thetas = [], [], [], [], []

    for day in range(days + 1):
        t = day / 365.0
        remaining_time = T - t if T - t > 0 else 0.0001
        N = max(50, int(remaining_time * 100))

        price = american_option_price_binomial(S, K, r, q, sigma, remaining_time, N, option_type)
        delta_, gamma_ = calculate_option_greeks(S, K, r, q, sigma, remaining_time, N, option_type)

        prices.append(price)
        deltas.append(delta_)
        gammas.append(gamma_)
        time_points.append(day)

        if day == 0:
            thetas.append(0.0)
        else:
            # Approximate daily Theta
            thetas.append((price - prices[-2]) / (1/365.0))

    return {
        "time_points": time_points,
        "theta_values": thetas,
        "prices": prices,
        "delta_values": deltas,
        "gamma_values": gammas
    }


#
# Covered Call Simulator (Black-Scholes)
#

def _phi(x):
    """CDF for standard normal."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2)))


def _normpdf(x):
    """PDF for standard normal."""
    return (1 / math.sqrt(2 * math.pi)) * math.exp(-0.5 * x ** 2)


def black_scholes_call_price(S, K, T, r, sigma, q=0.0):
    if T <= 0:
        return max(S - K, 0)

    d1 = (math.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    return (S * math.exp(-q * T) * _phi(d1)) - (K * math.exp(-r * T) * _phi(d2))


def black_scholes_call_greeks(S, K, T, r, sigma, q=0.0):
    if T <= 0:
        intrinsic = max(S - K, 0)
        return {
            "Delta": 1.0 if intrinsic > 0 else 0.0,
            "Gamma": 0.0,
            "Theta": 0.0,
            "Vega": 0.0,
            "Rho": 0.0
        }

    d1 = (math.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)

    delta = math.exp(-q * T) * _phi(d1)
    gamma = (math.exp(-q * T) / (S * sigma * math.sqrt(T))) * (1 / math.sqrt(2 * math.pi)) * math.exp(-0.5 * d1 ** 2)
    theta = (
        -(S * math.exp(-q * T) * _normpdf(d1) * sigma) / (2 * math.sqrt(T))
        - r * K * math.exp(-r * T) * _phi(d2)
        + q * S * math.exp(-q * T) * _phi(d1)
    )
    vega = S * math.exp(-q * T) * math.sqrt(T) * _normpdf(d1)
    rho = K * T * math.exp(-r * T) * _phi(d2)

    return {
        "Delta": delta,
        "Gamma": gamma,
        "Theta": theta,
        "Vega": vega,
        "Rho": rho
    }


def simulate_covered_call(initial_price, strike_price, volatility, risk_free_rate, dividend_yield,
                          days_to_expiration, pct_change):
    final_price = initial_price * (1 + pct_change)

    if days_to_expiration == 0:
        call_price = black_scholes_call_price(initial_price, strike_price, 0, risk_free_rate, volatility, dividend_yield)
        covered_call = initial_price - call_price
        greeks = black_scholes_call_greeks(initial_price, strike_price, 0, risk_free_rate, volatility, dividend_yield)
        return [0], [initial_price], [call_price], [covered_call], [greeks]

    days = list(range(days_to_expiration + 1))
    underlying_prices, call_prices, covered_call_positions, greeks_data = [], [], [], []

    for d in days:
        price_at_d = initial_price + (final_price - initial_price) * (d / days_to_expiration)
        t_remain = (days_to_expiration - d) / 365.0

        call_price_d = black_scholes_call_price(
            price_at_d, strike_price, t_remain, risk_free_rate, volatility, dividend_yield
        )
        covered_call_d = price_at_d - call_price_d

        greeks_d = black_scholes_call_greeks(
            price_at_d, strike_price, t_remain, risk_free_rate, volatility, dividend_yield
        )

        underlying_prices.append(price_at_d)
        call_prices.append(call_price_d)
        covered_call_positions.append(covered_call_d)
        greeks_data.append(greeks_d)

    return days, underlying_prices, call_prices, covered_call_positions, greeks_data
