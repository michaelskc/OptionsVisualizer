import dearpygui.dearpygui as dpg
from american_options_gui import setup_american_option_tab
from covered_call_gui import setup_covered_call_tab


def main():
    dpg.create_context()

    dpg.create_viewport(title="Option Strategies", width=1300, height=800)
    dpg.setup_dearpygui()
    dpg.set_viewport_resizable(True)

    with dpg.window(label="Option Strategies", tag="Primary Window", width=1300, height=800):
        with dpg.tab_bar():
            with dpg.tab(label="American Option Simulator"):
                setup_american_option_tab()

            with dpg.tab(label="Covered Call Simulator"):
                setup_covered_call_tab()

    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    main()
