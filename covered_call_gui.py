import dearpygui.dearpygui as dpg

from financial_calculations import simulate_covered_call

# Input parameters and simulation data
simulation_data = {
    "days": [],
    "underlying_prices": [],
    "call_prices": [],
    "covered_call_prices": [],
    "greeks": []
}


def run_simulation_callback():
    try:
        initial_price = float(dpg.get_value("inp_initial_price"))
        strike_price = float(dpg.get_value("inp_strike_price"))
        volatility = float(dpg.get_value("inp_volatility"))
        risk_free_rate = float(dpg.get_value("inp_rfr"))
        dividend_yield = float(dpg.get_value("inp_div_yield"))

        days_to_expiration = int(dpg.get_value("slider_days_to_exp"))
        pct_change = float(dpg.get_value("slider_pct_change")) / 100.0

        (days, underlying_prices, call_prices,
         covered_call_positions, greeks_data_list) = simulate_covered_call(
            initial_price, strike_price, volatility, risk_free_rate,
            dividend_yield, days_to_expiration, pct_change
        )

        simulation_data["days"] = days
        simulation_data["underlying_prices"] = underlying_prices
        simulation_data["call_prices"] = call_prices
        simulation_data["covered_call_prices"] = covered_call_positions
        simulation_data["greeks"] = greeks_data_list

        # Clear old data from the plot axes
        dpg.delete_item("plot_underlying_axis", children_only=True)
        dpg.delete_item("plot_call_axis", children_only=True)

        # Plot new lines
        dpg.add_line_series(days, underlying_prices, parent="plot_underlying_axis", label="Underlying Price")
        dpg.add_line_series(days, call_prices, parent="plot_call_axis", label="Call Option Price")
        dpg.add_line_series(days, covered_call_positions, parent="plot_call_axis", label="Covered Call Value")

        # Display final day Greeks
        if greeks_data_list:
            last_greeks = greeks_data_list[-1]
            dpg.set_value("txt_delta", f"{last_greeks['Delta']:.4f}")
            dpg.set_value("txt_gamma", f"{last_greeks['Gamma']:.4f}")
            dpg.set_value("txt_theta", f"{last_greeks['Theta']:.4f}")
            dpg.set_value("txt_vega", f"{last_greeks['Vega']:.4f}")
            dpg.set_value("txt_rho", f"{last_greeks['Rho']:.4f}")
        else:
            dpg.set_value("txt_delta", "N/A")
            dpg.set_value("txt_gamma", "N/A")
            dpg.set_value("txt_theta", "N/A")
            dpg.set_value("txt_vega", "N/A")
            dpg.set_value("txt_rho", "N/A")

    except ValueError:
        print("Error: One or more input parameters are invalid.")


def reset_callback():
    dpg.set_value("inp_initial_price", "")
    dpg.set_value("inp_strike_price", "")
    dpg.set_value("inp_volatility", "")
    dpg.set_value("inp_rfr", "")
    dpg.set_value("inp_div_yield", "")
    dpg.set_value("slider_days_to_exp", 0)
    dpg.set_value("slider_pct_change", 0)

    dpg.delete_item("plot_underlying_axis", children_only=True)
    dpg.delete_item("plot_call_axis", children_only=True)

    dpg.set_value("txt_delta", "")
    dpg.set_value("txt_gamma", "")
    dpg.set_value("txt_theta", "")
    dpg.set_value("txt_vega", "")
    dpg.set_value("txt_rho", "")

    simulation_data["days"].clear()
    simulation_data["underlying_prices"].clear()
    simulation_data["call_prices"].clear()
    simulation_data["covered_call_prices"].clear()
    simulation_data["greeks"].clear()


def setup_covered_call_tab():
    dpg.add_text("Input Parameters", color=[230, 100, 30])
    dpg.add_spacer(height=2)

    dpg.add_input_text(label="Initial Underlying Price", tag="inp_initial_price", width=200)
    dpg.add_input_text(label="Strike Price", tag="inp_strike_price", width=200)
    dpg.add_input_text(label="Volatility (annualized)", tag="inp_volatility", width=200)
    dpg.add_input_text(label="Risk-Free Interest Rate", tag="inp_rfr", width=200)
    dpg.add_input_text(label="Dividend Yield", tag="inp_div_yield", width=200)

    dpg.add_spacer(height=2)
    dpg.add_separator()
    dpg.add_spacer(height=2)

    dpg.add_slider_int(label="Days to Expiration", tag="slider_days_to_exp", default_value=0,
                       min_value=0, max_value=365, width=300)
    dpg.add_slider_float(label="Underlying Price % Change", tag="slider_pct_change", default_value=0.0,
                         min_value=-100.0, max_value=300.0, width=300, format="%.2f%%")

    dpg.add_spacer(height=2)
    dpg.add_separator()
    dpg.add_spacer(height=2)

    dpg.add_button(label="Run Simulation", callback=run_simulation_callback)
    dpg.add_button(label="Reset", callback=reset_callback)

    dpg.add_spacer(height=2)
    dpg.add_separator()
    dpg.add_spacer(height=2)

    # Plot 1: Underlying Asset
    with dpg.plot(label="Underlying Asset Price", height=250):
        dpg.add_plot_legend()
        with dpg.plot_axis(dpg.mvXAxis, label="Days"):
            pass
        with dpg.plot_axis(dpg.mvYAxis, label="Price", tag="plot_underlying_axis"):
            pass

    # Plot 2: Call & Covered Call
    with dpg.plot(label="Call Option and Covered Call Value", height=250):
        dpg.add_plot_legend()
        with dpg.plot_axis(dpg.mvXAxis, label="Days"):
            pass
        with dpg.plot_axis(dpg.mvYAxis, label="Value", tag="plot_call_axis"):
            pass

    dpg.add_spacer(height=2)
    dpg.add_separator()
    dpg.add_spacer(height=2)

    dpg.add_text("Option Greeks (approximation for expiration date)", color=[230, 100, 30])
    with dpg.group(horizontal=True):
        with dpg.group():
            dpg.add_text("Delta:")
            dpg.add_text("Gamma:")
            dpg.add_text("Theta:")
            dpg.add_text("Vega:")
            dpg.add_text("Rho:")
        with dpg.group():
            dpg.add_text("", tag="txt_delta")
            dpg.add_text("", tag="txt_gamma")
            dpg.add_text("", tag="txt_theta")
            dpg.add_text("", tag="txt_vega")
            dpg.add_text("", tag="txt_rho")
