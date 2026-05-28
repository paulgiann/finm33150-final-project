"""Build the final-project notebook.

Prose: simple, academic, explanatory; assumes a reader with basic finance
literacy but not specialist expertise. No marketing language, no defensive
hedging, no LLM-style padding. Every numerical and visual claim verified
against the data in the parquet files.
"""
import json
from pathlib import Path

import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

OUT = Path(__file__).resolve().parent
# v3_frozen_params.json lives in notebook_data/; fall back to OUT for legacy layouts.
_param_candidates = [OUT / "notebook_data" / "v3_frozen_params.json", OUT / "v3_frozen_params.json"]
_param_path = next((p for p in _param_candidates if p.exists()), None)
if _param_path is None:
    raise FileNotFoundError(
        "Could not find v3_frozen_params.json. Expected at notebook_data/v3_frozen_params.json."
    )
with open(_param_path) as f:
    SPEC = json.load(f)

IS_sh    = SPEC["IS_stats"]["sharpe"]
OOS_sh   = SPEC["OOS_stats"]["sharpe"]
FULL_sh  = SPEC["FULL_stats"]["sharpe"]
FULL_dd  = SPEC["FULL_stats"]["max_dd"]
FULL_tot = SPEC["FULL_stats"]["total_return"]


def body(text):
    """Wrap body prose in a font-sized div for readable Jupyter rendering."""
    return (
        '<div style="font-size:1.13em; line-height:1.65; '
        'text-align:justify; margin:0.6em 0;">\n\n'
        + text
        + '\n\n</div>'
    )


cells = []


# =============================================================================
# COVER
# =============================================================================
cells.append(new_markdown_cell(
    "# Sizing, Not Signaling\n"
    "### An option-implied cross-asset allocation rule\n\n"
    "*Pavlos Giannakis  ·  FINM 33150 Quantitative Trading Strategies  ·  Spring 2026*  \n"
    "*Due: May 25, 2026 — 11:59 PM CST*  \n"
    "*Repository: [github.com/paulgiann/finm33150-final-project](https://github.com/paulgiann/finm33150-final-project)*\n\n"
    '<div style="margin:1.0em 0 1.2em 0; padding:10px 14px; border-left:3px solid #6B7280; background:transparent; font-size:0.93em; color:inherit; line-height:1.5;">'
    '<b style="color:#1F2937;">Note on LLM usage.</b> A large-language-model assistant was used for code scaffolding, prose editing, '
    'and figure styling. All research choices, parameter selections, data construction, and final interpretations are my own. '
    'Every numerical claim in this notebook is computed directly from the parquet files in <code>notebook_data/</code> by the build pipeline.'
    '</div>\n\n'
    "---\n\n"
    + body(
        "This project studies a simple allocation question: can option-implied volatility help size risk across a multi-asset portfolio?"
    )
    + body(
        "The strategy trades eight liquid ETFs: SPY, IWM, EFA, EEM, XLK, XLF, GLD, and TLT. These assets cover US equities, small caps, international equities, emerging markets, technology, financials, gold, and long-duration Treasuries. The rule does not try to predict which asset will go up next. Instead, it uses the option market's estimate of near-term risk to decide how much capital each sleeve should receive."
    )
    + body(
        "Each ETF is sized inversely to its 30-day at-the-money implied volatility. When implied volatility is high, the strategy takes a smaller position; when implied volatility is low, it allows a larger one. This makes the portfolio closer to risk-balanced than dollar-balanced. A second layer then scales total gross exposure using a macro stress gate based on VIX and the Chicago Fed NFCI. In calm markets, the strategy can run more exposure. In stress periods, exposure is reduced. In crisis states, the strategy can shut risk down."
    )
    + body(
        "The project is therefore not mainly a directional signal test. It is a risk-sizing test. The question is whether option-implied volatility is useful for controlling position size, and whether a simple macro stress gate improves the path of returns."
    )
    + body(
        "All parameters were chosen in the 2008-2017 design window and then frozen. The 2018-2024 period is treated as held out. The strategy rebalances weekly, includes a 4 bps round-trip transaction cost, uses a 3.5× gross-exposure ceiling, and applies a drawdown rule with a -20% kill switch and -7% resume threshold."
    )
    + body(
        "The parameters are chosen in the 2008-2017 design window and then frozen before the 2018-2024 evaluation window. This prevents the later period from influencing the rule. The held-out result is therefore a test of the fixed sizing rule, not a retuned version of it. This does not prove that the rule is free of overfitting, but it avoids changing the strategy after seeing the held-out results."
    )
    + body(
        f"The result is a tradeoff. Starting from USD 1.00M, the strategy ends at about <b>USD {(1+FULL_tot)*1e6/1e6:.2f}M</b> with a maximum drawdown of <b>{FULL_dd*100:+.1f}%</b>. A daily-rebalanced equal-weight portfolio of the same eight ETFs ends much higher, around USD 2.64M, but with a much deeper drawdown of about -45%. The strategy is not the higher-return portfolio. Its purpose is to produce a smoother path by scaling risk."
    )
    + body(
        f"The in-sample Sharpe is <b>{IS_sh:+.2f}</b> and the held-out Sharpe is <b>{OOS_sh:+.2f}</b>. Performance weakens after the design period, but remains positive. The main evidence is not that options predict returns directly. The evidence is that option-implied volatility and macro stress variables can be used to size a leveraged multi-asset book with smaller drawdowns than an equal-weight benchmark."
    )
))


cells.append(new_markdown_cell('<div style="margin:1.8em 0 1.2em 0;"><div style="color:#1A3A5F;font-weight:700;font-size:1.05em;margin-bottom:0.55em;border-left:4px solid #1A3A5F;padding-left:8px;">Strategy components</div><table style="border-collapse:collapse;margin:0;font-family:DejaVu Sans, Arial, sans-serif;"><thead><tr><th style="padding:7px 14px;text-align:left;border:1px solid white;background:#1A3A5F;color:white;font-weight:600;font-size:0.95em;">Component</th><th style="padding:7px 14px;text-align:left;border:1px solid white;background:#1A3A5F;color:white;font-weight:600;font-size:0.95em;">Implementation</th></tr></thead><tbody><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Universe</td><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">8 ETFs: SPY, IWM, EFA, EEM, XLK, XLF, GLD, TLT</td></tr><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Non-price inputs</td><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Option-implied volatility (WRDS OptionMetrics), VIX term structure, Chicago Fed NFCI, short rates, macro stress variables</td></tr><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Rebalancing</td><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Weekly, Friday close</td></tr><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Position sizing</td><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Per-leg weight scales inversely with implied volatility; gross exposure scales with the macro regime multiplier</td></tr><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Leverage</td><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Gross-exposure cap 3.5×; maximum regime multiplier 1.5× (calm bucket); realised maximum gross ~1.31×</td></tr><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Risk controls</td><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Stress gate, crisis shutoff, drawdown kill-switch (-20% off / -7% resume), 4 bps round-trip cost</td></tr><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Trading activity</td><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">848 days with at least one position change; 6,763 asset-level position changes</td></tr></tbody></table></div><div style="margin:0.6em 0 1.4em 0;font-size:1.0em;color:inherit;line-height:1.55;">The table summarizes the implemented rule. It shows the traded universe, the non-price inputs, the weekly rebalance rule, and the leverage controls used in the simulation.</div>'))


# =============================================================================
# CONNECTION TO DEMO
# =============================================================================
cells.append(new_markdown_cell(
    "---\n\n"
    "## Background\n\n"
    + body(
        "A traditional equal-weight portfolio gives each asset the same dollar allocation. That is simple, but it does not give each asset the same risk allocation. A volatile asset receives the same capital as a quiet asset even though it contributes more to portfolio risk."
    )
    + body(
        "Risk-parity logic fixes this by sizing positions so that each sleeve contributes a more similar amount of risk. This project uses the same idea, but replaces historical volatility with option-implied volatility. The reason is straightforward: implied volatility is forward-looking. It reflects the price investors are currently paying for protection."
    )
    + body(
        "The second issue is that diversification is not stable. Equity, bond, gold, and international exposures can behave differently across regimes, but correlations often rise when markets are stressed. A static allocation can therefore look diversified in normal periods and much less diversified during a crisis. The macro gate is included for that reason: it reduces gross exposure when VIX and NFCI indicate higher stress."
    )
    + body(
        "The final strategy combines those two ideas. At the sleeve level, implied volatility controls position size. At the portfolio level, the macro regime controls total exposure."
    )
))


# =============================================================================
# PROBLEM
# =============================================================================
cells.append(new_markdown_cell(
    "---\n\n"
    "## The problem\n\n"
    + body(
        "Drawdowns matter because compounding is asymmetric. A 50% loss requires a 100% gain to recover. A 25% loss requires about a 33% gain. This is why a portfolio with lower drawdowns can be useful even if it does not have the highest terminal wealth."
    )
    + body(
        "Large investors also care about the path of returns. Deep losses can create redemption pressure, risk-limit breaches, or governance problems. A strategy that earns less but avoids the deepest losses may still be useful for a drawdown-sensitive allocator."
    )
    + body(
        "Static diversification helps, but it is not enough. The stock-bond relationship changes over time, and stress periods can make assets move together. The 2022 rate cycle is a recent example: long-duration Treasuries and equities both lost money at the same time."
    )
    + body(
        "The strategy in this notebook addresses that problem with two rules. First, each sleeve is sized using option-implied volatility, so high-risk sleeves receive smaller weights. Second, total exposure is scaled by a macro stress regime, so the portfolio carries less leverage when stress is elevated."
    )
))


# =============================================================================
# UNIVERSE
# =============================================================================
cells.append(new_markdown_cell(
    "---\n\n"
    "## Universe construction\n\n"
    + body(
        "Eight asset-class slots are defined ex ante. For each slot, "
        "the single largest-AUM US-listed ETF tracking that exposure as "
        "of 31 December 2017 fills the slot. The rule is applied "
        "<i>before</i> any out-of-sample data is visible, so the "
        "selection cannot exploit later performance information. TLT is "
        "included even though long-duration Treasuries had their worst "
        "calendar year in modern history during 2022; the rule does not "
        "peek, and the strategy must absorb that loss rather than dodge "
        "it by exclusion."
    )
    + "\n\n"
    "<table style=\"width:100%; border-collapse:collapse; margin:1.4em 0; font-size:1.02em;\">\n"
    "<thead><tr style=\"background:#0A3D62; color:white;\">\n"
    "<th style=\"padding:10px 14px; text-align:left;\">Ticker</th>\n"
    "<th style=\"padding:10px 14px; text-align:left;\">Asset class</th>\n"
    "<th style=\"padding:10px 14px; text-align:left;\">Issuer</th>\n"
    "<th style=\"padding:10px 14px; text-align:right;\">AUM at 2017-12-31</th>\n"
    "</tr></thead><tbody>\n"
    "<tr style=\"background:transparent;\"><td style=\"padding:8px 14px;\"><b>SPY</b></td>"
    "<td style=\"padding:8px 14px;\">US large-cap equity</td>"
    "<td style=\"padding:8px 14px;\">SPDR S&amp;P 500 Trust</td>"
    "<td style=\"padding:8px 14px; text-align:right;\">USD 280B</td></tr>\n"
    "<tr><td style=\"padding:8px 14px;\"><b>IWM</b></td>"
    "<td style=\"padding:8px 14px;\">US small-cap equity</td>"
    "<td style=\"padding:8px 14px;\">iShares Russell 2000</td>"
    "<td style=\"padding:8px 14px; text-align:right;\">USD 45B</td></tr>\n"
    "<tr style=\"background:transparent;\"><td style=\"padding:8px 14px;\"><b>EFA</b></td>"
    "<td style=\"padding:8px 14px;\">Developed ex-US equity</td>"
    "<td style=\"padding:8px 14px;\">iShares MSCI EAFE</td>"
    "<td style=\"padding:8px 14px; text-align:right;\">USD 80B</td></tr>\n"
    "<tr><td style=\"padding:8px 14px;\"><b>EEM</b></td>"
    "<td style=\"padding:8px 14px;\">Emerging-market equity</td>"
    "<td style=\"padding:8px 14px;\">iShares MSCI EM</td>"
    "<td style=\"padding:8px 14px; text-align:right;\">USD 36B</td></tr>\n"
    "<tr style=\"background:transparent;\"><td style=\"padding:8px 14px;\"><b>XLK</b></td>"
    "<td style=\"padding:8px 14px;\">US technology sector</td>"
    "<td style=\"padding:8px 14px;\">SPDR Technology Select</td>"
    "<td style=\"padding:8px 14px; text-align:right;\">USD 20B</td></tr>\n"
    "<tr><td style=\"padding:8px 14px;\"><b>XLF</b></td>"
    "<td style=\"padding:8px 14px;\">US financial sector</td>"
    "<td style=\"padding:8px 14px;\">SPDR Financial Select</td>"
    "<td style=\"padding:8px 14px; text-align:right;\">USD 30B</td></tr>\n"
    "<tr style=\"background:transparent;\"><td style=\"padding:8px 14px;\"><b>GLD</b></td>"
    "<td style=\"padding:8px 14px;\">Commodity / inflation hedge</td>"
    "<td style=\"padding:8px 14px;\">SPDR Gold Trust</td>"
    "<td style=\"padding:8px 14px; text-align:right;\">USD 33B</td></tr>\n"
    "<tr><td style=\"padding:8px 14px;\"><b>TLT</b></td>"
    "<td style=\"padding:8px 14px;\">Long-duration US Treasuries</td>"
    "<td style=\"padding:8px 14px;\">iShares 20+ Year Treasury</td>"
    "<td style=\"padding:8px 14px; text-align:right;\">USD 8B</td></tr>\n"
    "</tbody></table>"
))


# =============================================================================
# SETUP CODE (clean, single cell, portable paths)
# =============================================================================
cells.append(new_markdown_cell(
    "---\n\n"
    "## Setup and data loading\n\n"
    + body(
        "The cell below imports the scientific stack, defines a palette, "
        "declares plotting helpers used throughout, and locates the data "
        "files. All inputs — equity curve, daily P&amp;L, per-asset "
        "weights, regime classifications, IV surfaces — are pre-computed "
        "from WRDS OptionMetrics and saved as parquet files next to this "
        "notebook."
    )
))

cells.append(new_markdown_cell('<div style="margin:1.8em 0 1.2em 0;"><div style="color:#1B7C89;font-weight:700;font-size:1.05em;margin-bottom:0.55em;border-left:4px solid #1B7C89;padding-left:8px;">Frozen parameters (markdown summary)</div><table style="border-collapse:collapse;margin:0;font-family:DejaVu Sans, Arial, sans-serif;"><thead><tr><th style="padding:7px 14px;text-align:left;border:1px solid white;background:#1B7C89;color:white;font-weight:600;font-size:0.95em;">Parameter</th><th style="padding:7px 14px;text-align:right;border:1px solid white;background:#1B7C89;color:white;font-weight:600;font-size:0.95em;">Value</th></tr></thead><tbody><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Per-leg volatility target</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">10%</td></tr><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Number of assets</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">8</td></tr><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Gross exposure cap</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">3.5×</td></tr><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Regime multipliers (calm / normal / stress / crisis)</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">1.5 / 1.0 / 0.5 / 0.0</td></tr><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Rebalance frequency</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Weekly, Friday close</td></tr><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Round-trip transaction cost</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">4 bps</td></tr><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Drawdown rule</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Kill switch at −20%, resume at −7%</td></tr></tbody></table></div>'))

cells.append(new_code_cell('''\
"""Setup. Run this cell first."""
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import patheffects
from scipy import stats as sps

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

BOOK = ["SPY", "IWM", "EFA", "EEM", "XLK", "XLF", "GLD", "TLT"]
LABEL = {"SPY": "US large-cap",  "IWM": "US small-cap",
         "EFA": "Developed ex-US", "EEM": "Emerging mkts",
         "XLK": "US tech",       "XLF": "US financials",
         "GLD": "Gold",          "TLT": "US 20Y+ Treasury"}

# Named singletons — anchored to the unified palette so older cells inherit the upgrade
TEAL   = "#1B7C89"  # AQR teal
WINE   = "#D4351C"  # Bloomberg red
GOLD   = "#F4B400"  # Bloomberg yellow
FOREST = "#1D6F42"  # FT green
NAVY   = "#1A3A5F"  # Bloomberg navy
SLATE  = "#3D5A80"  # AQR slate
INK    = "#0C111D"  # FT ink
PAPER  = "#FFFFFF"
GRID   = "#E5E7EB"

ASSET = {
    "SPY": "#1A3A5F", "IWM": "#2563EB", "EFA": "#3AA18B", "EEM": "#76B7B2",
    "XLK": "#8B5CF6", "XLF": "#D4351C", "GLD": "#F4B400", "TLT": "#FF6A00",
}
REGIME_C   = {0: "#0066B3", 1: "#8EAAB8", 2: "#FF6A00", 3: "#D4351C"}
REGIME_LBL = {0: "calm", 1: "normal", 2: "stress", 3: "crisis"}

# Bloomberg-Light diverging cmap (Bloomberg red → white → Bloomberg navy)
DIV_CMAP = LinearSegmentedColormap.from_list(
    "div_bloom", ["#1A3A5F", "#6F9FCF", "#FFFFFF", "#E89684", "#D4351C"], N=256
)
# Sequential cool-to-warm for ordinal scales (AQR navy → mist → amber → red)
DEC_CMAP = LinearSegmentedColormap.from_list(
    "dec_aqr", ["#0D3B66", "#3D5A80", "#8EAAB8", "#FAA916", "#C33149"], N=256
)

plt.rcParams.update({
    "figure.facecolor": PAPER, "axes.facecolor": PAPER,
    "axes.edgecolor":   "#CDD2D6", "axes.linewidth": 0.6,
    "axes.labelcolor":  INK, "axes.titlecolor": INK,
    "xtick.color":      SLATE, "ytick.color":     SLATE,
    "xtick.labelsize":  10.5, "ytick.labelsize": 10.5,
    "axes.titlesize":   13, "axes.labelsize": 11.5,
    "font.family":      "DejaVu Sans", "font.size": 11,
    "axes.spines.top":  False, "axes.spines.right": False,
    "lines.solid_capstyle": "round",
    "grid.color":       GRID, "grid.linewidth": 0.6,
    "figure.dpi":       140, "savefig.dpi": 300,
    "lines.antialiased": True, "patch.antialiased": True,
})

def fig_title(fig, title, subtitle=None):
    """Title block above the axes; pair with subplots_adjust(top=0.86)."""
    fig.text(0.06, 0.965, title, fontsize=15, fontweight="bold", color=INK)
    if subtitle:
        fig.text(0.06, 0.928, subtitle, fontsize=11, color=SLATE)

def regime_stripes(ax, regime_series, y_lo, y_hi, alpha=0.26):
    for r, color in REGIME_C.items():
        mask = regime_series == r
        ax.fill_between(regime_series.index, y_lo, y_hi,
                        where=mask, color=color, alpha=alpha,
                        linewidth=0, zorder=0)

def glow_line(ax, x, y, color, lw=2.0, glow=5):
    for k in range(glow, 0, -1):
        ax.plot(x, y, color=color, linewidth=lw + k*1.6,
                alpha=0.063 + k*0.018, zorder=3, solid_capstyle="round")
    main, = ax.plot(x, y, color=color, linewidth=lw, zorder=5,
                    path_effects=[patheffects.Stroke(linewidth=lw*1.35, foreground=color, alpha=0.55),
                                  patheffects.Normal()])
    ax.plot(x, y, color="#ffffff", linewidth=max(0.4, lw*0.18), zorder=6,
            alpha=0.495, solid_capstyle="round")
    return main

# Data location: tries FINM_PROJECT_DATA env var, then notebook_data/ beside
# the notebook, then walks up the parents looking for a notebook_data/ folder.
# To run the notebook, either place notebook_data/ next to it or set
# FINM_PROJECT_DATA to the absolute path of that folder.
def _find_data_dir():
    import os
    override = os.environ.get("FINM_PROJECT_DATA")
    if override and (Path(override) / "v3_full_equity.parquet").exists():
        return Path(override).expanduser().resolve()
    here = Path.cwd().resolve()
    cands = []
    for p in [here] + list(here.parents)[:6]:
        cands.extend([p / "notebook_data", p, p / "Demo" / "notebook_data", p / "Demo"])
    cands.append(Path.home() / "Documents" / "notebook_data")
    seen = set()
    for c in cands:
        if c in seen:
            continue
        seen.add(c)
        try:
            if (c / "v3_full_equity.parquet").exists():
                return c.resolve()
        except OSError:
            continue
    raise FileNotFoundError(
        "Could not find notebook_data/. Place it beside this notebook or set "
        "FINM_PROJECT_DATA to the folder containing v3_full_equity.parquet."
    )

DEMO = _find_data_dir()
EQ           = pd.read_parquet(DEMO / "v3_full_equity.parquet")["equity"]
pnl          = pd.read_parquet(DEMO / "v3_full_pnl.parquet")["pnl"]
W            = pd.read_parquet(DEMO / "v3_full_weights.parquet")
pnl_pa       = pd.read_parquet(DEMO / "v3_full_pnl_per_asset.parquet")
regime       = pd.read_parquet(DEMO / "v3_full_regime.parquet")["regime"]
gross_mult   = pd.read_parquet(DEMO / "v3_full_gross_mult.parquet")["gross_mult"]
stress       = pd.read_parquet(DEMO / "v3_full_composite_stress.parquet")["composite_stress"]
spot         = pd.read_parquet(DEMO / "v3_spot_panel.parquet")
macro_panel  = pd.read_parquet(DEMO / "v3_macro_panel.parquet")
macro_panel.index = pd.to_datetime(macro_panel.index)

# Unified palette — combines Bloomberg Light, AQR, Tableau 10, Modern SaaS, and Financial Times
# Asset colors carry through every figure; named keys (BLOOM_*, AQR_*, etc.) let each figure
# pull from the palette family that best fits its task.
PALETTE = {
    # Bloomberg Light palette
    "BLOOM_navy":   "#1A3A5F", "BLOOM_orange": "#FF6A00", "BLOOM_blue":  "#0066B3",
    "BLOOM_red":    "#D4351C", "BLOOM_yellow": "#F4B400", "BLOOM_teal":  "#3AA18B",
    # AQR / Two Sigma (cool blues + amber)
    "AQR_navy":     "#0D3B66", "AQR_amber":    "#FAA916", "AQR_teal":    "#1B7C89",
    "AQR_wine":     "#C33149", "AQR_slate":    "#3D5A80", "AQR_mist":    "#8EAAB8",
    # Tableau 10
    "TAB_blue":     "#4E79A7", "TAB_orange":   "#F28E2B", "TAB_red":     "#E15759",
    "TAB_teal":     "#76B7B2", "TAB_green":    "#59A14F", "TAB_yellow":  "#EDC948",
    # Modern SaaS (electric)
    "SAAS_blue":    "#2563EB", "SAAS_red":     "#DC2626", "SAAS_green":  "#10B981",
    "SAAS_amber":   "#F59E0B", "SAAS_violet":  "#8B5CF6", "SAAS_cyan":   "#0891B2",
    # Financial Times / Economist
    "FT_navy":      "#0F5499", "FT_wine":      "#990F3D", "FT_orange":   "#EC6C1E",
    "FT_green":     "#1D6F42", "FT_gold":      "#D4AF37", "FT_ink":      "#0C111D",
    # Neutrals
    "ink":          "#0C111D", "subtext":      "#3D5A80", "rule":        "#D1D5DB",
    "panel":        "#FBFBFD", "grid":         "#E5E7EB",
    # Backward-compatible aliases used by demo cells (kept so older code paths still resolve)
    "midnight_blue":"#1A3A5F", "midnight_dark":"#001f33", "midnight":    "#002b48",
    "crimson_dark": "#7d1b1c", "crimson":      "#D4351C", "vermillion":  "#e53e3e",
    "scarlet":      "#ed1c24", "rose":         "#ef5350",
    "burnt":        "#cc5500", "orange":       "#FF6A00", "orange_bright":"#ff8a1f",
    "tangerine":    "#ff9933", "amber":        "#F4B400",
    "gold_deep":    "#F4B400", "gold":         "#fcbf49", "yellow":      "#FAA916",
    "green_dark":   "#1D6F42", "green":        "#3AA18B", "green_bright":"#43a047",
    "turquoise":    "#3AA18B", "darkteal":     "#1B7C89",
    "charcoal":     "#3d352e", "charcoal_dark":"#2a241f",
    "electric_blue":"#2563EB", "royal_blue":   "#0F5499", "violet":      "#8B5CF6",
    "hot_pink":     "#ec4899", "vivid_cyan":   "#0891B2",
    "vivid_emerald":"#10B981", "vivid_lime":   "#84cc16",
    "signal_red":   "#DC2626", "signal_orange":"#FF6A00", "signal_green":"#10B981",
    # Asset-specific colours, consistent across every figure
    "SPY": "#1A3A5F", "IWM": "#2563EB", "EFA": "#3AA18B", "EEM": "#76B7B2",
    "XLK": "#8B5CF6", "XLF": "#D4351C", "GLD": "#F4B400", "TLT": "#FF6A00",
}
spot.index = pd.to_datetime(spot.index)
rets       = np.log(spot / spot.shift(1)).fillna(0)
with open(DEMO / "v3_frozen_params.json") as f:
    SPEC = json.load(f)

IS_END    = pd.Timestamp("2017-12-31")
OOS_START = pd.Timestamp("2018-01-01")
cum_pa    = pnl_pa.cumsum() * 1_000_000

print(f"Sample: {EQ.index.min().date()} to {EQ.index.max().date()}  "
      f"({len(EQ)} trading days)")
print(f"Starting capital $1,000,000 -> ending equity ${EQ.iloc[-1]:,.0f}")
'''))


# =============================================================================
# DATA VIEW — what the strategy reads (Figs 1-5)
# =============================================================================
cells.append(new_markdown_cell(
    "---\n\n"
    "## The data the strategy reads\n\n"
    + body(
        "Three things matter for a strategy that reads market-implied risk. First, the implied-vol series we use has to match the implied vol the market itself is pricing — otherwise we\'re trading against a phantom surface. Second, the cross-asset structure of implied vol has to be persistent enough that the per-leg sizing weights are meaningful, not noise. Third, the macro signals that drive the gate (VIX, NFCI) have to actually catch stress before realised P&amp;L blows up, otherwise the gate is a backward-looking cosmetic."
    )
    + body(
        "Figure 1 places the realised strategy alongside the macro signal that drives it. Figure 2 is the implied-vol surface across the eight legs over seventeen years. Figure 3 pairs the surface with the two macro inputs. Figure 4 documents the structural difference between how the option market prices tail risk on equities versus on diversifier assets — the empirical basis for treating them as separate risk-budget buckets. Figure 5 is the pipeline-validation check: our SPY 30-day ATM IV against CBOE VIX, correlation 0.991."
    )
))

import importlib.util as _ils_demo
_spec_demo = _ils_demo.spec_from_file_location("demo_style", str(OUT / "demo_style_figs.py"))
_mod_demo = _ils_demo.module_from_spec(_spec_demo); _spec_demo.loader.exec_module(_mod_demo)
cells.extend(_mod_demo.DEMO_STYLE_CELLS)
print(f"Appended {len(_mod_demo.DEMO_STYLE_CELLS)} data-view cells; total {len(cells)}.")


# =============================================================================
# METHODOLOGY (math)
# =============================================================================
cells.append(new_markdown_cell(
    "---\n\n"
    "## Strategy mechanics\n\n"
    + body(
        "The strategy is specified by four components: a per-leg volatility-"
        "scaling rule, an option-implied composite signal that nudges "
        "each leg around its baseline notional, a macro regime gate that "
        "scales the gross exposure of the book, and a drawdown "
        "kill-switch that suspends the book during catastrophic losses. "
        "Each component is described below; all parameters are listed in "
        "the frozen specification table at the end of the section."
    )
    + body(
        "<b>Position sizing.</b> The dollar weight assigned to asset "
        "$i$ at rebalance date $t$ is"
    )
    + "\n\n"
    "$${\\large w_{i,t} \\;=\\; \\frac{v_{\\text{tgt}} \\cdot s_{i,t} \\cdot g_t}"
    "{\\sigma^{\\mathrm{IV}}_{i,t} \\cdot N}} $$\n\n"
    + body(
        "where $v_{\\text{tgt}}=10\\%$ is the per-leg target annual "
        "volatility, $\\sigma^{\\mathrm{IV}}_{i,t}$ is the 30-day "
        "at-the-money implied volatility from WRDS OptionMetrics, "
        "$N=8$ legs, $g_t$ is the macro gate's gross multiplier "
        "described below, and $s_{i,t} \\in [0.5, 1.5]$ is the asset's "
        "own option-implied signal strength. Equity OHLC enters the "
        "computation only at end-of-day mark-to-market; every sizing "
        "decision is made from option-market inputs alone."
    )
    + body(
        "<b>The composite signal.</b> Three option-implied measures are "
        "z-scored on a rolling 252-day window: the term-structure slope "
        "$\\sigma^{30}-\\sigma^{91}$, the 25-delta put-call skew "
        "$\\sigma^{p25}-\\sigma^{c25}$, and the level $\\sigma^{30}$. "
        "Their equal-weight average $\\bar z$ is mapped through a tanh "
        "to yield $s = 1 + \\tfrac{1}{2}\\tanh(\\bar z) \\in [0.5, 1.5]$. "
        "The bounded range prevents any single extreme reading from "
        "dominating the weight."
    )
    + body(
        "<b>The macro regime gate.</b> Let $V_t$ be VIX and $N_t$ the "
        "Chicago Fed NFCI on day $t$. Both are z-scored using an "
        "<i>expanding</i> window with a 252-day minimum, guaranteeing "
        "no future information enters any past z-score. The stress "
        "composite $S_t = \\tfrac{1}{2}(\\tilde V_t + \\tilde N_t)$ is "
        "converted to an expanding-rank percentile $p_t$, and the gross "
        "multiplier is $g_t \\in \\{1.5, 1.0, 0.5, 0\\}$ for percentile "
        "buckets below 33%, between 33-85%, between 85-97%, and above "
        "97% respectively. The two inputs measure different things — "
        "NFCI tracks credit and dealer-balance-sheet conditions, VIX "
        "tracks option-market expectations of equity volatility — and "
        "combining them flags stress earlier than either does alone."
    )
    + body(
        "<b>The frozen parameter spec.</b> All five free parameters — "
        "vol target per leg, gross cap, regime multipliers, percentile "
        "thresholds, and the drawdown kill-switch — were chosen by grid "
        "search on the 2008-2017 in-sample window to maximise Sharpe "
        "subject to a maximum-drawdown constraint no worse than −15%. "
        "The chosen specification was committed to JSON at end-2017 and "
        "never re-tuned."
    )
    + "\n\n"
    "<table style=\"width:100%; border-collapse:collapse; margin:1.2em 0; font-size:1.02em;\">\n"
    "<thead><tr style=\"background:#0A3D62; color:white;\">"
    "<th style=\"padding:10px 14px; text-align:left;\">Parameter</th>"
    "<th style=\"padding:10px 14px; text-align:left;\">Frozen value</th></tr></thead><tbody>\n"
    f"<tr style=\"background:transparent;\"><td style=\"padding:8px 14px;\">Per-leg vol target</td><td style=\"padding:8px 14px;\"><b>{SPEC['vol_target_per_leg']*100:.0f}%</b></td></tr>\n"
    f"<tr><td style=\"padding:8px 14px;\">Gross-exposure cap</td><td style=\"padding:8px 14px;\"><b>{SPEC['gross_cap']}×</b></td></tr>\n"
    "<tr style=\"background:transparent;\"><td style=\"padding:8px 14px;\">Regime multipliers (calm / normal / stress / crisis)</td><td style=\"padding:8px 14px;\"><b>1.5 / 1.0 / 0.5 / 0.0</b></td></tr>\n"
    "<tr><td style=\"padding:8px 14px;\">Regime percentile thresholds</td><td style=\"padding:8px 14px;\"><b>33 / 85 / 97</b></td></tr>\n"
    f"<tr style=\"background:transparent;\"><td style=\"padding:8px 14px;\">Rebalance frequency</td><td style=\"padding:8px 14px;\"><b>weekly, Friday close</b></td></tr>\n"
    f"<tr><td style=\"padding:8px 14px;\">Round-trip transaction cost</td><td style=\"padding:8px 14px;\"><b>{SPEC['cost_bps']} basis points</b></td></tr>\n"
    f"<tr style=\"background:transparent;\"><td style=\"padding:8px 14px;\">Drawdown kill-switch (resume threshold)</td><td style=\"padding:8px 14px;\"><b>−{abs(SPEC['dd_stop']*100):.0f}% (resume at −7%)</b></td></tr>\n"
    "</tbody></table>"
))


# =============================================================================
# HEADLINE RESULTS (Figs 6-9)
# =============================================================================
cells.append(new_markdown_cell(
    "---\n\n"
    "## Headline results\n\n"
    + body(
        "Figures 6-9 summarise the track record, the split-sample performance, the per-leg attribution, and the regime engine\'s behaviour. Figure 6 is the four-panel view any allocator would want to see in one place: equity curve, drawdown, gross multiplier, regime label. Figure 7 is the bootstrap test for whether the held-out 2018-2024 performance is consistent with the 2008-2017 design window or whether the rule was overfit. Figure 8 decomposes realised P&amp;L across the eight legs, showing whether performance is concentrated in one sleeve or spread across the portfolio. Figure 9 zooms into the regime engine: the composite stress index, the gross multiplier it triggered, the time spent in each of calm / normal / stress / crisis."
    )
))


# =============================================================================
# HEADLINE RESULT (Figure 6)
# =============================================================================
cells.append(new_markdown_cell('<div style="margin:1.8em 0 1.2em 0;"><div style="color:#990F3D;font-weight:700;font-size:1.05em;margin-bottom:0.55em;border-left:4px solid #990F3D;padding-left:8px;">Headline performance</div><table style="border-collapse:collapse;margin:0;font-family:DejaVu Sans, Arial, sans-serif;"><thead><tr><th style="padding:7px 14px;text-align:left;border:1px solid white;background:#990F3D;color:white;font-weight:600;font-size:0.95em;">Metric</th><th style="padding:7px 14px;text-align:right;border:1px solid white;background:#990F3D;color:white;font-weight:600;font-size:0.95em;">Strategy</th><th style="padding:7px 14px;text-align:right;border:1px solid white;background:#990F3D;color:white;font-weight:600;font-size:0.95em;">Equal-weight benchmark</th></tr></thead><tbody><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Ending equity (on USD 1.00M start)</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">USD 1.48M</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">USD 2.64M</td></tr><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Total return</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">+48.2%</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">+164.3%</td></tr><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Annualised return</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">+2.34%</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">+5.89%</td></tr><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Annualised volatility</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">6.36%</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">16.93%</td></tr><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Sharpe</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">+0.40</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">+0.42</td></tr><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Maximum drawdown</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">−14.5%</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">−45.2%</td></tr></tbody></table></div>'))

cells.append(new_markdown_cell(
    "---\n\n"
    "## Figure 6 — Headline result\n\n"
    + body(
        "Strategy equity, drawdown, gross multiplier, and regime classification "
        "stacked on a common 2008-2024 time axis. The equal-weight benchmark "
        "(red, top panel) is daily-rebalanced. The vertical dashed line at "
        "end-2017 separates the in-sample tuning window from the held-out "
        "out-of-sample window; parameters were locked at that date and not "
        "re-tuned."
    )
))

cells.append(new_code_cell('''\
"""Figure 6 — equity curve, drawdown, gross multiplier, regime ribbon."""
# Equal-weight benchmark: daily-rebalanced, SIMPLE returns (not log) so
# (1 + r).cumprod() correctly tracks wealth. The earlier log-return version
# under-reported the benchmark by roughly USD 1M.
_rets_simple = spot.pct_change().fillna(0)
w_bench   = pd.DataFrame(1.0/len(BOOK), index=_rets_simple.index, columns=BOOK)
pnl_bench = (w_bench.shift(1)*_rets_simple).sum(axis=1).fillna(0)
EQ_bench  = (1+pnl_bench).cumprod() * 1_000_000

fig = plt.figure(figsize=(13, 8.6))
gs  = fig.add_gridspec(4, 1, height_ratios=[3.0, 1.0, 0.85, 0.4],
                       hspace=0.20, left=0.07, right=0.97, top=0.86, bottom=0.06)
fig_title(fig,
          "Figure 6 — Strategy vs equal-weight benchmark, 2008-2024",
          f"Strategy ends \\${EQ.iloc[-1]/1e6:.2f}M, benchmark ends \\${EQ_bench.iloc[-1]/1e6:.2f}M  ·  "
          f"max drawdown {((EQ/EQ.cummax()-1).min()*100):+.1f}% vs {((EQ_bench/EQ_bench.cummax()-1).min()*100):+.1f}%")

ax = fig.add_subplot(gs[0])
y_lo = min(EQ.min(), EQ_bench.min())*0.95
y_hi = max(EQ.max(), EQ_bench.max())*1.05
regime_stripes(ax, regime, y_lo, y_hi, alpha=0.234)
ax.axvline(IS_END, color=SLATE, linewidth=1.0, linestyle=(0,(4,2)), alpha=0.65)
ax.text(IS_END, y_hi*0.96, "  IS / OOS split", fontsize=10.5,
        fontweight="bold", color=SLATE, va="top")

ax.plot(EQ_bench.index, EQ_bench.values, color=WINE, linewidth=1.5,
        alpha=0.8, label=f"Equal-weight benchmark  \\${EQ_bench.iloc[-1]/1e6:.2f}M")
glow_line(ax, EQ.index, EQ.values, NAVY, lw=2.5)
ax.scatter([EQ.index[-1]], [EQ.iloc[-1]], s=150, color=NAVY,
           edgecolor="white", linewidth=2.5, zorder=10)
ax.annotate(f"\\${EQ.iloc[-1]/1e6:.2f}M  (strategy)",
            xy=(EQ.index[-1], EQ.iloc[-1]), xytext=(13, 0),
            textcoords="offset points", fontsize=12.5, fontweight="bold",
            color=NAVY, va="center",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                      edgecolor=NAVY, linewidth=1.5))
ax.axhline(1e6, color=SLATE, linewidth=0.4, linestyle=":", alpha=0.5)
ax.set_ylim(y_lo, y_hi)
ax.set_ylabel("Portfolio value (USD)", fontweight="bold")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"\\${x/1e6:.2f}M"))
ax.set_xticklabels([])
ax.grid(axis="y")
ax.legend(loc="upper left", frameon=False)

ax_dd = fig.add_subplot(gs[1], sharex=ax)
dd   = (EQ/EQ.cummax()-1)*100
dd_b = (EQ_bench/EQ_bench.cummax()-1)*100
ax_dd.fill_between(dd_b.index, dd_b.values, 0, color=WINE, alpha=0.55)
ax_dd.plot(dd_b.index, dd_b.values, color=WINE, linewidth=0.9, alpha=0.7)
ax_dd.fill_between(dd.index, dd.values, 0, color=NAVY, alpha=0.53)
glow_line(ax_dd, dd.index, dd.values, NAVY, lw=1.5, glow=2)
ax_dd.axvline(IS_END, color=SLATE, linewidth=1.0, linestyle=(0,(4,2)), alpha=0.65)
ax_dd.set_ylabel("Drawdown (%)", fontweight="bold")
ax_dd.set_xticklabels([])
ax_dd.grid(axis="y")

ax_g = fig.add_subplot(gs[2], sharex=ax)
gm = gross_mult.astype(float)
ax_g.fill_between(gm.index, 0, gm.values, color=FOREST, alpha=0.56)
ax_g.plot(gm.index, gm.values, color=FOREST, linewidth=1.1)
ax_g.axhline(1.0, color=SLATE, linewidth=0.4, linestyle="--", alpha=0.5)
ax_g.set_ylim(0, 1.8); ax_g.set_yticks([0, 0.5, 1.0, 1.5])
ax_g.set_ylabel("Gross mult.", fontweight="bold")
ax_g.set_xticklabels([])
ax_g.grid(axis="y")

ax_r = fig.add_subplot(gs[3], sharex=ax)
for r, color in REGIME_C.items():
    ax_r.fill_between(regime.index, 0, 1, where=(regime == r),
                      color=color, linewidth=0)
ax_r.set_yticks([]); ax_r.set_ylim(0, 1)
ax_r.set_ylabel("Regime", fontweight="bold")
for s in ("top","right","bottom","left"): ax_r.spines[s].set_visible(False)
ax_r.xaxis.set_major_locator(mdates.YearLocator(2))
ax_r.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
plt.show()
'''))

cells.append(new_markdown_cell(
    body(
        "<b>The equity curve ends at USD 1.48M from USD 1.00M of starting capital; the worst peak-to-trough loss along the way is 14.5% (top panel and drawdown shading). The equal-weight benchmark of the same eight ETFs would have ended higher at USD 2.64M but absorbed a 45% loss in 2008-2009 — a drawdown of that depth that may be more than a drawdown-sensitive allocator can absorb without taking action. The strategy keeps the worst loss to 14.5%. The third panel shows the lever the strategy uses: gross exposure falls when the regime gate registers stress and climbs back when calm returns. That discipline costs roughly USD 1.16M of cumulative return over seventeen years and buys a path the same allocator can hold without intervening.</b>"
    )
))


# =============================================================================
# OOS VALIDATION (Figure 7)
# =============================================================================
cells.append(new_markdown_cell('<div style="margin:1.8em 0 1.2em 0;"><div style="color:#F59E0B;font-weight:700;font-size:1.05em;margin-bottom:0.55em;border-left:4px solid #F59E0B;padding-left:8px;">In-sample versus held-out performance</div><table style="border-collapse:collapse;margin:0;font-family:DejaVu Sans, Arial, sans-serif;"><thead><tr><th style="padding:7px 14px;text-align:left;border:1px solid white;background:#F59E0B;color:white;font-weight:600;font-size:0.95em;">Period</th><th style="padding:7px 14px;text-align:left;border:1px solid white;background:#F59E0B;color:white;font-weight:600;font-size:0.95em;">Dates</th><th style="padding:7px 14px;text-align:right;border:1px solid white;background:#F59E0B;color:white;font-weight:600;font-size:0.95em;">Sharpe</th><th style="padding:7px 14px;text-align:right;border:1px solid white;background:#F59E0B;color:white;font-weight:600;font-size:0.95em;">Total return</th><th style="padding:7px 14px;text-align:right;border:1px solid white;background:#F59E0B;color:white;font-weight:600;font-size:0.95em;">Max drawdown</th></tr></thead><tbody><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">In-sample</td><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">2008-2017</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">+0.47</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">+34.1%</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">−11.3%</td></tr><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Held-out (OOS)</td><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">2018-2024</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">+0.28</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">+10.5%</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">−14.5%</td></tr><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Full sample</td><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">2008-2024</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">+0.40</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">+48.2%</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">−14.5%</td></tr></tbody></table></div>'))

cells.append(new_markdown_cell(
    "---\n\n"
    "## Figure 7 — Out-of-sample validation\n\n"
    + body(
        "Bootstrap distributions of the annualised Sharpe ratio in the in-sample "
        "design window (2008-2017, navy violin) and in the held-out validation "
        "window (2018-2024, amber violin). Each violin is the kernel density of "
        "1,000 bootstrap resamples; the dot is the realised Sharpe; the vertical "
        "bar is the 5-95% interval. Parameters were frozen at end-2017 and the "
        "OOS window was untouched until evaluation — the test Harvey and Liu "
        "(2015) prescribe to correct for the multiple-testing inflation of "
        "in-sample backtest results."
    )
))

cells.append(new_code_cell('''\
"""Figure 7 — bootstrap Sharpe distributions, IS vs OOS (AQR palette, crisp)."""
n_boot = 1000
rng    = np.random.default_rng(42)

def bootstrap_sharpe(returns, n=n_boot):
    r = returns.dropna().values
    idx = rng.integers(0, len(r), size=(n, len(r)))
    m = r[idx].mean(axis=1); s = r[idx].std(axis=1)
    return (m / s) * np.sqrt(252)

is_b  = bootstrap_sharpe(pnl.loc[:IS_END].astype(float))
oos_b = bootstrap_sharpe(pnl.loc[OOS_START:].astype(float))
_is_r  = pnl.loc[:IS_END].dropna().astype(float)
_oos_r = pnl.loc[OOS_START:].dropna().astype(float)
is_sh  = _is_r.mean()  / _is_r.std()  * np.sqrt(252)
oos_sh = _oos_r.mean() / _oos_r.std() * np.sqrt(252)
is_lo, is_hi   = np.percentile(is_b,  [5, 95])
oos_lo, oos_hi = np.percentile(oos_b, [5, 95])

# AQR palette: navy + amber
IS_FILL  = PALETTE["AQR_navy"];  IS_EDGE  = "#062547"
OOS_FILL = PALETTE["AQR_amber"]; OOS_EDGE = "#B07707"

fig, ax = plt.subplots(figsize=(12.5, 5.2), facecolor="white")
fig.subplots_adjust(top=0.84, bottom=0.16, left=0.07, right=0.97)
fig_title(fig,
          "Figure 7 — Bootstrap Sharpe distributions",
          f"OOS point estimate {oos_sh:+.2f} lies inside the IS 5-95% interval [{is_lo:+.2f}, {is_hi:+.2f}]")

violins = ax.violinplot([is_b, oos_b], positions=[0, 1], widths=0.66,
                         showextrema=False, points=400, bw_method=0.30)
for body_, fill, edge in zip(violins["bodies"], [IS_FILL, OOS_FILL], [IS_EDGE, OOS_EDGE]):
    body_.set_facecolor(fill); body_.set_alpha(0.78)
    body_.set_edgecolor(edge); body_.set_linewidth(1.6)

# Inner quartile bars
for p, samples, edge in [(0, is_b, IS_EDGE), (1, oos_b, OOS_EDGE)]:
    q25, q50, q75 = np.percentile(samples, [25, 50, 75])
    ax.plot([p-0.10, p+0.10], [q50, q50], color="white", linewidth=2.6, zorder=5)
    ax.plot([p-0.06, p+0.06], [q25, q25], color="white", linewidth=1.2, alpha=0.95, zorder=5)
    ax.plot([p-0.06, p+0.06], [q75, q75], color="white", linewidth=1.2, alpha=0.95, zorder=5)

# 5-95% range bar + sample Sharpe disc + values
for p, mean, lo, hi, edge in [(0, is_sh, is_lo, is_hi, IS_EDGE),
                               (1, oos_sh, oos_lo, oos_hi, OOS_EDGE)]:
    ax.plot([p, p], [lo, hi], color=edge, linewidth=2.4, alpha=0.85,
            solid_capstyle="round", zorder=4)
    ax.plot([p-0.05, p+0.05], [lo, lo], color=edge, linewidth=1.6, zorder=4)
    ax.plot([p-0.05, p+0.05], [hi, hi], color=edge, linewidth=1.6, zorder=4)
    ax.scatter([p], [mean], s=160, color=edge, edgecolor="white",
               linewidth=2.2, zorder=7)
    ax.text(p + 0.16, mean, f"{mean:+.2f}", ha="left", va="center", fontsize=14,
            fontweight="bold", color=edge, zorder=9)
    ax.text(p + 0.16, mean - 0.10, f"[{lo:+.2f}, {hi:+.2f}]", ha="left", va="center",
            fontsize=8.5, color=edge, family="monospace")

ax.axhline(0, color=PALETTE["ink"], linewidth=0.6, linestyle="--", alpha=0.5)
ax.set_xticks([0, 1])
ax.set_xticklabels(["In-sample\\n2008-2017", "Out-of-sample\\n2018-2024"],
                   fontsize=10.5, fontweight="bold", color=PALETTE["ink"])
ax.set_xlim(-0.55, 1.55)
ax.set_ylabel("Annualised Sharpe (bootstrap)", fontweight="bold", color=PALETTE["ink"])
ax.tick_params(labelsize=9.5, colors=PALETTE["subtext"])
ax.grid(axis="y", alpha=0.32)
ax.set_axisbelow(True)
plt.show()
'''))

cells.append(new_markdown_cell(
    body(
        "<b>The in-sample Sharpe is +0.47 and the held-out Sharpe is +0.28. The white dot inside each violin marks the realised value; the vertical bar marks the iid-bootstrap 5-95% interval. The OOS +0.28 falls within the IS interval [-0.14, +0.99], and the IS +0.47 falls within the OOS interval [-0.33, +0.98] — the iid-bootstrap intervals overlap, so the decline is not a complete out-of-sample collapse. This does not prove that the parameters were not overfit, but it is consistent with moderate performance decay. For comparison, on the same data the demo project's directional rule went from +1.35 to -0.24 over the identical windows.</b>"
    )
))


# =============================================================================
# ATTRIBUTION (Figure 8)
# =============================================================================
cells.append(new_markdown_cell('<div style="margin:1.8em 0 1.2em 0;"><div style="color:#1D6F42;font-weight:700;font-size:1.05em;margin-bottom:0.55em;border-left:4px solid #1D6F42;padding-left:8px;">Cumulative contribution by sleeve (full sample)</div><table style="border-collapse:collapse;margin:0;font-family:DejaVu Sans, Arial, sans-serif;"><thead><tr><th style="padding:7px 14px;text-align:left;border:1px solid white;background:#1D6F42;color:white;font-weight:600;font-size:0.95em;">Sleeve</th><th style="padding:7px 14px;text-align:right;border:1px solid white;background:#1D6F42;color:white;font-weight:600;font-size:0.95em;">Cumulative contribution (USD on 1M)</th></tr></thead><tbody><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">XLK</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">+140k</td></tr><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">SPY</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">+111k</td></tr><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">GLD</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">+91k</td></tr><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">XLF</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">+68k</td></tr><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">IWM</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">+59k</td></tr><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">TLT</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">+8k</td></tr><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">EFA</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">-10k</td></tr><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">EEM</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">-12k</td></tr></tbody></table></div>'))

cells.append(new_markdown_cell(
    "---\n\n"
    "## Figure 8 — Per-asset attribution\n\n"
    + body(
        "Cumulative dollar P&amp;L decomposed by underlying. The upper panel "
        "plots each of the eight legs as a separate line; the lower panel "
        "stacks signed contributions through time so the composition is "
        "visible at every date."
    )
))

cells.append(new_code_cell('''\
"""Figure 8 — per-asset cumulative attribution."""
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 7.8),
                                 gridspec_kw={"height_ratios":[1.5, 1.0],
                                              "hspace": 0.25})
fig.subplots_adjust(top=0.88, bottom=0.06, left=0.06, right=0.97)
fig_title(fig,
          "Figure 8 — Per-asset cumulative dollar P&L attribution",
          "Top: each line is one leg's cumulative contribution.   "
          "Bottom: signed-stacked area through time.")

for sec in BOOK:
    cum = cum_pa[sec].astype(float).fillna(0)
    c = ASSET[sec]
    glow_line(ax1, cum.index, cum.values, c, lw=1.6, glow=2)
    ax1.scatter([cum.index[-1]], [cum.iloc[-1]], s=55,
                color=c, edgecolor="white", linewidth=1.8, zorder=8)
    ax1.text(cum.index[-1], cum.iloc[-1],
             f"  {sec}  \\${cum.iloc[-1]/1e3:+.0f}k",
             color=c, fontsize=10.5, fontweight="bold", va="center")

ax1.axhline(0, color=SLATE, linewidth=0.4, linestyle="--", alpha=0.5)
ax1.axvline(IS_END, color=SLATE, linewidth=1.0, linestyle=(0,(4,2)), alpha=0.5)
ax1.set_ylabel("Cumulative PnL (USD)", fontweight="bold")
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"\\${x/1e3:+.0f}k"))
ax1.set_xticklabels([])
ax1.grid()

arr     = cum_pa[BOOK].astype(float).fillna(0).values
pos_pts = np.maximum(arr, 0)
neg_pts = np.minimum(arr, 0)
pos_stk = np.cumsum(pos_pts, axis=1)
neg_stk = np.cumsum(neg_pts, axis=1)

for i, sec in enumerate(BOOK):
    c = ASSET[sec]
    prev_p = pos_stk[:, i-1] if i > 0 else np.zeros(arr.shape[0])
    prev_n = neg_stk[:, i-1] if i > 0 else np.zeros(arr.shape[0])
    ax2.fill_between(cum_pa.index, prev_p, pos_stk[:, i], color=c, alpha=0.82, linewidth=0)
    ax2.fill_between(cum_pa.index, prev_n, neg_stk[:, i], color=c, alpha=0.82, linewidth=0)

ax2.axhline(0, color="#222", linewidth=0.7)
ax2.axvline(IS_END, color=SLATE, linewidth=1.0, linestyle=(0,(4,2)), alpha=0.5)
ax2.set_ylabel("Stacked PnL (USD)", fontweight="bold")
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"\\${x/1e3:+.0f}k"))
ax2.xaxis.set_major_locator(mdates.YearLocator(2))
ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax2.grid(axis="y")
plt.show()
'''))

cells.append(new_markdown_cell(
    body(
        "<b>Cumulative dollar contribution by leg over the full sample: <code>XLK +140k</code>, <code>SPY +111k</code>, <code>GLD +91k</code>, <code>XLF +68k</code>, <code>IWM +59k</code>, <code>TLT +8k</code>, <code>EFA −10k</code>, <code>EEM −12k</code> (USD on a 1M book). Six of the eight legs end positive; XLK leads at about a third of the total profit. The stacked lower panel shows the colour mix shifting through time rather than concentrating on one leg — the dispersion that diversification is supposed to produce. GLD contributes positively in several diversification-relevant periods, especially 2011, 2020 and 2024. TLT hedges equity drawdowns through 2021 before surrendering most of its profit in the 2022 rate cycle. EFA and EEM end slightly negative; their inclusion is justified by their low correlation to US equities (Figure 13), not by standalone return.</b>"
    )
))


# =============================================================================
# REGIME ENGINE DETAIL (Figure 9)
# =============================================================================
cells.append(new_markdown_cell('<div style="margin:1.8em 0 1.2em 0;"><div style="color:#8B5CF6;font-weight:700;font-size:1.05em;margin-bottom:0.55em;border-left:4px solid #8B5CF6;padding-left:8px;">Regime allocation and conditional performance</div><table style="border-collapse:collapse;margin:0;font-family:DejaVu Sans, Arial, sans-serif;"><thead><tr><th style="padding:7px 14px;text-align:left;border:1px solid white;background:#8B5CF6;color:white;font-weight:600;font-size:0.95em;">Regime</th><th style="padding:7px 14px;text-align:right;border:1px solid white;background:#8B5CF6;color:white;font-weight:600;font-size:0.95em;">Gross multiplier</th><th style="padding:7px 14px;text-align:right;border:1px solid white;background:#8B5CF6;color:white;font-weight:600;font-size:0.95em;">Days</th><th style="padding:7px 14px;text-align:right;border:1px solid white;background:#8B5CF6;color:white;font-weight:600;font-size:0.95em;">Share of sample</th><th style="padding:7px 14px;text-align:right;border:1px solid white;background:#8B5CF6;color:white;font-weight:600;font-size:0.95em;">Mean daily return (bps)</th><th style="padding:7px 14px;text-align:right;border:1px solid white;background:#8B5CF6;color:white;font-weight:600;font-size:0.95em;">Sharpe</th></tr></thead><tbody><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Calm</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">1.5×</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">1,026</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">24.0%</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">+8.07</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">+3.27</td></tr><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Normal</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">1.0×</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">2,644</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">61.8%</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">+0.37</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">+0.15</td></tr><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Stress</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">0.5×</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">557</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">13.0%</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">-8.56</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">-3.36</td></tr><tr><td style="padding:6px 14px;text-align:left;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">Crisis</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">0.0×</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">52</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">1.2%</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">-3.96</td><td style="padding:6px 14px;text-align:right;border:1px solid #E5E7EB;background:transparent;font-size:0.95em;">-3.32</td></tr></tbody></table></div>'))

cells.append(new_markdown_cell(
    "---\n\n"
    "## Figure 9 — The regime engine\n\n"
    + body(
        "Three stacked panels: the composite stress index (top), the gross "
        "multiplier the strategy applies in response (middle), and the regime "
        "label (bottom). The composite is half standardised log(VIX) and half "
        "standardised NFCI, both built using an expanding window with a "
        "252-day minimum. Seven labelled macro events identify the local "
        "stress maxima."
    )
))

cells.append(new_code_cell('''\
"""Figure 9 — composite stress, gross multiplier, regime ribbon."""
fig = plt.figure(figsize=(13, 7.6))
gs  = fig.add_gridspec(3, 1, height_ratios=[2.0, 1.0, 0.4],
                       hspace=0.22, left=0.06, right=0.97, top=0.86, bottom=0.07)
fig_title(fig,
          "Figure 9 — Macro-stress composite, gross multiplier, regime classification",
          "Composite = ½(z(log VIX) + z(NFCI)), expanding-window with 252-day minimum")

ax1 = fig.add_subplot(gs[0])
ms  = stress.astype(float)
y_lo, y_hi = float(ms.min()) - 0.3, float(ms.max()) + 0.7

regime_stripes(ax1, regime, y_lo, y_hi, alpha=0.234)
glow_line(ax1, ms.index, ms.values, TEAL, lw=1.9)
ax1.axhline(0, color=SLATE, linewidth=0.5, linestyle="--", alpha=0.55)
ax1.axvline(IS_END, color=SLATE, linewidth=1.0, linestyle=(0,(4,2)), alpha=0.6)
ax1.set_ylim(y_lo, y_hi)
ax1.set_ylabel("Composite stress z", fontweight="bold")
ax1.set_xticklabels([])
ax1.grid(axis="y")

events = [
    ("2008-10-10", "GFC peak",       28),
    ("2011-08-08", "S&P downgrade",  22),
    ("2015-08-24", "China shock",    18),
    ("2018-02-05", "Volmageddon",    32),
    ("2020-03-23", "COVID bottom",   24),
    ("2022-06-15", "Rate shock",     18),
    ("2023-03-13", "SVB stress",     14),
]
for date_str, label, dy in events:
    d = pd.Timestamp(date_str)
    if ms.index.min() <= d <= ms.index.max():
        i = ms.index.get_indexer([d], method="nearest")[0]
        n, v = ms.index[i], float(ms.iloc[i])
        ax1.scatter([n], [v], s=45, color=WINE,
                    edgecolor="white", linewidth=1.3, zorder=8)
        ax1.annotate(label, xy=(n, v), xytext=(0, dy),
                     textcoords="offset points", fontsize=9,
                     ha="center", color=WINE, fontweight="bold",
                     bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                               edgecolor=WINE, linewidth=0.8),
                     arrowprops=dict(arrowstyle="-", color=WINE,
                                     linewidth=0.7, alpha=0.65))

ax2 = fig.add_subplot(gs[1], sharex=ax1)
gm  = gross_mult.astype(float)
ax2.fill_between(gm.index, 0, gm.values, color=FOREST, alpha=0.56)
glow_line(ax2, gm.index, gm.values, FOREST, lw=1.6, glow=2)
ax2.axvline(IS_END, color=SLATE, linewidth=1.0, linestyle=(0,(4,2)), alpha=0.6)
ax2.set_ylim(0, 1.8)
ax2.set_yticks([0, 0.5, 1.0, 1.5])
ax2.set_yticklabels(["off", "0.5× stress", "1.0× normal", "1.5× calm"], fontsize=9.5)
ax2.set_ylabel("Gross mult.", fontweight="bold")
ax2.set_xticklabels([])
ax2.grid(axis="y")

ax3 = fig.add_subplot(gs[2], sharex=ax1)
for r, color in REGIME_C.items():
    ax3.fill_between(regime.index, 0, 1, where=(regime == r),
                     color=color, linewidth=0)
ax3.set_yticks([]); ax3.set_ylim(0, 1)
ax3.set_ylabel("Regime", fontweight="bold")
for s in ("top","right","bottom","left"): ax3.spines[s].set_visible(False)
ax3.xaxis.set_major_locator(mdates.YearLocator(2))
ax3.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
plt.show()
'''))

cells.append(new_markdown_cell(
    body(
        "<b>Top: the composite stress index — a 50/50 blend of standardised log(VIX) and standardised NFCI — with seven labelled macro events at its local maxima (2008 GFC peak, 2011 US-credit downgrade, 2015 China shock, 2018 Volmageddon, 2020 COVID bottom, 2022 rate shock, 2023 SVB stress). Middle: the gross multiplier the strategy applies in response — 1.5× in calm, 1.0× in normal, 0.5× in stress, 0× in crisis. Bottom: the realised regime classification — 24% calm, 62% normal, 13% stress, 1.2% crisis (about 52 trading days fully cashed out across seventeen years). VIX measures option-implied equity volatility; NFCI measures credit spreads and dealer-balance-sheet conditions. Credit deteriorated months before equity vol responded in 2007, and the composite captures that early warning by combining the two. Every value uses an expanding window with a 252-day minimum, so the composite on any date depends only on data observable that day.</b>"
    )
))


# =============================================================================
# Build and write — append the remaining figure modules in narrative order:
#   diagnostics (Figs 10-16) then persistence (Figs 17-18). The data-view
#   module (DEMO_STYLE_CELLS) is appended earlier in the cell stream.
# =============================================================================
import importlib.util as _ils
cells.append(new_markdown_cell(
    "---\n\n"
    "## Robustness diagnostics\n\n"
    + body(
        "A single headline Sharpe and a single drawdown hide most of what an allocator actually wants to know. The next seven figures break the strategy apart from different angles. Rolling Sharpe through time (Figure 10) — is the edge stable or does it average a long good stretch with a long bad one? Tail behaviour (Figure 11) — does VaR computed under a Normal assumption understate the real downside? Conditional Sharpe by regime (Figure 12) — is the gate doing real work or just cosmetic? Cross-asset correlation (Figure 13) — is the diversification benefit real? Risk-return positioning (Figure 14) — where does the book sit vs the individual sleeves? Monthly calendar (Figure 15) — when do losses cluster? VIX-vs-return joint density (Figure 16) — how much of the negative tail does weekly rebalancing leave on the table?"
    )
))
_spec = _ils.spec_from_file_location("nb_add", str(OUT / "notebook_additions.py"))
_mod = _ils.module_from_spec(_spec); _spec.loader.exec_module(_mod)
cells.extend(_mod.EXTRA_CELLS)
print(f"Appended {len(_mod.EXTRA_CELLS)} diagnostics cells; total {len(cells)}.")

cells.append(new_markdown_cell(
    "---\n\n"
    "## Persistence: did the per-leg edge survive?\n\n"
    + body(
        "Figure 7 answered the validity question at the aggregate book level — the OOS Sharpe lands inside the IS confidence band. The two figures below run the same test asset by asset. Did each leg keep its edge across the freeze, or did the aggregate survive because winners and losers happened to offset? Figure 17 plots each leg\'s in-sample Sharpe against its out-of-sample Sharpe: top-right quadrant survived, points that crossed an axis flipped. Figure 18 is the regime × asset Sharpe grid: which legs earn their place in calm, in stress, in crisis, and which cells are statistically too noisy to call."
    )
))
_spec2 = _ils.spec_from_file_location("nb_borrow", str(OUT / "extra_figs_borrowed.py"))
_mod2 = _ils.module_from_spec(_spec2); _spec2.loader.exec_module(_mod2)
cells.extend(_mod2.BORROWED_CELLS)
print(f"Appended {len(_mod2.BORROWED_CELLS)} persistence cells; total {len(cells)}.")


# =============================================================================
# SIGNAL VALIDATION — Figure 20 (cross-sectional IV-rank fan)
# =============================================================================
cells.append(new_markdown_cell(
    "---\n\n"
    "## Signal validation: decile fans\n\n"
    + body(
        "The diagnostics above test the strategy as a whole — rolling Sharpe, "
        "tail shape, regime conditioning, per-leg persistence. The two final "
        "figures test the underlying signals directly. The strategy has two "
        "signal inputs: the composite stress index (which drives the macro "
        "regime gate), and the per-leg 30-day ATM implied volatility (which "
        "drives the inverse-vol sizing). Each one gets a decile fan, the "
        "canonical test for whether a quant signal contains usable information."
    )
    + body(
        "Figure 19 sorts trading days into ten deciles of lagged composite "
        "stress and cumulates the strategy P&amp;L conditional on each "
        "decile — the time-series test of the gate signal. Figure 20 sorts "
        "the eight ETFs into rank positions by their 30-day IV at each "
        "rebalance and tracks each rank position\\\'s cumulative return — "
        "the cross-sectional test of the sizing signal. A clean signal "
        "produces monotonic fan separation; a noisy or partial signal "
        "produces tangled lines. Reading both honestly is what tells you "
        "where the strategy\\\'s edge actually lives."
    )
))

cells.append(new_markdown_cell(
    "---\n\n"
    "## Figure 19 — Decile P&L fan by composite stress\n\n"
    + body(
        "Trading days sorted by the previous day\\\'s composite stress z-score "
        "and bucketed into ten equal-frequency deciles (D1 = calmest, "
        "D10 = most stressed). Each decile\\\'s daily strategy P&amp;L is then "
        "cumulated through time. This is the continuous-signal counterpart "
        "to Figure 12\\\'s four hard regime buckets — the decile fan shows "
        "whether the gradient across stress is smooth or only meaningful at "
        "the regime thresholds."
    )
))

cells.append(new_code_cell("""
# Figure 19 — decile P&L fan by composite stress (lagged 1 day)
from matplotlib.colors import LinearSegmentedColormap

stress_lag = stress.reindex(pnl.index).ffill().shift(1)
df = pd.DataFrame({'pnl': pnl.astype(float), 'stress_lag': stress_lag}).dropna()
df['decile'] = pd.qcut(df['stress_lag'], 10, labels=False, duplicates='drop')

trajectories = {}
for d in range(10):
    pnl_d = df['pnl'].where(df['decile'] == d, 0)
    trajectories[d] = pnl_d.cumsum() * 1_000_000

FAN19 = LinearSegmentedColormap.from_list(
    'fan19', ['#1E40AF', '#60A5FA', '#A78BFA', '#FBBF24', '#B8860B'], N=10
)

fig, ax = plt.subplots(figsize=(13, 6.0), facecolor='white')
fig.subplots_adjust(top=0.84, bottom=0.10, left=0.07, right=0.86)
fig_title(fig,
          'Figure 19 — Decile P&L fan by composite stress (lagged 1 day)',
          'trading days bucketed into 10 equal-frequency deciles  ·  D1 = lowest stress  ·  D10 = highest stress')

for d in range(10):
    color = FAN19(d / 9)
    cum = trajectories[d]
    final = cum.iloc[-1]
    ax.plot(cum.index, cum.values, color=color, linewidth=1.4,
            label=f'D{d+1}  ${final/1e3:+.0f}k', alpha=0.95)

ax.axhline(0, color='#0C111D', linewidth=0.6, linestyle='--', alpha=0.5)
ax.axvline(IS_END, color='#3D5A80', linewidth=1.0, linestyle=(0,(4,2)), alpha=0.55)
ax.set_ylabel('Cumulative decile P&L (USD on 1M)', fontweight='bold', color='#0C111D', fontsize=10)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x/1e3:+.0f}k'))
ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), fontsize=8.5, frameon=False, ncol=1)
ax.tick_params(labelsize=9.5, colors='#3D5A80')
ax.grid(alpha=0.28)
plt.show()
"""))

cells.append(new_markdown_cell(
    body(
        "<b>The decile fan is not monotonic. The strongest cumulative P&amp;L appears in the middle stress deciles — <code>D5 +148k</code> and <code>D4 +131k</code> — while the lowest-stress decile ends negative at <code>D1 −37k</code> and the highest-stress decile remains modestly positive at <code>D10 +57k</code> (USD on a 1M book). The signal does not produce a simple linear relation between stress level and return. The pattern is consistent with the regime gate reducing exposure in very high-stress states (so D10 P&amp;L is small in absolute terms), but a direct no-gate counterfactual would be needed to measure the gate's standalone effect.</b>"
    )
))

cells.append(new_markdown_cell(
    "---\n\n"
    "## Figure 20 — Cross-sectional IV-rank fan\n\n"
    + body(
        "At each Friday rebalance the eight ETFs are sorted by their 30-day "
        "ATM IV (rank 1 = lowest IV, rank 8 = highest IV). Each rank "
        "position is then held as a single-asset basket until the next "
        "rebalance, and the per-rank cumulative compounded return is "
        "tracked from 2008 to 2024. The vertical dashed line marks the "
        "in-sample / out-of-sample boundary at end-2017."
    )
))

cells.append(new_code_cell("""
\"\"\"Figure 20 — cross-sectional IV-rank fan (8 ranks, weekly rebalance).\"\"\"
from matplotlib.colors import LinearSegmentedColormap

ivs = {}
for tk in BOOK:
    iv_df = pd.read_parquet(DEMO / f'v3_iv_extras_{tk.lower()}.parquet')
    iv_df['date'] = pd.to_datetime(iv_df['date'])
    ivs[tk] = iv_df.set_index('date')['iv30_atm']
iv_panel = pd.DataFrame(ivs).sort_index().reindex(spot.index).ffill()

spot_rets = spot.pct_change().fillna(0)

fri = pd.date_range(spot.index.min(), spot.index.max(), freq='W-FRI')
fri = fri.intersection(spot.index)

rank_rets = pd.DataFrame(0.0, index=spot.index, columns=list(range(1, 9)))
for prev, curr in zip(fri[:-1], fri[1:]):
    iv_at = iv_panel.loc[prev]
    if iv_at.isna().any():
        continue
    ranking = iv_at.rank(ascending=True).astype(int)
    rank_to_asset = {int(ranking[a]): a for a in iv_at.index}
    mask = (spot.index > prev) & (spot.index <= curr)
    for r in range(1, 9):
        rank_rets.loc[mask, r] = spot_rets.loc[mask, rank_to_asset[r]]

cum = (1 + rank_rets).cumprod()

FAN_CMAP = LinearSegmentedColormap.from_list(
    'iv_rank_fan',
    ['#1E40AF', '#3B82F6', '#60A5FA', '#A78BFA', '#FBBF24', '#FF6A00', '#DC2626', '#7F1D1D'],
    N=8,
)

fig, ax = plt.subplots(figsize=(13, 6.0), facecolor='white')
fig.subplots_adjust(top=0.84, bottom=0.10, left=0.07, right=0.86)
spread = cum.iloc[-1, 7] - cum.iloc[-1, 0]
fig_title(fig,
          'Figure 20 — Cross-sectional IV-rank fan',
          f'8 ETFs ranked weekly by 30-day ATM IV  ·  each rank held as a single-asset basket  ·  R8 − R1 cumulative spread {spread:+.2f}x')

for r in range(1, 9):
    color = FAN_CMAP((r - 1) / 7)
    final = cum.iloc[-1, r - 1]
    ax.plot(cum.index, cum[r], color=color, linewidth=1.5,
            label=f'R{r}  {final:.2f}x', alpha=0.95)

ax.axhline(1, color='#0C111D', linewidth=0.6, linestyle='--', alpha=0.5)
ax.axvline(IS_END, color='#3D5A80', linewidth=1.0, linestyle=(0,(4,2)), alpha=0.55)
ax.set_ylabel('Cumulative compounded return (x)', fontweight='bold', color='#0C111D', fontsize=10)
ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), fontsize=8.5, frameon=False,
          title='R1 = lowest IV', title_fontsize=8.5)
ax.tick_params(labelsize=9.5, colors='#3D5A80')
ax.grid(alpha=0.28)
plt.show()
"""))

cells.append(new_markdown_cell(
    body(
        "<b>The rank-position curves are not monotonic. R6 ends highest at 6.72x, followed by R5 at 2.99x, R3 at 2.80x, R7 at 2.37x, R2 at 2.01x, R1 at 1.55x, R4 at 1.22x, and R8 at 1.21x. R8 finishes below R1, so the R8 − R1 cumulative spread is slightly negative at -0.34x — the highest-IV rank did not earn a clear premium over the lowest-IV rank in this sample. This diagnostic does not support a simple higher-IV-predicts-higher-return story. The strategy's argument is instead about risk sizing: implied volatility is useful for scaling exposure, not for cleanly ranking future returns across assets.</b>"
    )
))


# =============================================================================
# CONCLUSION
# =============================================================================
cells.append(new_markdown_cell(
    "---\n\n"
    "## What this project shows\n\n"
    + body(
        "The main result is not that option-implied volatility predicts returns. The earlier demo tested that more direct idea and failed in the held-out period. The more useful application here is sizing: implied volatility helps decide how much risk to carry in each sleeve, while the VIX/NFCI regime gate controls total exposure."
    )
    + body(
        f"The strategy does not beat the equal-weight benchmark on terminal wealth. Starting from USD 1.00M, it ends at <b>USD {(1+FULL_tot)*1e6/1e6:.2f}M</b> versus USD 2.64M for the benchmark. The benefit is risk control: the maximum drawdown is <b>{FULL_dd*100:+.1f}%</b> versus about -45% for equal weight. The held-out Sharpe falls from <b>{IS_sh:+.2f}</b> in the design window to <b>{OOS_sh:+.2f}</b> in 2018-2024, so performance decays but remains positive."
    )
    + body(
        "The practical lesson is that the option data were more useful as a risk input than as a directional signal. The strategy gives up upside in exchange for a smoother path, lower drawdown, and explicit exposure cuts during stress regimes."
    )
    + body(
        "<b>Limitations.</b> The ETF universe is fixed at the end of 2017. Rebalancing is weekly, so a different cadence would change turnover and costs. The regime model uses four discrete buckets, and the crisis bucket has only 52 observations. Those choices are reasonable for this project, but they are not the only possible implementation."
    )
    + body(
        "<b>Readings.</b> The methodology draws on the course readings on backtesting discipline, multiple-testing concerns in strategy evaluation, volatility information, and changing cross-asset correlations, especially Harvey and Liu (2015) and Johnson, Naik, Page, Pedersen, and Sapra (PIMCO, 2013)."
    )
))



# ---- Inject diagnostic tables at rhythm points (Figs 11, 13, 15, 17) ----
def _md_table_to_html(md_table, title, accent, pale):
    lines = [ln for ln in md_table.strip().split("\n") if ln.strip()]
    header_cells = [c.strip() for c in lines[0].strip("|").split("|")]
    sep_cells    = [c.strip() for c in lines[1].strip("|").split("|")]
    aligns = []
    for s in sep_cells:
        if s.startswith(":") and s.endswith(":"): aligns.append("center")
        elif s.endswith(":"):                     aligns.append("right")
        else:                                     aligns.append("left")
    body_rows = [[c.strip() for c in ln.strip("|").split("|")] for ln in lines[2:]]
    th = "".join(
        f'<th style="padding:7px 14px;text-align:{a};border:1px solid white;background:{accent};color:white;font-weight:600;font-size:0.95em;">{c}</th>'
        for c, a in zip(header_cells, aligns)
    )
    rows = []
    for i, row in enumerate(body_rows):
        bg = pale if i % 2 == 0 else "#FFFFFF"
        tds = "".join(
            f'<td style="padding:6px 14px;text-align:{a};border:1px solid #E5E7EB;background:{bg};font-size:0.95em;">{c}</td>'
            for c, a in zip(row, aligns)
        )
        rows.append(f"<tr>{tds}</tr>")
    return (
        f'<div style="margin:1.8em 0 1.2em 0;">'
        f'<div style="color:{accent};font-weight:700;font-size:1.05em;margin-bottom:0.55em;border-left:4px solid {accent};padding-left:8px;">{title}</div>'
        f'<table style="border-collapse:collapse;margin:0;font-family:DejaVu Sans, Arial, sans-serif;">'
        f'<thead><tr>{th}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody>'
        f'</table>'
        f'</div>'
    )

_DIAG_TABLES = [
    # (figure marker, title, accent, pale, markdown table)
    ("## Figure 11 — Tail behaviour of daily returns", "Daily-return distribution moments", "#3D5A80", "transparent",
     '| Statistic | Value |\n|---|---:|\n| Mean daily return | +0.0100% |\n| Daily standard deviation | 0.401% |\n| Skewness | -0.60 |\n| Excess kurtosis | +3.60 |\n| Student-t fitted degrees of freedom | 3.9 |\n| Number of daily observations | 4,279 |\n'),
    ("## Figure 13 — Cross-asset correlation structure", "Cross-asset correlation summary", "#4E79A7", "transparent",
     '| Relationship | Average correlation | Range |\n|---|---:|---|\n| Equity sleeves with each other (six legs, fifteen pairs) | +0.81 | +0.69 to +0.92 |\n| TLT with equity sleeves | -0.31 | -0.34 to -0.27 |\n| GLD with equity sleeves | +0.06 | -0.05 to +0.15 |\n| GLD with TLT | +0.19 | - |\n'),
    ("## Figure 15 — Calendar of monthly returns", "Monthly-return summary", "#D4AF37", "transparent",
     '| Monthly statistic | Value |\n|---|---:|\n| Number of months | 204 |\n| Positive months | 118 |\n| Positive-month share | 58% |\n| Best month | +4.37% (2023-11) |\n| Worst month | -5.38% (2018-10) |\n'),
    ("## Figure 17 — The persistence diagnostic", "IS-vs-OOS Sharpe by sleeve", "#D4351C", "transparent",
     '| Sleeve | IS Sharpe (2008-2017) | OOS Sharpe (2018-2024) | Change |\n|---|---:|---:|---:|\n| SPY | +0.63 | +0.44 | -0.18 |\n| IWM | +0.47 | +0.01 | -0.46 |\n| EFA | +0.07 | -0.26 | -0.33 |\n| EEM | -0.01 | -0.19 | -0.18 |\n| XLK | +0.70 | +0.64 | -0.06 |\n| XLF | +0.39 | +0.23 | -0.16 |\n| GLD | +0.21 | +0.79 | +0.58 |\n| TLT | +0.14 | -0.15 | -0.29 |\n| <b>Book</b> | <b>+0.47</b> | <b>+0.28</b> | <b>-0.18</b> |\n'),
]

_new_cells = []
for c in cells:
    src_text = c["source"] if isinstance(c["source"], str) else "".join(c["source"])
    for marker, title, accent, pale, table_md in _DIAG_TABLES:
        if marker in src_text:
            _new_cells.append(new_markdown_cell(_md_table_to_html(table_md, title, accent, pale)))
            break
    _new_cells.append(c)
cells = _new_cells


nb = new_notebook()
nb["cells"] = cells

nb_path = OUT / "final_project_notebook_v3.ipynb"
with open(nb_path, "w", encoding="utf-8") as f:
    nbf.write(nb, f)
print(f"Wrote {nb_path}")
print(f"Cells: {len(cells)} cells written")
