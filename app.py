"""Regional Sales Gradio Dashboard — entry point."""

from __future__ import annotations

import gradio as gr
import pandas as pd

from charts import (
    build_aov_histogram,
    build_channel_pie,
    build_correlation_heatmap,
    build_customer_bar,
    build_customer_bubble,
    build_kpi_cards_html,
    build_margin_by_channel,
    build_monthly_profit,
    build_monthly_revenue,
    build_price_boxplot,
    build_revenue_profit_by_channel,
    build_region_bar,
    build_state_choropleth,
    build_states_dual_bar,
    build_top_products_profit,
    build_top_products_revenue,
)
from data import apply_filters, load_csv
from insights import geo_customer_insight, llm_recommendation, overview_insight, product_channel_insight
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


def render_explorer(df_filtered: pd.DataFrame) -> str:
    try:
        from pygwalker.api.html import to_html
        return to_html(df_filtered, spec_io_mode="rw")
    except Exception as e:
        return f"<div style='padding:24px;color:#a33;'>PyGWalker error: {e}</div>"


def render_tab3(df_filtered: pd.DataFrame, filters: dict, cust_mode: str) -> tuple:
    return (
        build_region_bar(df_filtered),
        build_state_choropleth(df_filtered),
        build_states_dual_bar(df_filtered),
        build_customer_bar(df_filtered, cust_mode),
        build_customer_bubble(df_filtered),
        build_correlation_heatmap(df_filtered),
        geo_customer_insight(df_filtered, filters),
    )


def render_tab2(df_filtered: pd.DataFrame, filters: dict) -> tuple:
    return (
        build_top_products_revenue(df_filtered),
        build_top_products_profit(df_filtered),
        build_channel_pie(df_filtered),
        build_margin_by_channel(df_filtered),
        build_price_boxplot(df_filtered),
        product_channel_insight(df_filtered, filters),
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
        build_revenue_profit_by_channel(df_filtered),
        overview_insight(df_filtered, filters),
    )


def build_app() -> gr.Blocks:
    df_full = load_csv()
    year_choices = sorted(df_full["order_date"].dt.year.unique().tolist())
    channel_choices = sorted(df_full["channel"].unique().tolist())
    region_choices = sorted(df_full["us_region"].unique().tolist())
    product_choices = sorted(
        df_full["product_name"].unique().tolist(),
        key=lambda x: int(x.split()[-1]) if x.split()[-1].isdigit() else x,
    )
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

        with gr.Tabs() as tabs:
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
                    rev_profit_ch_chart = gr.Plot(build_revenue_profit_by_channel(df_full))
                tab1_insight = gr.Markdown(
                    overview_insight(df_full, {}), elem_classes=["insight-panel"]
                )
                tab1_llm_btn = gr.Button("Sinh Strategic Recommendation (AI)", variant="primary")
                tab1_llm_output = gr.Markdown(elem_classes=["llm-output"])
            with gr.Tab("Product & Channel"):
                with gr.Row():
                    tp_rev_chart = gr.Plot(build_top_products_revenue(df_full))
                    tp_profit_chart = gr.Plot(build_top_products_profit(df_full))
                with gr.Row():
                    ch_pie_chart = gr.Plot(build_channel_pie(df_full))
                    ch_margin_chart = gr.Plot(build_margin_by_channel(df_full))
                price_box_chart = gr.Plot(build_price_boxplot(df_full))
                tab2_insight = gr.Markdown(
                    product_channel_insight(df_full, {}), elem_classes=["insight-panel"]
                )
                tab2_llm_btn = gr.Button("Sinh Strategic Recommendation (AI)", variant="primary")
                tab2_llm_output = gr.Markdown(elem_classes=["llm-output"])
            with gr.Tab("Geography & Customer"):
                with gr.Row():
                    region_chart = gr.Plot(build_region_bar(df_full))
                    map_chart = gr.Plot(build_state_choropleth(df_full))
                states_dual_chart = gr.Plot(build_states_dual_bar(df_full))
                with gr.Row():
                    with gr.Column():
                        customer_mode = gr.Radio(
                            ["top", "bottom"], value="top", label="Customer view",
                        )
                        customer_bar_chart = gr.Plot(build_customer_bar(df_full, "top"))
                    bubble_chart = gr.Plot(build_customer_bubble(df_full))
                with gr.Row():
                    heatmap_chart = gr.Plot(build_correlation_heatmap(df_full))
                    tab3_insight = gr.Markdown(
                        geo_customer_insight(df_full, {}), elem_classes=["insight-panel"]
                    )
                tab3_llm_btn = gr.Button("Sinh Strategic Recommendation (AI)", variant="primary")
                tab3_llm_output = gr.Markdown(elem_classes=["llm-output"])
            with gr.Tab("Explorer") as explorer_tab:
                gr.Markdown(
                    "### Data Explorer — PyGWalker\n"
                    "Keo-tha dimension/measure de kham pha du lieu tu do. "
                    "Dataset da duoc ap global filter truoc khi mo tab nay."
                )
                explorer_html = gr.HTML(label="Explorer")

        tab1_outputs = [
            kpi_html, monthly_rev_chart, monthly_profit_chart,
            aov_chart, rev_profit_ch_chart, tab1_insight,
        ]
        tab2_outputs = [
            tp_rev_chart, tp_profit_chart, ch_pie_chart,
            ch_margin_chart, price_box_chart, tab2_insight,
        ]
        tab3_outputs = [
            region_chart, map_chart, states_dual_chart,
            customer_bar_chart, bubble_chart, heatmap_chart, tab3_insight,
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
            ).then(
                fn=render_tab2,
                inputs=[df_filtered_state, filter_dict_state],
                outputs=tab2_outputs,
            ).then(
                fn=render_tab3,
                inputs=[df_filtered_state, filter_dict_state, customer_mode],
                outputs=tab3_outputs,
            )

        monthly_rev_mode.change(
            fn=render_tab1,
            inputs=[df_filtered_state, filter_dict_state, monthly_rev_mode],
            outputs=tab1_outputs,
        )

        customer_mode.change(
            fn=render_tab3,
            inputs=[df_filtered_state, filter_dict_state, customer_mode],
            outputs=tab3_outputs,
        )

        clear_btn.click(
            fn=lambda: clear_filters(year_choices, channel_choices, region_choices),
            outputs=[year_f, channel_f, region_f, product_f],
        )

        tab1_llm_btn.click(
            fn=lambda df, f: llm_recommendation(df, f, "overview"),
            inputs=[df_filtered_state, filter_dict_state],
            outputs=tab1_llm_output,
        )
        tab2_llm_btn.click(
            fn=lambda df, f: llm_recommendation(df, f, "product_channel"),
            inputs=[df_filtered_state, filter_dict_state],
            outputs=tab2_llm_output,
        )
        tab3_llm_btn.click(
            fn=lambda df, f: llm_recommendation(df, f, "geo_customer"),
            inputs=[df_filtered_state, filter_dict_state],
            outputs=tab3_llm_output,
        )

        explorer_tab.select(
            fn=render_explorer,
            inputs=[df_filtered_state],
            outputs=[explorer_html],
        )

    return app


if __name__ == "__main__":
    build_app().launch(
        theme=gr.themes.Soft(),
        css=CUSTOM_CSS,
        inbrowser=True,
    )
