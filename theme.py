"""Color palette and CSS for the Regional Sales Dashboard (modern light theme)."""

COLORS = {
    "header_bg":    "#4f8ef7",
    "header_bg2":   "#6366f1",
    "page_bg":      "#f8faff",
    "card_bg":      "#ffffff",
    "accent":       "#4f8ef7",
    "accent_2":     "#6366f1",
    "accent_alt":   "#10b981",
    "warning":      "#f59e0b",
    "danger":       "#ef4444",
    "text_primary": "#1e293b",
    "text_muted":   "#64748b",
    "border":       "#e2e8f0",
}

PALETTE = ["#4f8ef7", "#10b981", "#f59e0b", "#6366f1", "#fb923c", "#34d399"]

CUSTOM_CSS = """
/* ── Base layout ─────────────────────────────────────────────── */
.gradio-container {
    background: #f8faff !important;
    font-family: Inter, system-ui, sans-serif;
    max-width: 100% !important;
}

/* ── App header ──────────────────────────────────────────────── */
#app-header {
    background: linear-gradient(135deg, #4f8ef7 0%, #6366f1 100%);
    color: white;
    padding: 24px 32px;
    border-radius: 16px;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(79, 142, 247, 0.3);
}
#app-header h1 {
    margin: 0;
    font-size: 26px;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.3px;
}
#app-header .subtitle {
    color: rgba(255,255,255,0.8);
    font-size: 13px;
    margin-top: 6px;
}

/* ── Filter bar ──────────────────────────────────────────────── */
#filter-bar {
    background: #ffffff;
    border-radius: 14px;
    padding: 16px 20px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}
#filter-bar label {
    font-weight: 600;
    color: #1e293b;
    font-size: 13px;
}

/* ── KPI cards ───────────────────────────────────────────────── */
.kpi-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 20px 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.05);
    border-top: 4px solid #4f8ef7;
    min-height: 110px;
}
.kpi-card .label {
    color: #64748b;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-weight: 600;
}
.kpi-card .value {
    font-size: 30px;
    font-weight: 700;
    color: #1e293b;
    margin-top: 8px;
    line-height: 1.2;
}
.kpi-card .sub {
    color: #64748b;
    font-size: 12px;
    margin-top: 6px;
}

/* ── Chart panels ────────────────────────────────────────────── */
.chart-panel {
    background: #ffffff;
    border-radius: 12px;
    padding: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.gradio-plot {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

/* ── Insight panel ───────────────────────────────────────────── */
.insight-panel {
    background: #eff6ff;
    border-left: 4px solid #3b82f6;
    border-radius: 10px;
    padding: 16px 20px;
    margin: 10px 0;
}
.insight-panel h3,
.insight-panel h4 {
    margin-top: 0;
    color: #1d4ed8;
}
.insight-panel * {
    color: #1e293b !important;
}

/* ── LLM output panel ────────────────────────────────────────── */
.llm-output {
    background: #fffbeb;
    border-left: 4px solid #f59e0b;
    border-radius: 10px;
    padding: 16px 20px;
    margin-top: 10px;
}
.llm-output h3 {
    margin-top: 0;
    color: #92400e;
}
.llm-output * {
    color: #1e293b !important;
}

/* ── Buttons ─────────────────────────────────────────────────── */
button.primary,
.gr-button-primary {
    background: linear-gradient(135deg, #4f8ef7, #6366f1) !important;
    border: none !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
button.primary:hover,
.gr-button-primary:hover {
    background: linear-gradient(135deg, #3b7de8, #4f52d4) !important;
    box-shadow: 0 4px 12px rgba(79, 142, 247, 0.35) !important;
}

/* ── Tab navigation ──────────────────────────────────────────── */
.tab-nav,
div[class*="tab-nav"] {
    background: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    border-radius: 12px 12px 0 0;
    padding: 0 8px;
}

.tab-nav button,
.tabs > div > button,
div[class*="tab-nav"] button {
    color: #475569 !important;
    background: transparent !important;
    opacity: 1 !important;
    visibility: visible !important;
    font-size: 14px;
    font-weight: 500;
    padding: 10px 18px;
    border: none !important;
    border-bottom: 3px solid transparent !important;
    border-radius: 0 !important;
    transition: color 0.15s, border-color 0.15s, background 0.15s;
}

.tab-nav button:hover,
.tabs > div > button:hover,
div[class*="tab-nav"] button:hover {
    color: #4f8ef7 !important;
    background: #eff6ff !important;
    border-bottom-color: #bfdbfe !important;
}

.tab-nav button.selected,
.tabs > div > button.selected,
div[class*="tab-nav"] button.selected {
    color: #4f8ef7 !important;
    border-bottom: 3px solid #4f8ef7 !important;
    font-weight: 700;
    background: transparent !important;
}

/* ── Checkboxes / dropdowns inside filter bar ────────────────── */
.gradio-container input[type="checkbox"]:checked {
    accent-color: #4f8ef7;
}
"""
