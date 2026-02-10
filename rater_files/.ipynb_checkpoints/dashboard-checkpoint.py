from pathlib import Path
import pandas as pd
import plotly.express as px
from jinja2 import Template
import os

# Ask user for path
path_str = input("Enter File path: ").strip()

# Convert to Path object
path = Path(path_str)
# -----------------------------
# CONFIG
# -----------------------------
CSV_PATH = Path(os.path.join(path,'rated_policies.csv'))         # <-- change
OUT_HTML = Path(os.path.join(path,"dashboard.html"))

# -----------------------------
# LOAD
# -----------------------------
df = pd.read_csv(CSV_PATH)

# ---- basic cleaning / types (adjust if needed)
# Try parsing dates if present
for col in ["policyeffectivedate", "eff_dt"]:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

# Numeric columns we’ll use
for col in ["current_premium", "coll_loss", "exposure", "olp", "expenses"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Create loss ratio if possible
if "coll_loss" in df.columns and "current_premium" in df.columns:
    df["loss_ratio"] = (df["coll_loss"].fillna(0) / df["current_premium"].replace({0: pd.NA})).astype("float")

# -----------------------------
# KPIs
# -----------------------------
def safe_sum(s): 
    return float(pd.to_numeric(s, errors="coerce").fillna(0).sum())

def safe_mean(s):
    x = pd.to_numeric(s, errors="coerce")
    return float(x.dropna().mean()) if x.notna().any() else 0.0

kpis = {
    "Rows": f"{len(df):,}",
    "Policies (unique)": f"{df['policy'].nunique():,}" if "policy" in df.columns else "N/A",
    "Written Premium (sum)": f"{safe_sum(df['current_premium']):,.2f}" if "current_premium" in df.columns else "N/A",
    "Avg Premium": f"{safe_mean(df['current_premium']):,.2f}" if "current_premium" in df.columns else "N/A",
    "Avg Exposure": f"{safe_mean(df['exposure']):,.3f}" if "exposure" in df.columns else "N/A",
    "Avg Loss Ratio": f"{safe_mean(df['loss_ratio']):.1%}" if "loss_ratio" in df.columns else "N/A",
}

# -----------------------------
# CHARTS (Plotly)
# -----------------------------
charts = {}

# 1) Premium distribution
if "current_premium" in df.columns:
    fig = px.histogram(df, x="current_premium", nbins=40, title="Premium Distribution")
    fig.update_layout(margin=dict(l=12, r=12, t=55, b=12))
    charts["premium_hist"] = fig.to_html(full_html=False, include_plotlyjs="cdn")

# 2) Premium by State
if "state" in df.columns and "current_premium" in df.columns:
    tmp = df.groupby("state", as_index=False)["current_premium"].sum().sort_values("current_premium", ascending=False)
    fig = px.bar(tmp, x="state", y="current_premium", title="Total Premium by State")
    fig.update_layout(margin=dict(l=12, r=12, t=55, b=12))
    charts["premium_by_state"] = fig.to_html(full_html=False, include_plotlyjs=False)

# 3) Loss ratio trend by eym (YYYYMM)
if "eym" in df.columns and "loss_ratio" in df.columns:
    tmp = df.groupby("eym", as_index=False).agg(
        avg_lr=("loss_ratio", "mean"),
        premium=("current_premium", "sum") if "current_premium" in df.columns else ("loss_ratio", "size")
    ).sort_values("eym")
    fig = px.line(tmp, x="eym", y="avg_lr", markers=True, title="Average Loss Ratio by EYM")
    fig.update_layout(yaxis_tickformat=".0%", margin=dict(l=12, r=12, t=55, b=12))
    charts["lr_by_eym"] = fig.to_html(full_html=False, include_plotlyjs=False)

# 4) Premium by Vehicle Use
if "vehicle_use" in df.columns and "current_premium" in df.columns:
    tmp = df.groupby("vehicle_use", as_index=False)["current_premium"].sum().sort_values("current_premium", ascending=False)
    fig = px.bar(tmp, x="vehicle_use", y="current_premium", title="Total Premium by Vehicle Use")
    fig.update_layout(margin=dict(l=12, r=12, t=55, b=12))
    charts["premium_by_use"] = fig.to_html(full_html=False, include_plotlyjs=False)

# 5) Top Zipcodes by Premium
if "zipcode" in df.columns and "current_premium" in df.columns:
    tmp = df.groupby("zipcode", as_index=False)["current_premium"].sum().sort_values("current_premium", ascending=False).head(15)
    fig = px.bar(tmp, x="zipcode", y="current_premium", title="Top 15 Zipcodes by Total Premium")
    fig.update_layout(margin=dict(l=12, r=12, t=55, b=12))
    charts["premium_by_zip"] = fig.to_html(full_html=False, include_plotlyjs=False)

# -----------------------------
# TABLE PREVIEW
# -----------------------------
preview_cols = [c for c in [
    "policy", "state", "zipcode", "current_premium", "coll_loss", "loss_ratio", "exposure",
    "policyholder_age", "policyholder_sex", "vehicle_use", "vehicle_value", "eym"
] if c in df.columns]

preview_df = df[preview_cols].head(50).copy() if preview_cols else df.head(50).copy()

# Format loss ratio nicely if present
if "loss_ratio" in preview_df.columns:
    preview_df["loss_ratio"] = preview_df["loss_ratio"].map(lambda x: f"{x:.1%}" if pd.notna(x) else "")

table_html = preview_df.to_html(index=False, classes="table table-striped table-hover", border=0)

# -----------------------------
# HTML TEMPLATE (well-designed)
# -----------------------------
template = Template(r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{{ title }}</title>

  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">

  <style>
    :root{
      --bg: #0b1220;
      --card: rgba(255,255,255,.06);
      --border: rgba(255,255,255,.10);
      --text: rgba(255,255,255,.92);
      --muted: rgba(255,255,255,.70);
    }
    body{
      background:
        radial-gradient(1200px 800px at 20% 0%, rgba(124,58,237,.22), transparent 60%),
        radial-gradient(900px 600px at 90% 20%, rgba(56,189,248,.16), transparent 55%),
        var(--bg);
      color: var(--text);
      font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
    }
    .glass {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 18px;
      box-shadow: 0 10px 30px rgba(0,0,0,.25);
    }
    .kpi {
      padding: 16px 16px;
      border-radius: 16px;
      border: 1px solid var(--border);
      background: rgba(255,255,255,.05);
      height: 100%;
    }
    .kpi .label { color: var(--muted); font-size: .9rem; }
    .kpi .value { font-size: 1.45rem; font-weight: 750; }
    .section-title { font-weight: 750; }
    .table { color: var(--text); }
    .table thead th { color: var(--muted); border-color: var(--border); }
    .table td, .table th { border-color: var(--border); }
  </style>
</head>

<body>
  <header class="container py-4">
    <div class="d-flex flex-wrap align-items-end justify-content-between gap-3">
      <div>
        <h1 class="h3 mb-1">{{ title }}</h1>
        <div class="text-secondary" style="color: var(--muted) !important;">
          {{ subtitle }}
        </div>
      </div>
      <div class="text-secondary" style="color: var(--muted) !important;">
        Generated: {{ generated }}
      </div>
    </div>
  </header>

  <main class="container pb-5">
    <!-- KPI Cards -->
    <section class="glass p-4 mb-4">
      <h2 class="h5 section-title mb-3">Key Metrics</h2>
      <div class="row g-3">
        {% for k, v in kpis.items() %}
        <div class="col-12 col-md-4 col-lg-3">
          <div class="kpi">
            <div class="label">{{ k }}</div>
            <div class="value">{{ v }}</div>
          </div>
        </div>
        {% endfor %}
      </div>
    </section>

    <!-- Charts -->
    <section class="glass p-4 mb-4">
      <h2 class="h5 section-title mb-3">Charts</h2>

      <div class="row g-4">
        {% if charts.premium_hist %}
        <div class="col-12">
          {{ charts.premium_hist | safe }}
        </div>
        {% endif %}

        {% if charts.premium_by_state %}
        <div class="col-12 col-lg-6">
          {{ charts.premium_by_state | safe }}
        </div>
        {% endif %}

        {% if charts.lr_by_eym %}
        <div class="col-12 col-lg-6">
          {{ charts.lr_by_eym | safe }}
        </div>
        {% endif %}

        {% if charts.premium_by_use %}
        <div class="col-12 col-lg-6">
          {{ charts.premium_by_use | safe }}
        </div>
        {% endif %}

        {% if charts.premium_by_zip %}
        <div class="col-12 col-lg-6">
          {{ charts.premium_by_zip | safe }}
        </div>
        {% endif %}
      </div>
    </section>

    <!-- Table Preview -->
    <section class="glass p-4">
      <h2 class="h5 section-title mb-3">Data Preview (Top 50)</h2>
      <div class="table-responsive">
        {{ table_html | safe }}
      </div>
      <div class="mt-3" style="color: var(--muted); font-size: .9rem;">
        You can swap in pricing-specific visuals next: A/E by decile, lift curves, dislocation heatmaps, GLM vs GBM comparison, etc.
      </div>
    </section>
  </main>
</body>
</html>
""")

html = template.render(
    title="Personal Auto Pricing Dashboard",
    subtitle="Quick portfolio summary from CSV (HTML output)",
    generated=pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
    kpis=kpis,
    charts=charts,
    table_html=table_html,
)

OUT_HTML.write_text(html, encoding="utf-8")
print(f"✅ Wrote {OUT_HTML.resolve()}")
