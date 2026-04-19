"""Regional Sales Gradio Dashboard — entry point."""

from __future__ import annotations

import gradio as gr
import pandas as pd

from data import apply_filters, load_csv
from theme import CUSTOM_CSS


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
        "product_name": products or [],
    }
    df_filtered = apply_filters(df_full, filters)
    return df_filtered, filters


def clear_filters() -> tuple[list, list, list, list]:
    return [], [], [], []


def build_app() -> gr.Blocks:
    df_full = load_csv()
    year_choices = sorted(df_full["order_date"].dt.year.unique().tolist())
    channel_choices = sorted(df_full["channel"].unique().tolist())
    region_choices = sorted(df_full["us_region"].unique().tolist())
    product_choices = sorted(df_full["product_name"].unique().tolist())

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
                product_choices, label="Product", multiselect=True, value=[]
            )
            clear_btn = gr.Button("Clear Filters", variant="secondary", scale=0)

        with gr.Tabs():
            with gr.Tab("Overview"):
                gr.Markdown("*(Tab 1 content - will be added in Phase 2)*")
            with gr.Tab("Product & Channel"):
                gr.Markdown("*(Tab 2 content - will be added in Phase 3)*")
            with gr.Tab("Geography & Customer"):
                gr.Markdown("*(Tab 3 content - will be added in Phase 4)*")
            with gr.Tab("Explorer"):
                gr.Markdown("*(Tab 4 PyGWalker - will be added in Phase 6)*")

        filter_inputs = [df_full_state, year_f, channel_f, region_f, product_f]
        for widget in [year_f, channel_f, region_f, product_f]:
            widget.change(
                fn=build_filter_state,
                inputs=filter_inputs,
                outputs=[df_filtered_state, filter_dict_state],
            )

        clear_btn.click(
            fn=clear_filters,
            outputs=[year_f, channel_f, region_f, product_f],
        )

    return app


if __name__ == "__main__":
    build_app().launch(
        theme=gr.themes.Soft(),
        css=CUSTOM_CSS,
        inbrowser=True,
    )
