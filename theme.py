"""Custom CSS and color palette to match the Canva background of the source project."""

COLORS = {
    "header_bg": "#3c3c40",
    "page_bg": "#f6f6f6",
    "card_bg": "#ffffff",
    "accent": "#6b4eff",
    "accent_soft": "#9b86ff",
    "text_primary": "#1a1a1a",
    "text_muted": "#6b6b6b",
    "success": "#2e7d32",
    "warning": "#ed6c02",
}

CUSTOM_CSS = """
.gradio-container {background: #f6f6f6 !important; font-family: Inter, system-ui, sans-serif;}

#app-header {
    background: #3c3c40; color: white; padding: 20px 32px;
    border-radius: 0; margin: -16px -16px 16px -16px;
}
#app-header h1 {margin: 0; font-size: 24px; font-weight: 600;}
#app-header .subtitle {color: #c9c6d9; font-size: 13px; margin-top: 4px;}

#filter-bar {
    background: white; border-radius: 12px; padding: 16px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08); margin-bottom: 16px;
}
#filter-bar label {font-weight: 600; color: #3c3c40;}

.kpi-card {
    background: white; border-radius: 16px; padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.10);
    border-top: 3px solid #6b4eff; min-height: 110px;
}
.kpi-card .label {color: #6b6b6b; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px;}
.kpi-card .value {font-size: 28px; font-weight: 700; color: #1a1a1a; margin-top: 8px;}
.kpi-card .sub {color: #6b6b6b; font-size: 12px; margin-top: 4px;}

.chart-panel {
    background: white; border-radius: 12px; padding: 8px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}

.insight-panel {
    background: #f3f1ff; border-left: 4px solid #6b4eff;
    border-radius: 8px; padding: 16px; margin: 8px 0;
}
.insight-panel h3, .insight-panel h4 {margin-top: 0; color: #3c3c40;}
.insight-panel * {color: #1a1a1a !important;}

.llm-output {
    background: #fff7e6; border-left: 4px solid #ed6c02;
    border-radius: 8px; padding: 16px; margin-top: 8px;
}
.llm-output h3 {margin-top: 0; color: #b45309;}
.llm-output * {color: #1a1a1a !important;}

button.primary {background: #6b4eff !important; border-color: #6b4eff !important;}
button.primary:hover {background: #5a3de0 !important;}

.tabs button.selected {color: #6b4eff !important; border-color: #6b4eff !important;}

.gradio-plot {border-radius: 12px; overflow: hidden;}
"""
