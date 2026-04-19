"""Color palette and CSS for the Regional Sales Dashboard (Grafana/Linear aesthetic)."""

COLORS = {
    "header_bg":    "#0f1117",
    "page_bg":      "#f1f5f9",
    "card_bg":      "#ffffff",
    "accent":       "#4f8ef7",
    "accent_alt":   "#22c55e",
    "warning":      "#f59e0b",
    "danger":       "#ef4444",
    "text_primary": "#0f172a",
    "text_muted":   "#64748b",
    "border":       "#e2e8f0",
}

PALETTE = ["#4f8ef7", "#22c55e", "#f59e0b", "#a78bfa", "#fb923c", "#34d399"]

CUSTOM_CSS = """
.gradio-container {background: #f1f5f9 !important; font-family: Inter, system-ui, sans-serif;}

#app-header {
    background: #0f1117; color: white; padding: 20px 32px;
    border-radius: 0; margin: -16px -16px 16px -16px;
}
#app-header h1 {margin: 0; font-size: 24px; font-weight: 600; color: #ffffff;}
#app-header .subtitle {color: #94a3b8; font-size: 13px; margin-top: 4px;}

#filter-bar {
    background: white; border-radius: 12px; padding: 16px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 16px;
}
#filter-bar label {font-weight: 600; color: #0f172a;}

.kpi-card {
    background: white; border-radius: 16px; padding: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.06);
    border-top: 3px solid #4f8ef7; min-height: 110px;
}
.kpi-card .label {color: #64748b; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px;}
.kpi-card .value {font-size: 32px; font-weight: 700; color: #0f172a; margin-top: 8px;}
.kpi-card .sub {color: #64748b; font-size: 12px; margin-top: 4px;}

.chart-panel {
    background: white; border-radius: 12px; padding: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

.gradio-plot {border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.06);}

.insight-panel {
    background: #eff6ff; border-left: 4px solid #2563eb;
    border-radius: 8px; padding: 16px; margin: 8px 0;
}
.insight-panel h3, .insight-panel h4 {margin-top: 0; color: #1e40af;}
.insight-panel * {color: #0f172a !important;}

.llm-output {
    background: #fefce8; border-left: 4px solid #d97706;
    border-radius: 8px; padding: 16px; margin-top: 8px;
}
.llm-output h3 {margin-top: 0; color: #92400e;}
.llm-output * {color: #0f172a !important;}

button.primary {background: #4f8ef7 !important; border-color: #4f8ef7 !important;}
button.primary:hover {background: #3b7de8 !important;}

.tabs button.selected {color: #4f8ef7 !important; border-color: #4f8ef7 !important;}
"""
