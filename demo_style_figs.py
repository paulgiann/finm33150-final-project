"""Demo-style figures using strategy data.

Five new figures that adopt the demo notebook's chart-type vocabulary:
  A. 4-panel headline (Cell 18 style): stress / equity log / return dist / leverage scatter
  B. 3-row IV diagnostic (Cell 14 style): per-asset 30d IV + boxplot + spread histograms
  C. 1x2 term structure + dual-axis (Cell 21 style): per-asset IV monthly mean + VIX/NFCI
  D. 2x2 skew/smile (Cell 10 style): per-asset 25dp / ATM / 25dc IV averages
  E. 1x2 IV vs VIX (Cell 47 style): SPY 30d ATM IV vs CBOE VIX, time series + scatter

All figures use the unified palette in demo_palette.py.
"""
from nbformat.v4 import new_markdown_cell, new_code_cell


def body(text):
    return ('<div style="font-size:1.13em; line-height:1.65; text-align:justify;">\n\n'
            + text + '\n\n</div>')


DEMO_STYLE_CELLS = []


# =============================================================================
# A. Demo-style 4-panel headline (Cell 18 of demo)
# =============================================================================
DEMO_STYLE_CELLS.append(new_markdown_cell(
    "---\n\n"
    "## Figure 1 — Headline data view\n\n"
    + body(
        "Four panels summarising the data the strategy operates on: "
        "the composite stress z-score (top-left), the strategy equity curve on a log scale (top-right), "
        "the daily-return distribution (bottom-left), and the SPY-vs-VIX leverage-effect scatter (bottom-right). "
        "Built from the macro panel, the realised P&L parquet, and the spot-price panel."
    )
))

DEMO_STYLE_CELLS.append(new_code_cell('''\
"""Figure 1 — Headline data view (compact, Modern SaaS palette, integrated title)."""
import matplotlib.dates as mdates
from matplotlib import gridspec
P = PALETTE  # inlined in setup cell

vix_series = macro_panel["VIX"].astype(float)
spy_ret = rets["SPY"].astype(float) * 100
aligned = pd.concat([vix_series.rename("VIX"), spy_ret.rename("SPY_ret")], axis=1).dropna()

fig = plt.figure(figsize=(12.5, 7.2), facecolor="white")
gs = gridspec.GridSpec(2, 2, height_ratios=[1.1, 1], hspace=0.50, wspace=0.30)
fig.subplots_adjust(top=0.86, bottom=0.10, left=0.07, right=0.97)
fig_title(fig,
          "Figure 1 — Headline data view",
          "composite stress · strategy equity (log) · daily-return distribution · leverage-effect scatter")

# TL: composite stress
ax = fig.add_subplot(gs[0, 0])
ax.fill_between(stress.index, 0, stress.values, color=P["SAAS_red"], alpha=0.14)
ax.plot(stress.index, stress.values, color=P["SAAS_red"], linewidth=0.8)
ax.axhline(stress.median(), color=P["SAAS_blue"], linewidth=1.0, linestyle="--",
           label=f"median  {stress.median():+.2f}")
ax.axhline(np.percentile(stress.dropna(), 90), color=P["AQR_navy"], linewidth=1.0,
           linestyle=":", label=f"90th pct  {np.percentile(stress.dropna(), 90):+.2f}")
ax.xaxis.set_major_locator(mdates.YearLocator(3))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.set_title("Composite stress z", loc="left", fontweight="bold", fontsize=10.5, color=P["ink"])
ax.set_ylabel("z-score", fontweight="bold", color=P["ink"], fontsize=9.5)
ax.legend(loc="upper right", fontsize=8, frameon=False)
ax.tick_params(labelsize=8.5, colors=P["subtext"])
ax.grid(alpha=0.28)

# TR: equity log
ax2 = fig.add_subplot(gs[0, 1])
ax2.plot(EQ.index, EQ.values, color=P["SAAS_green"], linewidth=1.4)
ax2.fill_between(EQ.index, EQ.values.min(), EQ.values, color=P["SAAS_green"], alpha=0.10)
ax2.set_yscale("log")
ax2.xaxis.set_major_locator(mdates.YearLocator(3))
ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax2.set_title("Strategy equity · log scale", loc="left", fontweight="bold", fontsize=10.5, color=P["ink"])
ax2.set_ylabel("Portfolio value (log USD)", fontweight="bold", color=P["ink"], fontsize=9.5)
ax2.tick_params(labelsize=8.5, colors=P["subtext"])
ax2.grid(alpha=0.28, which="both")

# BL: daily return distribution
ax3 = fig.add_subplot(gs[1, 0])
r = pnl.dropna().astype(float) * 100
ax3.hist(r, bins=70, color=P["SAAS_blue"], edgecolor="white", linewidth=0.4, alpha=0.85)
ax3.axvline(r.mean(), color=P["SAAS_amber"], linewidth=1.4, linestyle="--",
            label=f"mean {r.mean():+.3f}%")
ax3.axvline(r.std(),  color=P["SAAS_red"], linewidth=1.1, linestyle=":",
            label=f"±σ  {r.std():.3f}%")
ax3.axvline(-r.std(), color=P["SAAS_red"], linewidth=1.1, linestyle=":")
ax3.set_xlabel("Daily strategy return (%)", fontweight="bold", color=P["ink"], fontsize=9.5)
ax3.set_ylabel("Count", fontweight="bold", color=P["ink"], fontsize=9.5)
ax3.set_title("Daily-return distribution", loc="left", fontweight="bold", fontsize=10.5, color=P["ink"])
ax3.legend(loc="upper right", fontsize=8, frameon=False)
ax3.tick_params(labelsize=8.5, colors=P["subtext"])
ax3.grid(alpha=0.28)

# BR: leverage-effect scatter
ax4 = fig.add_subplot(gs[1, 1])
ax4.scatter(aligned["SPY_ret"], aligned["VIX"], s=7, color=P["SAAS_violet"],
            alpha=0.30, edgecolor="none")
slope, intercept = np.polyfit(aligned["SPY_ret"], aligned["VIX"], 1)
xs = np.linspace(aligned["SPY_ret"].min(), aligned["SPY_ret"].max(), 60)
ax4.plot(xs, slope*xs + intercept, color=P["SAAS_amber"], linewidth=2.0,
         label=f"OLS slope {slope:+.2f}")
corr = aligned["SPY_ret"].corr(aligned["VIX"])
ax4.set_xlabel("Daily SPY return (%)", fontweight="bold", color=P["ink"], fontsize=9.5)
ax4.set_ylabel("VIX level", fontweight="bold", color=P["ink"], fontsize=9.5)
ax4.set_title(f"Leverage effect · corr {corr:+.2f}", loc="left", fontweight="bold", fontsize=10.5, color=P["ink"])
ax4.legend(loc="upper right", fontsize=8, frameon=False)
ax4.tick_params(labelsize=8.5, colors=P["subtext"])
ax4.grid(alpha=0.28)
plt.show()
'''))

DEMO_STYLE_CELLS.append(new_markdown_cell(
    body(
        "<b>Top-left: the composite stress z-score spikes above its 90th-percentile mark (+0.38) in 2008, 2011, 2020 and 2022 — the same windows where the gross multiplier cut exposure. Top-right: the equity curve on a log scale climbs from USD 1.00M to USD 1.48M without the deep 2008 trench a buy-and-hold benchmark would show. Bottom-left: daily-return distribution concentrated near a positive mean (+0.011%/day) with one-sigma at 0.39%; the narrow dispersion is what risk targeting produces. Bottom-right: SPY daily return against the contemporaneous VIX level, OLS slope -1.10 and correlation -0.15. When stocks fall the cost of insurance rises — the leverage effect, the empirical fact that makes implied volatility a forward-looking risk gauge worth reading.</b>"
    )
))



# =============================================================================
# B. 3-row IV diagnostic (Cell 14 of demo)
# =============================================================================
DEMO_STYLE_CELLS.append(new_markdown_cell(
    "---\n\n"
    "## Figure 2 — Cross-asset implied-volatility diagnostic\n\n"
    + body(
        "30-day at-the-money implied volatility for the eight ETFs in the book, "
        "extracted from WRDS OptionMetrics IvyDB constant-maturity surfaces. "
        "Top row: the time series. Middle: per-asset distributions (left) and three "
        "cross-sectional spread histograms (right). Bottom: the cross-asset 60-day mean. "
        "This is the input the inverse-vol sizing rule reads."
    )
))

DEMO_STYLE_CELLS.append(new_code_cell('''\
"""Figure 2 — Cross-asset IV diagnostic (compact, integrated title)."""
import matplotlib.dates as mdates
from matplotlib import gridspec
P = PALETTE

ivs = {}
for tk in BOOK:
    iv_df = pd.read_parquet(DEMO / f"v3_iv_extras_{tk.lower()}.parquet")
    iv_df["date"] = pd.to_datetime(iv_df["date"])
    ivs[tk] = iv_df.set_index("date")["iv30_atm"] * 100
iv_panel = pd.DataFrame(ivs).sort_index()

fig = plt.figure(figsize=(13, 8.6), facecolor="white")
gs = gridspec.GridSpec(3, 4, height_ratios=[1.35, 1.0, 1.0], hspace=0.55, wspace=0.36)
fig.subplots_adjust(top=0.89, bottom=0.07, left=0.06, right=0.98)
fig_title(fig,
          "Figure 2 — Cross-asset implied-volatility diagnostic",
          "30d ATM IV per asset · distribution · cross-sectional spread · 60d cross-asset mean")

asset_colors = {tk: P[tk] for tk in BOOK}

# Row 1: 8 tickers stacked
ax = fig.add_subplot(gs[0, :])
sm = iv_panel.rolling(5, min_periods=1).mean()
for tk in BOOK:
    ax.plot(sm.index, sm[tk], color=asset_colors[tk], linewidth=1.0,
            label=tk, alpha=0.95)
ax.set_ylabel("30-day ATM IV (%)", fontweight="bold", color=P["ink"], fontsize=9.5)
ax.set_title(f"30d ATM IV across the book · {iv_panel.index.min().year}-{iv_panel.index.max().year}",
             loc="left", fontweight="bold", fontsize=10.5, color=P["ink"])
ax.legend(loc="upper right", ncol=8, fontsize=8, frameon=False, columnspacing=0.9)
ax.xaxis.set_major_locator(mdates.YearLocator(3))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.tick_params(labelsize=8.5, colors=P["subtext"])
ax.grid(alpha=0.28)

# Row 2 left: boxplot of 30d IV per asset
ax2 = fig.add_subplot(gs[1, :2])
data = [iv_panel[tk].dropna().values for tk in BOOK]
bp = ax2.boxplot(data, labels=BOOK, patch_artist=True, widths=0.58,
                 medianprops=dict(color="white", linewidth=1.8),
                 whiskerprops=dict(color=P["subtext"], linewidth=1.0),
                 capprops=dict(color=P["subtext"], linewidth=1.0),
                 flierprops=dict(marker="o", markersize=2.2, markerfacecolor=P["subtext"],
                                 markeredgecolor="none", alpha=0.55))
for patch, tk in zip(bp["boxes"], BOOK):
    patch.set_facecolor(asset_colors[tk]); patch.set_alpha(0.85)
    patch.set_edgecolor(asset_colors[tk]); patch.set_linewidth(1.0)
ax2.set_ylabel("30d ATM IV (%)", fontweight="bold", color=P["ink"], fontsize=9.5)
ax2.set_title(f"Per-asset distribution · {len(iv_panel):,} days",
              loc="left", fontweight="bold", fontsize=10.5, color=P["ink"])
ax2.tick_params(labelsize=8.5, colors=P["subtext"])
ax2.grid(alpha=0.28, axis="y")

# Row 2 right: cross-sectional IV spread histograms (3 panels)
spread_specs = [
    ("XLK - SPY", iv_panel["XLK"] - iv_panel["SPY"], P["SAAS_violet"]),
    ("EEM - EFA", iv_panel["EEM"] - iv_panel["EFA"], P["SAAS_green"]),
    ("XLF - SPY", iv_panel["XLF"] - iv_panel["SPY"], P["SAAS_red"]),
]
gs_in = gs[1, 2:].subgridspec(1, 3, wspace=0.30)
xlo = min(s.min() for _, s, _ in spread_specs) * 1.1
xhi = max(s.max() for _, s, _ in spread_specs) * 1.1
for k, (name, sp, col) in enumerate(spread_specs):
    axk = fig.add_subplot(gs_in[0, k])
    axk.hist(sp.dropna(), bins=22, color=col, alpha=0.88,
             edgecolor="white", linewidth=0.5, range=(xlo, xhi))
    axk.axvline(0, color=P["ink"], linewidth=0.6, alpha=0.5)
    axk.axvline(sp.median(), color=col, linestyle="--", linewidth=1.2)
    axk.set_title(f"{name}\\nmedian {sp.median():+.2f}",
                  loc="left", fontweight="bold", fontsize=9, color=col, pad=2)
    axk.set_xlim(xlo, xhi)
    axk.tick_params(labelsize=7.5, colors=P["subtext"])
    axk.grid(alpha=0.22)
    if k == 0: axk.set_ylabel("Count", fontweight="bold", color=P["ink"], fontsize=9)

# Row 3: rolling 60d cross-asset average IV
ax_b = fig.add_subplot(gs[2, :])
mean_iv = iv_panel.mean(axis=1).rolling(60, min_periods=1).mean()
ax_b.fill_between(mean_iv.index, mean_iv.values, color=P["BLOOM_navy"], alpha=0.13)
ax_b.plot(mean_iv.index, mean_iv.values, color=P["BLOOM_navy"], linewidth=1.5)
ax_b.axhline(mean_iv.median(), color=P["BLOOM_red"], linewidth=1.0, linestyle="--",
             label=f"median {mean_iv.median():.1f}%")
ax_b.set_ylabel("Mean 30d ATM IV (%)", fontweight="bold", color=P["ink"], fontsize=9.5)
ax_b.set_title("Cross-asset mean 30d IV · 60-day smoothed",
               loc="left", fontweight="bold", fontsize=10.5, color=P["ink"])
ax_b.legend(loc="upper right", fontsize=8, frameon=False)
ax_b.xaxis.set_major_locator(mdates.YearLocator(3))
ax_b.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax_b.tick_params(labelsize=8.5, colors=P["subtext"])
ax_b.grid(alpha=0.28)
plt.show()
'''))

DEMO_STYLE_CELLS.append(new_markdown_cell(
    body(
        "<b>Top: 30-day at-the-money implied volatility for the eight ETFs over 2008-2024 — all eight spike together in 2008, 2020 and 2022, but their resting levels differ: TLT and GLD around 12-20% in calm periods, EEM and XLF closer to 18-30%. Middle-left: per-asset boxplots make the ordering explicit and show how wide each leg's vol distribution is. Middle-right: histograms of three cross-sectional spreads (XLK-SPY, EEM-EFA, XLF-SPY) — each centred well away from zero, persistent rather than transient. Bottom: the cross-asset 60-day mean IV ranges from 14% in 2017 to above 50% in 2020. The inverse-vol rule reads each leg's series in the top panel and assigns proportionally smaller weight when its implied vol is high, so every leg in the book contributes the same dollar risk regardless of its underlying volatility.</b>"
    )
))



# =============================================================================
# C. 1x2 term structure + dual-axis (Cell 21 of demo)
# =============================================================================
DEMO_STYLE_CELLS.append(new_markdown_cell(
    "---\n\n"
    "## Figure 3 — Monthly IV term structure and macro-stress drivers\n\n"
    + body(
        "Two panels. Left: each asset\'s 30-day ATM implied vol at monthly mean. "
        "Right: the two macro inputs to the regime gate side-by-side — CBOE VIX "
        "(left axis) and the Chicago Fed NFCI (right axis)."
    )
))

DEMO_STYLE_CELLS.append(new_code_cell('''\
"""Demo C — Term structure + VIX/NFCI dual axis."""
import matplotlib.dates as mdates
P = PALETTE  # inlined in setup cell

ivs = {}
for tk in BOOK:
    iv_df = pd.read_parquet(DEMO / f"v3_iv_extras_{tk.lower()}.parquet")
    iv_df["date"] = pd.to_datetime(iv_df["date"])
    ivs[tk] = iv_df.set_index("date")["iv30_atm"] * 100
iv_panel = pd.DataFrame(ivs).sort_index()
iv_monthly = iv_panel.resample("ME").mean()

vix_series = macro_panel["VIX"].astype(float)
nfci_series = macro_panel["NFCI"].astype(float)

fig, axes = plt.subplots(1, 2, figsize=(13, 5.4), gridspec_kw={"wspace": 0.34},
                          facecolor="white")
fig.subplots_adjust(top=0.82, bottom=0.13, left=0.06, right=0.95)
fig_title(fig,
          "Figure 3 — Monthly IV term structure and macro-stress drivers",
          "per-asset monthly mean 30d IV · VIX + NFCI dual axis · 2008-2024")

# Left: per-asset monthly mean IV
ax = axes[0]
for tk in BOOK:
    ax.plot(iv_monthly.index, iv_monthly[tk], color=P[tk], linewidth=1.1,
            label=tk, alpha=0.95)
ax.set_title("30d ATM IV by asset · monthly mean",
             loc="left", fontweight="bold", fontsize=10.5, color=P["ink"])
ax.set_ylabel("Implied vol (%)", fontweight="bold", color=P["ink"], fontsize=9.5)
ax.xaxis.set_major_locator(mdates.YearLocator(3))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.legend(ncol=8, loc="upper right", fontsize=8, frameon=False, columnspacing=0.9)
ax.tick_params(labelsize=8.5, colors=P["subtext"])
ax.grid(alpha=0.28)

# Right: VIX (left axis) + NFCI (right axis)
ax2 = axes[1]
vix_m = vix_series.resample("ME").mean()
nfci_m = nfci_series.resample("ME").mean()
ax2.plot(vix_m.index, vix_m.values, color=P["BLOOM_red"], linewidth=1.4,
         label="VIX (left)")
ax_r = ax2.twinx()
ax_r.plot(nfci_m.index, nfci_m.values, color=P["BLOOM_navy"], linewidth=1.4,
          label="NFCI (right)")
ax2.set_ylabel("VIX", color=P["BLOOM_red"], fontweight="bold", fontsize=9.5)
ax_r.set_ylabel("Chicago Fed NFCI", color=P["BLOOM_navy"], fontweight="bold", fontsize=9.5)
ax2.tick_params(axis="y", labelcolor=P["BLOOM_red"], labelsize=8.5)
ax_r.tick_params(axis="y", labelcolor=P["BLOOM_navy"], labelsize=8.5)
ax2.tick_params(axis="x", labelsize=8.5, colors=P["subtext"])
ax2.set_title("VIX and NFCI · the two stress inputs · monthly mean",
              loc="left", fontweight="bold", fontsize=10.5, color=P["ink"])
ax2.xaxis.set_major_locator(mdates.YearLocator(3))
ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
lines1, labels1 = ax2.get_legend_handles_labels()
lines2, labels2 = ax_r.get_legend_handles_labels()
ax2.legend(lines1 + lines2, labels1 + labels2, loc="upper right", fontsize=8.5, frameon=False)
ax2.grid(alpha=0.28)
plt.show()
'''))

DEMO_STYLE_CELLS.append(new_markdown_cell(
    body(
        "<b>Left: monthly mean 30-day ATM IV per asset, smoothed for readability. The ordering is stable through the cycle — GLD and TLT at the bottom (12-25%), broad equity indices in the middle (15-25%), XLF and EEM at the top (20-35%) — which makes the inverse-vol weights interpretable rather than a one-day artefact. Right: VIX (red, left axis) and NFCI (navy, right axis) at monthly frequency. The two series move together most of the time, which is why combining them works. They diverge ahead of 2008 — credit (NFCI) deteriorated months before equity volatility responded — and during 2022, when NFCI spiked on lending-condition concerns while VIX stayed modest. A composite that takes both is sensitive to either kind of stress.</b>"
    )
))



# =============================================================================
# D. 2x2 skew/smile (Cell 10 of demo)
# =============================================================================
DEMO_STYLE_CELLS.append(new_markdown_cell(
    "---\n\n"
    "## Figure 4 — Cross-asset skew snapshot\n\n"
    + body(
        "Each leg\'s 30-day option chain summarised at three strikes: 25-delta call, "
        "at-the-money, 25-delta put. Top row: the sample-average shape across all "
        "trading days, equity legs and diversifier legs separately. Bottom row: the "
        "put-skew (25Δ-put minus ATM) over time."
    )
))

DEMO_STYLE_CELLS.append(new_code_cell('''\
"""Demo D — Per-asset skew snapshot (25dp / ATM / 25dc) + put-skew time series."""
import matplotlib.dates as mdates
from matplotlib import gridspec
P = PALETTE  # inlined in setup cell

ivs = {}
for tk in BOOK:
    iv_df = pd.read_parquet(DEMO / f"v3_iv_extras_{tk.lower()}.parquet")
    iv_df["date"] = pd.to_datetime(iv_df["date"])
    iv_df = iv_df.set_index("date")
    ivs[tk] = iv_df[["iv30_c25", "iv30_atm", "iv30_p25"]] * 100

mean_skew = pd.DataFrame({
    tk: [ivs[tk]["iv30_c25"].mean(), ivs[tk]["iv30_atm"].mean(), ivs[tk]["iv30_p25"].mean()]
    for tk in BOOK
}, index=["25Δ call", "ATM", "25Δ put"])

fig = plt.figure(figsize=(13, 8), facecolor="white")
gs = gridspec.GridSpec(2, 2, hspace=0.48, wspace=0.30)
fig.subplots_adjust(top=0.88, bottom=0.08, left=0.07, right=0.97)
fig_title(fig,
          "Figure 4 — Cross-asset skew snapshot",
          "25Δ-put / ATM / 25Δ-call IV (sample mean) · put-skew time series · 60-day smoothed")

# TL: skew curves, 4 equity legs
ax = fig.add_subplot(gs[0, 0])
equity_legs = ["SPY", "IWM", "XLK", "XLF"]
xs = list(range(3))
for tk in equity_legs:
    ax.plot(xs, mean_skew[tk], "o-", color=P[tk], markersize=6, linewidth=1.8,
            label=tk, markeredgecolor="white", markeredgewidth=1.0)
ax.set_xticks(xs); ax.set_xticklabels(mean_skew.index, fontweight="bold", color=P["ink"])
ax.set_ylabel("Mean IV (%)", fontweight="bold", color=P["ink"], fontsize=9.5)
ax.set_title("Skew shape · equity legs", loc="left", fontweight="bold", fontsize=10.5, color=P["ink"])
ax.legend(loc="upper left", fontsize=8.5, frameon=False)
ax.tick_params(labelsize=8.5, colors=P["subtext"])
ax.grid(alpha=0.28)

# TR: skew curves, 4 diversifying legs
ax2 = fig.add_subplot(gs[0, 1])
other_legs = ["EFA", "EEM", "GLD", "TLT"]
for tk in other_legs:
    ax2.plot(xs, mean_skew[tk], "o-", color=P[tk], markersize=6, linewidth=1.8,
             label=tk, markeredgecolor="white", markeredgewidth=1.0)
ax2.set_xticks(xs); ax2.set_xticklabels(mean_skew.index, fontweight="bold", color=P["ink"])
ax2.set_ylabel("Mean IV (%)", fontweight="bold", color=P["ink"], fontsize=9.5)
ax2.set_title("Skew shape · international + diversifiers",
              loc="left", fontweight="bold", fontsize=10.5, color=P["ink"])
ax2.legend(loc="upper left", fontsize=8.5, frameon=False)
ax2.tick_params(labelsize=8.5, colors=P["subtext"])
ax2.grid(alpha=0.28)

# BL: put-skew time series for the 4 broad-equity legs
ax3 = fig.add_subplot(gs[1, 0])
for tk in equity_legs:
    put_skew = (ivs[tk]["iv30_p25"] - ivs[tk]["iv30_atm"]).rolling(60, min_periods=1).mean()
    ax3.plot(put_skew.index, put_skew.values, color=P[tk], linewidth=1.1, label=tk, alpha=0.95)
ax3.axhline(0, color=P["ink"], linewidth=0.5, alpha=0.5)
ax3.set_ylabel("25Δ put − ATM (vol pts)", fontweight="bold", color=P["ink"], fontsize=9.5)
ax3.set_title("Put-skew · equity legs", loc="left", fontweight="bold", fontsize=10.5, color=P["ink"])
ax3.legend(loc="upper right", fontsize=8.5, ncol=4, frameon=False)
ax3.xaxis.set_major_locator(mdates.YearLocator(3))
ax3.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax3.tick_params(labelsize=8.5, colors=P["subtext"])
ax3.grid(alpha=0.28)

# BR: put-skew time series for the 4 diversifying legs
ax4 = fig.add_subplot(gs[1, 1])
for tk in other_legs:
    put_skew = (ivs[tk]["iv30_p25"] - ivs[tk]["iv30_atm"]).rolling(60, min_periods=1).mean()
    ax4.plot(put_skew.index, put_skew.values, color=P[tk], linewidth=1.1, label=tk, alpha=0.95)
ax4.axhline(0, color=P["ink"], linewidth=0.5, alpha=0.5)
ax4.set_ylabel("25Δ put − ATM (vol pts)", fontweight="bold", color=P["ink"], fontsize=9.5)
ax4.set_title("Put-skew · diversifying legs", loc="left", fontweight="bold", fontsize=10.5, color=P["ink"])
ax4.legend(loc="upper right", fontsize=8.5, ncol=4, frameon=False)
ax4.xaxis.set_major_locator(mdates.YearLocator(3))
ax4.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax4.tick_params(labelsize=8.5, colors=P["subtext"])
ax4.grid(alpha=0.28)
plt.show()
'''))

DEMO_STYLE_CELLS.append(new_markdown_cell(
    body(
        "<b>Top-left: average implied vol at 25Δ-call, ATM, and 25Δ-put for the broad-equity legs (SPY, IWM, XLK, XLF). The put leg sits clearly above the call leg in every case — out-of-the-money puts trade richer than out-of-the-money calls because the market consistently pays up for crash insurance on equities. Top-right: the same view for EFA, EEM, GLD, TLT. GLD and TLT smiles are essentially flat — the market does not price crash insurance on gold or Treasuries the way it does on equities. Bottom row: the put-skew (25Δ-put minus ATM) over time, equity legs on the left and diversifiers on the right. Equity put-skew widens to 4-6 vol-points during the 2008, 2018 and 2020 stress windows; the diversifier panel stays inside ±2 vol-points. This is the structural difference that justifies treating equities and diversifiers as separate risk-budget buckets.</b>"
    )
))



# =============================================================================
# E. 1x2 IV vs VIX comparison (Cell 47 of demo)
# =============================================================================
DEMO_STYLE_CELLS.append(new_markdown_cell(
    "---\n\n"
    "## Figure 5 — Data validation: SPY 30d ATM IV vs CBOE VIX\n\n"
    + body(
        "Sanity check on the implied-vol pipeline. Left: SPY 30-day ATM IV from "
        "our WRDS extract plotted against the published CBOE VIX index over the full sample. "
        "Right: scatter of one against the other with the y = x reference line."
    )
))

DEMO_STYLE_CELLS.append(new_code_cell('''\
"""Figure 5 — SPY 30d ATM IV vs CBOE VIX (compact, integrated title)."""
import matplotlib.dates as mdates
P = PALETTE

spy_iv_df = pd.read_parquet(DEMO / "v3_iv_extras_spy.parquet")
spy_iv_df["date"] = pd.to_datetime(spy_iv_df["date"])
spy_iv = spy_iv_df.set_index("date")["iv30_atm"] * 100
vix_series = macro_panel["VIX"].astype(float)
merged = pd.concat([spy_iv.rename("SPY_30d"), vix_series.rename("VIX")], axis=1).dropna()
corr = merged["SPY_30d"].corr(merged["VIX"])

fig, axes = plt.subplots(1, 2, figsize=(13, 4.6), facecolor="white",
                         gridspec_kw={"width_ratios": [2.4, 1], "wspace": 0.24})
fig.subplots_adjust(top=0.80, bottom=0.16, left=0.07, right=0.97)
fig_title(fig,
          "Figure 5 — Data validation: SPY 30d ATM IV vs CBOE VIX",
          f"correlation {corr:.3f} · {len(merged):,} daily observations · 2008-2024")

ax = axes[0]
ax.plot(merged.index, merged["SPY_30d"], "-", linewidth=1.0, color=P["SAAS_blue"],
        label="SPY 30d ATM IV (our pipeline)")
ax.plot(merged.index, merged["VIX"], "-", linewidth=1.0, color=P["BLOOM_red"],
        label="CBOE VIX (published)", alpha=0.95)
ax.fill_between(merged.index, merged["SPY_30d"], merged["VIX"],
                color=P["SAAS_blue"], alpha=0.10)
ax.set_xlabel("Date", fontweight="bold", color=P["ink"], fontsize=9.5)
ax.set_ylabel("Implied vol (%)", fontweight="bold", color=P["ink"], fontsize=9.5)
ax.set_title("Both series · time", loc="left", fontweight="bold", fontsize=10.5, color=P["ink"])
ax.legend(loc="upper left", fontsize=8.5, frameon=False)
ax.xaxis.set_major_locator(mdates.YearLocator(3))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.tick_params(labelsize=8.5, colors=P["subtext"])
ax.grid(alpha=0.28)

ax = axes[1]
ax.scatter(merged["SPY_30d"], merged["VIX"], s=6, alpha=0.40,
           color=P["SAAS_blue"], edgecolor="none")
lim_lo = min(merged.min()) - 2
lim_hi = max(merged.max()) + 2
ax.plot([lim_lo, lim_hi], [lim_lo, lim_hi], "--", color=P["BLOOM_red"],
        linewidth=1.4, label="y = x")
ax.set_xlim(lim_lo, lim_hi); ax.set_ylim(lim_lo, lim_hi)
ax.set_xlabel("SPY 30d ATM IV (%)", fontweight="bold", color=P["ink"], fontsize=9.5)
ax.set_ylabel("CBOE VIX (%)", fontweight="bold", color=P["ink"], fontsize=9.5)
ax.set_title("Scatter", loc="left", fontweight="bold", fontsize=10.5, color=P["ink"])
ax.legend(loc="upper left", fontsize=8.5, frameon=False)
ax.tick_params(labelsize=8.5, colors=P["subtext"])
ax.grid(alpha=0.28)
ax.set_aspect("equal")
plt.show()
'''))

DEMO_STYLE_CELLS.append(new_markdown_cell(
    body(
        "<b>Left: our pipeline's SPY 30-day at-the-money implied vol (blue) plotted against the published CBOE VIX index (red) over 2008-2024. Right: the same two series as a scatter against the y = x reference line. Correlation is 0.991 and the scatter sits tightly along the identity line across the full VIX range. CBOE's VIX is a 30-day SPX variance-swap fair-strike; our number is a constant-maturity 30-day ATM SPY IV — not the same construction, but the agreement is close enough that a pipeline error large enough to affect strategy results would be visible here. Every implied-vol series for the other seven ETFs comes through the identical pipeline.</b>"
    )
))



print(f"DEMO_STYLE_CELLS = {len(DEMO_STYLE_CELLS)} cells ({sum(1 for c in DEMO_STYLE_CELLS if c['cell_type']=='markdown')} md, {sum(1 for c in DEMO_STYLE_CELLS if c['cell_type']=='code')} code)")
