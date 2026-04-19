"""Regional Sales Gradio Dashboard — entry point."""

from __future__ import annotations

import gradio as gr
import pandas as pd

from charts import (
    build_aov_histogram,
    build_kpi_cards_html,
    build_monthly_profit,
    build_monthly_revenue,
    build_price_margin_scatter,
)
from data import apply_filters, load_csv
from insights import overview_insight
from theme import CUSTOM_CSS

ALL_PRODUCTS_LABEL = "All Products"


def _resolve_product_filter(products: list[str] | None) -> list[str]:
    """If the sentinel 'All Products' is selected, return []  (no filter)."""
    if not products:
        return []
    if ALL_PRODUCTS_LABEL in products:
        return []
    return products


def build_filter_state(
    df_full: pd.DataFrame,
    years: list[int],
    channels: list[str],
    regions: list[str],
    products: list[str],
) -> tuple[pd.DataFrame, dict]:
    filters = {
        "year": years or [],
        "channel": channels or [],
        "us_region": regions or [],
        "product_name": _resolve_product_filter(products),
    }
    df_filtered = apply_filters(df_full, filters)
    return df_filtered, filters


def clear_filters(
    year_choices: list[int],
    channel_choices: list[str],
    region_choices: list[str],
) -> tuple[list, list, list, list]:
    return (
        year_choices,
        channel_choices,
        region_choices,
        [ALL_PRODUCTS_LABEL],
    )


def render_tab1(
    df_filtered: pd.DataFrame,
    filters: dict,
    rev_mode: str,
) -> tuple:
    return (
        build_kpi_cards_html(df_filtered),
        build_monthly_revenue(df_filtered, rev_mode),
        build_monthly_profit(df_filtered),
        build_aov_histogram(df_filtered),
        build_price_margin_scatter(df_filtered),
        overview_insight(df_filtered, filters),
    )


def build_app() -> gr.Blocks:
    df_full = load_csv()
    year_choices = sorted(df_full["order_date"].dt.year.unique().tolist())
    channel_choices = sorted(df_full["channel"].unique().tolist())
    region_choices = sorted(df_full["us_region"].unique().tolist())
    product_choices = sorted(df_full["product_name"].unique().tolist())
    product_dropdown_choices = [ALL_PRODUCTS_LABEL] + product_choices

    with gr.Blocks(title="USA Regional Sales Dashboard") as app:
        df_full_state = gr.State(df_full)
        df_filtered_state = gr.State(df_full)
        filter_dict_state = gr.State({})

        gr.HTML(
            """
            <div id='app-header'>
                <h1>USA Regional Sales Dashboard</h1>
                <div class='subtitle'>Acme Co. - 2014-2018 - Truc quan hoa du lieu ban hang</div>
            </div>
            """
        )

        with gr.Row(elem_id="filter-bar"):
            year_f = gr.CheckboxGroup(
                year_choices, label="Year", value=year_choices
            )
            channel_f = gr.CheckboxGroup(
                channel_choices, label="Channel", value=channel_choices
            )
            region_f = gr.CheckboxGroup(
                region_choices, label="US Region", value=region_choices
            )
            product_f = gr.Dropdown(
                product_dropdown_choices,
                label="Product",
                multiselect=True,
                value=[ALL_PRODUCTS_LABEL],
                info="Select 'All Products' to show every SKU, or pick specific products.",
            )
            clear_btn = gr.Button("Clear Filters", variant="secondary", scale=0)

        with gr.Tabs():
            with gr.Tab("Overview"):
                kpi_html = gr.HTML(build_kpi_cards_html(df_full))
                with gr.Row():
                    monthly_rev_mode = gr.Radio(
                        ["timeseries", "seasonal"],
                        value="timeseries",
                        label="Monthly Revenue view",
                        scale=1,
                    )
                with gr.Row():
                    monthly_rev_chart = gr.Plot(build_monthly_revenue(df_full, "timeseries"))
                    monthly_profit_chart = gr.Plot(build_monthly_profit(df_full))
                with gr.Row():
                    aov_chart = gr.Plot(build_aov_histogram(df_full))
                    scatter_chart = gr.Plot(build_price_margin_scatter(df_full))
                tab1_insight = gr.Markdown(
                    overview_insight(df_full, {}), elem_classes=["insight-panel"]
                )
            with gr.Tab("Product & Channel"):
                gr.Markdown("*(Tab 2 content - will be added in Phase 3)*")
            with gr.Tab("Geography & Customer"):
                gr.Markdown("*(Tab 3 content - will be added in Phase 4)*")
            with gr.Tab("Explorer"):
                gr.Markdown("*(Tab 4 PyGWalker - will be added in Phase 6)*")

        tab1_outputs = [
            kpi_html, monthly_rev_chart, monthly_profit_chart,
            aov_chart, scatter_chart, tab1_insight,
        ]

        filter_inputs = [df_full_state, year_f, channel_f, region_f, product_f]
        for widget in [year_f, channel_f, region_f, product_f]:
            widget.change(
                fn=build_filter_state,
                inputs=filter_inputs,
                outputs=[df_filtered_state, filter_dict_state],
            ).then(
                fn=render_tab1,
                inputs=[df_filtered_state, filter_dict_state, monthly_rev_mode],
                outputs=tab1_outputs,
            )

        monthly_rev_mode.change(
            fn=render_tab1,
            inputs=[df_filtered_state, filter_dict_state, monthly_rev_mode],
            outputs=tab1_outputs,
        )

        clear_btn.click(
            fn=lambda: clear_filters(year_choices, channel_choices, region_choices),
            outputs=[year_f, channel_f, region_f, product_f],
        )

    return app


if __name__ == "__main__":
    build_app().launch(
        theme=gr.themes.Soft(),
        css=CUSTOM_CSS,
        inbrowser=True,
    )
