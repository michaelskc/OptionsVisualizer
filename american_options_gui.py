import time
import dearpygui.dearpygui as dpg
from financial_calculations import calculate_theta_over_time

# Results storage
scenario_data_store = {}


def on_calculate_theta():
    S = dpg.get_value("input_S")
    K = dpg.get_value("input_K")
    volatility = dpg.get_value("input_volatility")
    r = dpg.get_value("input_r")
    q = dpg.get_value("input_q")
    days = dpg.get_value("slider_days")
    option_type = dpg.get_value("input_option_type").lower()

    results = calculate_theta_over_time(S, K, r, q, volatility, days, option_type)
    scenario_id = f"scenario_{int(time.time())}"
    scenario_data_store[scenario_id] = results

    # Update plots
    dpg.set_value("theta_series", [results["time_points"], results["theta_values"]])
    dpg.fit_axis_data("theta_x_axis")
    dpg.fit_axis_data("theta_y_axis")

    dpg.set_value("delta_series", [results["time_points"], results["delta_values"]])
    dpg.set_value("gamma_series", [results["time_points"], results["gamma_values"]])
    dpg.fit_axis_data("dg_x_axis")
    dpg.fit_axis_data("dg_y_axis")


def on_reset():
    scenario_data_store.clear()
    dpg.set_value("input_S", 100.0)
    dpg.set_value("input_K", 100.0)
    dpg.set_value("input_sigma", 0.2)
    dpg.set_value("input_r", 0.01)
    dpg.set_value("input_q", 0.0)
    dpg.set_value("input_option_type", "Call")
    dpg.set_value("slider_days", 30)

    dpg.set_value("theta_series", [[], []])
    dpg.set_value("delta_series", [[], []])
    dpg.set_value("gamma_series", [[], []])

    dpg.fit_axis_data("theta_x_axis")
    dpg.fit_axis_data("theta_y_axis")
    dpg.fit_axis_data("dg_x_axis")
    dpg.fit_axis_data("dg_y_axis")


def setup_american_option_tab():
    with dpg.group(horizontal=False):
        # Input Parameters
        with dpg.child_window(label="Input Parameters", width=-1, height=280):
            dpg.add_text("Option Parameters")
            dpg.add_separator()

            dpg.add_input_float(label="Stock Price (S)", tag="input_S", default_value=100.0)
            dpg.add_input_float(label="Strike Price (K)", tag="input_K", default_value=100.0)
            dpg.add_input_float(label="Volatility (σ)", tag="input_volatility", default_value=0.2, format="%.4f")
            dpg.add_input_float(label="Risk-free Rate (r)", tag="input_r", default_value=0.01, format="%.4f")
            dpg.add_input_float(label="Dividend Yield (q)", tag="input_q", default_value=0.0, format="%.4f")

            dpg.add_radio_button(("Call", "Put"), label="Option Type", tag="input_option_type", default_value="Call")
            dpg.add_slider_int(label="Days to Expiration", tag="slider_days", default_value=30, min_value=1,
                               max_value=365)

            dpg.add_separator()
            dpg.add_button(label="Calculate Theta", callback=on_calculate_theta)
            dpg.add_button(label="Reset", callback=on_reset)
            dpg.add_spacer(height=10)

        # Theta Decay Chart
        with dpg.child_window(label="Theta Decay Chart", width=-1, height=250):
            with dpg.plot(label="Theta Decay", tag="plot_theta", height=-1, width=-1):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis, label="Days", tag="theta_x_axis")
                with dpg.plot_axis(dpg.mvYAxis, label="Theta", tag="theta_y_axis"):
                    dpg.add_line_series([], [], label="Theta", tag="theta_series")

        #  Delta / Gamma Chart
        with dpg.child_window(label="Delta & Gamma Chart", width=-1, height=-1):
            with dpg.plot(label="Delta & Gamma", tag="plot_dg", height=-1, width=-1):
                dpg.add_plot_legend()
                dpg.add_plot_axis(dpg.mvXAxis, label="Days", tag="dg_x_axis")
                with dpg.plot_axis(dpg.mvYAxis, label="Value", tag="dg_y_axis"):
                    dpg.add_line_series([], [], label="Delta", tag="delta_series")
                    dpg.add_line_series([], [], label="Gamma", tag="gamma_series")
