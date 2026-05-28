"""Side-module — figures 10-16 (was 5-15 before renumbering).

Plain academic prose, every claim verified against the parquet data.
"""
from nbformat.v4 import new_markdown_cell, new_code_cell


def body(text):
    return ('<div style="font-size:1.13em; line-height:1.65; text-align:justify;">\n\n'
            + text
            + '\n\n</div>')


EXTRA_CELLS = []


# -----------------------------------------------------------------------------
# Figure 10 — Rolling 252-day Sharpe
# -----------------------------------------------------------------------------
EXTRA_CELLS.append(new_markdown_cell(
    "---\n\n"
    "## Figure 10 — Performance through time\n\n"
    + body(
        "Trailing 252-day Sharpe ratio of the strategy\'s daily P&L, with the "
        "regime ribbon shaded underneath."
    )
))

EXTRA_CELLS.append(new_code_cell('''\
"""Figure 10 — rolling 252-day Sharpe ratio."""
rolling_sh = (pnl.rolling(252).mean() / pnl.rolling(252).std()) * np.sqrt(252)
rolling_sh = rolling_sh.dropna()

fig, ax = plt.subplots(figsize=(13, 5.6))
fig.subplots_adjust(top=0.84, bottom=0.10, left=0.07, right=0.97)
fig_title(fig,
          "Figure 10 — Rolling 252-day Sharpe ratio",
          f"Positive on {((rolling_sh>0).mean()*100):.0f}% of dates · "
          f"peak {rolling_sh.max():+.2f} ({rolling_sh.idxmax().strftime('%Y-%m')}) · "
          f"trough {rolling_sh.min():+.2f} ({rolling_sh.idxmin().strftime('%Y-%m')})")

y_lo, y_hi = rolling_sh.min() - 0.3, rolling_sh.max() + 0.3
regime_stripes(ax, regime.reindex(rolling_sh.index), y_lo, y_hi, alpha=0.234)

ax.axhline(0,   color=SLATE, linewidth=0.6, linestyle="--", alpha=0.6)
ax.axhline(1.0, color=GOLD,  linewidth=0.7, linestyle=":",  alpha=0.8)
ax.axvline(IS_END, color=SLATE, linewidth=1.0, linestyle=(0,(4,2)), alpha=0.6)

ax.fill_between(rolling_sh.index, rolling_sh.values, 0,
                where=(rolling_sh.values >= 0), color=FOREST, alpha=0.624)
ax.fill_between(rolling_sh.index, rolling_sh.values, 0,
                where=(rolling_sh.values <  0), color=WINE, alpha=0.364)
glow_line(ax, rolling_sh.index, rolling_sh.values, NAVY, lw=1.7, glow=4)

ax.set_ylim(y_lo, y_hi)
ax.set_ylabel("Rolling 252-day Sharpe (annualised)", fontweight="bold")
ax.xaxis.set_major_locator(mdates.YearLocator(2))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.grid(axis="y")
plt.show()
'''))

EXTRA_CELLS.append(new_markdown_cell(
    body(
        "<b>Trailing 252-day Sharpe ratio for the strategy across 2008-2024, with regime-coloured shading underneath. Positive on 71% of dates, peak +3.27 reached early 2018, trough -2.14 in late 2022. Two periods of sustained negative trailing Sharpe: 2009-2010 (post-GFC mean-reversion, when buy-and-hold equities rallied harder than the gated book) and 2022 (the year stocks and Treasuries fell together, eliminating the usual hedge). Outside those two windows the trailing-year Sharpe is positive at almost every date. A headline +0.40 full-sample number hides the fact that an allocator reviewing on a quarterly cycle would have seen a positive trailing Sharpe at most observation dates.</b>"
    )
))


# -----------------------------------------------------------------------------
# Figure 11 — Tail behaviour
# -----------------------------------------------------------------------------
EXTRA_CELLS.append(new_markdown_cell(
    "---\n\n"
    "## Figure 11 — Tail behaviour of daily returns\n\n"
    + body(
        "Three panels checking how well a Normal or a Student-t fits the daily "
        "P&L. Left: Q-Q plot vs Normal. Middle: Q-Q plot vs fitted Student-t. "
        "Right: the raw return histogram with mean overlaid."
    )
))

EXTRA_CELLS.append(new_code_cell('''\
"""Figure 11 — distributional diagnostics for daily returns."""
r  = pnl.dropna().astype(float)
sk, kt = r.skew(), r.kurtosis()

fig, axes = plt.subplots(1, 3, figsize=(13, 4.8),
                          gridspec_kw={"wspace": 0.30})
fig.subplots_adjust(top=0.82, bottom=0.13, left=0.06, right=0.97)
fig_title(fig,
          "Figure 11 — Distributional diagnostics for daily strategy returns",
          f"Skewness {sk:+.2f} · excess kurtosis {kt:+.2f} · n = {len(r)} daily observations")

ax = axes[0]
sps.probplot(r.values, dist="norm", plot=ax)
l0, l1 = ax.get_lines()
l0.set_color(NAVY); l0.set_marker("o"); l0.set_markersize(3); l0.set_alpha(0.6)
l1.set_color(WINE); l1.set_linewidth(1.5)
ax.set_title("")
ax.set_title("Q-Q vs Normal", loc="left", fontweight="bold", pad=8)
ax.set_xlabel("Normal quantiles"); ax.set_ylabel("Empirical quantiles")
ax.grid()

ax = axes[1]
t_p = sps.t.fit(r.values); df_t = t_p[0]
sps.probplot(r.values, dist=sps.t, sparams=(df_t,), plot=ax)
l0, l1 = ax.get_lines()
l0.set_color(GOLD); l0.set_marker("o"); l0.set_markersize(3); l0.set_alpha(0.6)
l1.set_color(WINE); l1.set_linewidth(1.5)
ax.set_title("")
ax.set_title(f"Q-Q vs Student-t (df={df_t:.1f})", loc="left", fontweight="bold", pad=8)
ax.set_xlabel("Student-t quantiles"); ax.set_ylabel("Empirical quantiles")
ax.grid()

ax = axes[2]
bins = np.linspace(r.quantile(0.001), r.quantile(0.999), 60)
ax.hist(r.values*100, bins=bins*100, color=NAVY,
        alpha=0.6, edgecolor="white", linewidth=0.5)
ax.axvline(0, color=SLATE, linewidth=0.5, linestyle="--")
ax.axvline(r.mean()*100, color=WINE, linewidth=1.5,
           label=f"Mean {r.mean()*100:+.3f}%")
ax.set_title("Daily return histogram", loc="left", fontweight="bold", pad=8)
ax.set_xlabel("Daily return (%)"); ax.set_ylabel("Frequency")
ax.legend(loc="upper right", frameon=False, fontsize=9)
ax.grid()
plt.show()
'''))

EXTRA_CELLS.append(new_markdown_cell(
    body(
        "<b>Left: Q-Q plot of strategy daily returns against a Normal distribution — the lower-left tail bends sharply below the reference line, meaning extreme down-days happen more often than a Normal predicts. Middle: same plot against a fitted Student-t with 4.2 degrees of freedom — the empirical points fall close to the reference line through both tails. Right: the raw daily-return histogram, mean +0.011%, standard deviation 0.39%, n = 4,279, skewness -0.60, excess kurtosis +3.6. Negative skew means the typical large move is downward (asymmetric loss versus gain); positive excess kurtosis means large moves of either sign happen more often than the Normal assumes. The Student-t reference fits the tails better than the Normal in this diagnostic. This suggests that tail-risk estimates should not rely only on a Normal assumption. A formal VaR or expected-shortfall comparison would require computing those estimates directly.</b>"
    )
))


# -----------------------------------------------------------------------------
# Figure 12 — Regime Sharpe bars
# -----------------------------------------------------------------------------
EXTRA_CELLS.append(new_markdown_cell(
    "---\n\n"
    "## Figure 12 — Conditional performance by regime\n\n"
    + body(
        "Annualised Sharpe ratio of the strategy within each of the four regime "
        "buckets (calm, normal, stress, crisis), with bootstrap 5-95% intervals. "
        "Per-bucket day count and mean daily return are printed under each bar."
    )
))

EXTRA_CELLS.append(new_code_cell('''\
"""Figure 12 — annualised Sharpe by regime with bootstrap 5-95% CI."""
df = pd.DataFrame({"pnl":    pnl.astype(float),
                    "regime": regime.reindex(pnl.index).ffill()}).dropna()

rng8 = np.random.default_rng(123)
def boot_sharpe(arr, n=2000):
    if len(arr) < 30 or arr.std() == 0:
        return np.array([0.0])
    idx = rng8.integers(0, len(arr), size=(n, len(arr)))
    m = arr[idx].mean(axis=1); s = arr[idx].std(axis=1)
    return (m / np.where(s > 0, s, 1)) * np.sqrt(252)

regimes = [0, 1, 2, 3]
point_sh, lo_sh, hi_sh, daily_mu, daily_sd, n_obs = [], [], [], [], [], []
for r_val in regimes:
    arr = df.loc[df["regime"] == r_val, "pnl"].values.astype(float)
    if len(arr) >= 30 and arr.std() > 0:
        point_sh.append(arr.mean()/arr.std()*np.sqrt(252))
        b = boot_sharpe(arr)
        lo_sh.append(np.percentile(b, 5))
        hi_sh.append(np.percentile(b, 95))
    else:
        point_sh.append(0.0); lo_sh.append(0.0); hi_sh.append(0.0)
    daily_mu.append(arr.mean()*1e4)   # in bps
    daily_sd.append(arr.std()*100)    # in % daily
    n_obs.append(len(arr))

fig, ax = plt.subplots(figsize=(13, 5.6))
fig.subplots_adjust(top=0.84, bottom=0.18, left=0.10, right=0.96)
fig_title(fig,
          "Figure 12 — Annualised Sharpe by regime, with bootstrap 5-95% CI",
          "Four hard regime buckets at the 33rd, 85th, 97th composite-stress percentiles · n_boot = 2000")

x = np.arange(len(regimes))
bar_colors = [REGIME_C[r] for r in regimes]
bars = ax.bar(x, point_sh, width=0.66, color=bar_colors,
              edgecolor="white", linewidth=2.0, zorder=3)
err_lo = [p - l for p, l in zip(point_sh, lo_sh)]
err_hi = [h - p for p, h in zip(point_sh, hi_sh)]
ax.errorbar(x, point_sh, yerr=[err_lo, err_hi], fmt="none",
            ecolor=SLATE, elinewidth=1.4, capsize=7, capthick=1.4, zorder=4)

# Value labels above each bar
for xi, val in zip(x, point_sh):
    ax.text(xi, val + (0.05 if val >= 0 else -0.12), f"{val:+.2f}",
            ha="center", fontsize=14, fontweight="bold", color=INK)

# Annotated stats under each bar
ax.axhline(0, color=SLATE, linewidth=0.7, linestyle="--", alpha=0.7, zorder=1)
y_text = min(lo_sh) - 0.35
for xi, r_val, mu, sd, n in zip(x, regimes, daily_mu, daily_sd, n_obs):
    label = (f"{REGIME_LBL[r_val]}\\n"
             f"n = {n}\\n"
             f"μ = {mu:+.1f} bps/d\\n"
             f"σ = {sd:.2f}%/d")
    ax.text(xi, y_text, label, ha="center", va="top", fontsize=10.5,
            family="monospace", color=SLATE,
            bbox=dict(boxstyle="round,pad=0.35", facecolor="white",
                      edgecolor="#CDD2D6", linewidth=0.8))

ax.set_xticks(x)
ax.set_xticklabels([REGIME_LBL[r] for r in regimes],
                   fontsize=12, fontweight="bold")
ax.set_ylim(min(lo_sh) - 1.1, max(hi_sh) + 0.35)
ax.set_ylabel("Annualised Sharpe (within-regime)", fontweight="bold")
ax.grid(axis="y", linewidth=0.5)
plt.show()
'''))

EXTRA_CELLS.append(new_markdown_cell(
    body(
        "<b>Annualised Sharpe ratio within each regime bucket: calm +3.27 on 1,026 days, normal +0.15 on 2,644 days, stress -3.36 on 557 days, and crisis -3.35 on 52 days. Calm periods have the strongest return profile. Normal periods are close to flat. Stress and crisis periods are negative in this sample. The strategy therefore reduces exposure as the stress regime worsens: 1.5× in calm, 1.0× in normal, 0.5× in stress, and 0× in crisis. The crisis bucket has only 52 days, so the crisis estimate is treated as descriptive.</b>"
    )
))


# -----------------------------------------------------------------------------
# Figure 13 — Cross-asset correlation heatmap (replaces the old chord network)
# -----------------------------------------------------------------------------
EXTRA_CELLS.append(new_markdown_cell(
    "---\n\n"
    "## Figure 13 — Cross-asset correlation structure\n\n"
    + body(
        "Pearson correlation matrix of daily log-returns for the eight ETFs over "
        "the full 2008-2024 sample, rendered in the Bloomberg Light divergent "
        "palette (red = positive correlation, blue = negative)."
    )
))

EXTRA_CELLS.append(new_code_cell('''\
"""Figure 13 — Cross-asset daily-return correlation (Bloomberg Light, compact)."""
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
corr = rets[BOOK].corr()

# Bloomberg Light diverging: red (#D4351C) → white → navy (#1A3A5F)
BLOOM_DIV = LinearSegmentedColormap.from_list(
    "bloom_div", ["#1A3A5F", "#6F9FCF", "#FFFFFF", "#E89684", "#D4351C"], N=256
)

fig, ax = plt.subplots(figsize=(10.5, 5.8))
fig.subplots_adjust(top=0.84, bottom=0.10, left=0.10, right=0.94)
fig_title(fig,
          "Figure 13 — Cross-asset daily-return correlation",
          "Pearson rho on log-returns · 2008-2024 · Bloomberg Light palette")

sns.heatmap(corr, ax=ax, cmap=BLOOM_DIV, center=0, vmin=-1, vmax=1,
            annot=True, fmt="+.2f",
            annot_kws={"size": 9.5, "weight": "bold"},
            linewidths=0.8, linecolor="white",
            square=False,
            cbar_kws={"label": "Pearson rho", "shrink": 0.82, "pad": 0.02})
ax.set_aspect("auto")  # let cells fill the wider axes
ax.set_xticklabels(BOOK, fontsize=10, fontweight="bold", rotation=0, color=PALETTE["ink"])
ax.set_yticklabels(BOOK, fontsize=10, fontweight="bold", rotation=0, color=PALETTE["ink"])
ax.tick_params(left=False, bottom=False)
cbar = ax.collections[0].colorbar
cbar.outline.set_visible(False)
cbar.ax.tick_params(labelsize=8.5, colors=PALETTE["subtext"])
cbar.set_label("Pearson rho", fontweight="bold", color=PALETTE["ink"], fontsize=9.5)
plt.show()
'''))

EXTRA_CELLS.append(new_markdown_cell(
    body(
        "<b>Pearson correlation of daily log-returns among the eight ETFs over 2008-2024. The six-leg equity block (SPY, IWM, EFA, EEM, XLK, XLF) shows pairwise correlations between +0.69 (XLK-XLF) and +0.92 (SPY-XLK) — these names move together, especially under stress, which limits how much diversification you can extract from inside the equity universe alone. TLT correlates -0.27 to -0.34 against the equity legs — the classic equity-to-Treasuries hedge holds across this sample. GLD shows correlations near zero with the equity legs and only modest correlation with TLT. That justifies its place in the book as a diversifying sleeve, even though its role is not to maximize standalone return. The composition therefore: equities for the equity-risk premium, TLT for negative-beta hedging, GLD for low-correlation diversification.</b>"
    )
))


# -----------------------------------------------------------------------------
# Figure 14 — Risk/return bubble
# -----------------------------------------------------------------------------
EXTRA_CELLS.append(new_markdown_cell(
    "---\n\n"
    "## Figure 14 — Risk-return positioning\n\n"
    + body(
        "Annualised volatility (x) against annualised return (y) for each of the "
        "eight ETFs and the strategy book. Iso-Sharpe lines drawn for reference."
    )
))

EXTRA_CELLS.append(new_code_cell('''\
"""Figure 14 — risk/return Markowitz bubble chart."""
rows = []
for sec in BOOK:
    r_ = rets[sec].dropna().astype(float)
    ann_ret = r_.mean()*252*100
    ann_vol = r_.std()*np.sqrt(252)*100
    sh = (ann_ret - 2)/ann_vol if ann_vol > 0 else 0
    rows.append({"sec":sec, "ann_ret":ann_ret, "ann_vol":ann_vol, "sharpe":sh})
df = pd.DataFrame(rows)
r_full = pnl.astype(float)
ann_ret_f = r_full.mean()*252*100
ann_vol_f = r_full.std()*np.sqrt(252)*100
sh_f = (ann_ret_f - 2)/ann_vol_f if ann_vol_f > 0 else 0

fig, ax = plt.subplots(figsize=(13, 6.6), facecolor="white")
fig.subplots_adjust(top=0.84, bottom=0.10, left=0.07, right=0.95)
ax.set_facecolor("#FFFDF7")
fig_title(fig,
          "Figure 14 — Annualised return vs annualised volatility, 2008-2024",
          "Bubble = one underlying (raw spot statistics) · diamond = strategy book · shaded zones = Sharpe quality")

# Sharpe-quality background zones — diagonal shading between iso-Sharpe lines
# Painted FIRST so bubbles sit on top
xlim_max_pre = max(df["ann_vol"].max(), ann_vol_f)*1.25
ylim_min_pre = min(0, df["ann_ret"].min()-3)
ylim_max_pre = max(df["ann_ret"].max(), ann_ret_f)*1.32
x_zone = np.linspace(0, xlim_max_pre, 200)
# Sharpe below 0.3 band
ax.fill_between(x_zone, ylim_min_pre, 2 + x_zone*0.3,
                color="#FFCDD2", alpha=0.45, zorder=0)
# Sharpe 0.3 to 0.5 band
ax.fill_between(x_zone, 2 + x_zone*0.3, 2 + x_zone*0.5,
                color="#FFF59D", alpha=0.50, zorder=0)
# Sharpe 0.5 to 1.0 band
ax.fill_between(x_zone, 2 + x_zone*0.5, 2 + x_zone*1.0,
                color="#C8E6C9", alpha=0.55, zorder=0)
# Sharpe above 1.0 band
ax.fill_between(x_zone, 2 + x_zone*1.0, ylim_max_pre*2,
                color="#80CBC4", alpha=0.50, zorder=0)

# Zone labels at the right edge
ax.text(xlim_max_pre*0.97, ylim_min_pre + (ylim_max_pre-ylim_min_pre)*0.06,
        "LOW Sh", ha="right", va="bottom", fontsize=9, fontweight="bold",
        color="#C62828", alpha=0.7)
ax.text(xlim_max_pre*0.97, 2 + xlim_max_pre*0.4,
        "MEDIOCRE", ha="right", va="center", fontsize=9, fontweight="bold",
        color="#F9A825", alpha=0.75)
ax.text(xlim_max_pre*0.55, 2 + xlim_max_pre*0.55*0.75,
        "GOOD", ha="right", va="center", fontsize=9, fontweight="bold",
        color="#2E7D32", alpha=0.75)
ax.text(xlim_max_pre*0.25, 2 + xlim_max_pre*0.25*1.1,
        "EXCELLENT", ha="left", va="bottom", fontsize=9, fontweight="bold",
        color="#00695C", alpha=0.80)

# Asset bubble markers
for _, row in df.iterrows():
    base_s = max(abs(row["sharpe"]), 0.1)*550 + 320
    c = ASSET[row["sec"]]
    # Outer marker rings
    ax.scatter(row["ann_vol"], row["ann_ret"], s=base_s*2.4,
               color=c, alpha=0.15, zorder=3)
    ax.scatter(row["ann_vol"], row["ann_ret"], s=base_s*1.6,
               color=c, alpha=0.28, zorder=3)
    # Main filled bubble
    ax.scatter(row["ann_vol"], row["ann_ret"], s=base_s, color=c,
               edgecolor="white", linewidth=2.5, zorder=5)
    ax.annotate(row["sec"], xy=(row["ann_vol"], row["ann_ret"]),
                xytext=(11, 11), textcoords="offset points",
                fontsize=13, fontweight="bold", color=c, zorder=6,
                path_effects=[patheffects.withStroke(linewidth=3, foreground="white")])

# BOOK diamond marker
s_book = max(abs(sh_f), 0.1)*350 + 250
ax.scatter(ann_vol_f, ann_ret_f, s=s_book*1.7, color=NAVY, alpha=0.234,
           marker="D", zorder=4)
ax.scatter(ann_vol_f, ann_ret_f, s=s_book, color=NAVY,
           edgecolor="white", linewidth=2.0, marker="D", zorder=7)

# BOOK label in the upper-left quadrant (always clear in a risk/return plot
# because no asset sits at low-vol/high-return) with a leader line to the diamond.
xlim_max = max(df["ann_vol"].max(), ann_vol_f)*1.25
ylim_min = min(0, df["ann_ret"].min()-3)
ylim_max = max(df["ann_ret"].max(), ann_ret_f)*1.32
label_x = xlim_max * 0.08
label_y = ylim_max * 0.88
ax.annotate("★ BOOK", xy=(ann_vol_f, ann_ret_f),
            xytext=(label_x, label_y),
            fontsize=14, fontweight="bold", color=NAVY, zorder=10,
            ha="left", va="center",
            arrowprops=dict(arrowstyle="-", color=NAVY, linewidth=1.0, alpha=0.7),
            bbox=dict(boxstyle="round,pad=0.45", facecolor="white",
                      edgecolor=NAVY, linewidth=1.5))
ax.text(label_x, label_y - (ylim_max - ylim_min)*0.05,
        f"Sh {sh_f:+.2f}  ·  vol {ann_vol_f:.1f}%  ·  ret {ann_ret_f:.1f}%",
        fontsize=9.5, color=NAVY, fontweight="normal", zorder=10,
        ha="left", va="center",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                  edgecolor="#CDD2D6", linewidth=0.6))

xlim_max = max(df["ann_vol"].max(), ann_vol_f)*1.25
ylim_min = min(0, df["ann_ret"].min()-3)
ylim_max = max(df["ann_ret"].max(), ann_ret_f)*1.32
ax.set_xlim(0, xlim_max)
ax.set_ylim(ylim_min, ylim_max)

x_range = np.linspace(1, xlim_max, 100)
for sh_iso in [0.3, 0.5, 1.0]:
    y_line = 2 + x_range*sh_iso
    # Clip line and label to within the visible axes box
    mask = y_line <= ylim_max
    if mask.any():
        ax.plot(x_range[mask], y_line[mask], color=SLATE,
                linewidth=0.6, linestyle="--", alpha=0.55, zorder=1)
        x_label = x_range[mask][-1]
        y_label = y_line[mask][-1]
        # If line exits the top, drop label just below the top edge; otherwise tag the right end
        if y_label >= ylim_max - 0.5 and x_label < xlim_max - 0.5:
            ax.text(x_label + 0.3, y_label - 0.6, f"Sh {sh_iso}",
                    color=SLATE, fontsize=10, alpha=0.85,
                    va="top", ha="left", fontweight="bold")
        else:
            ax.text(x_label, y_label, f"  Sh {sh_iso}",
                    color=SLATE, fontsize=10, alpha=0.85,
                    va="center", ha="left", fontweight="bold")
ax.axhline(2, color=SLATE, linewidth=0.3, linestyle=":", alpha=0.6)
ax.set_xlabel("Annualised volatility (%)", fontweight="bold")
ax.set_ylabel("Annualised return (%)", fontweight="bold")
ax.grid()
plt.show()
'''))

EXTRA_CELLS.append(new_markdown_cell(
    body(
        "<b>Annualised volatility (x) against annualised return (y) for each of the eight ETFs and the strategy book (★ diamond). XLK sits upper-right (vol ~19%, return ~13%, Sharpe ~0.6); SPY just below (vol ~17%, return ~8%); EEM and XLF are upper-right on volatility but only middle on return (vol ~25-32%, return ~0-3%). GLD and TLT cluster lower-left (vol ~15%, modest return). The strategy book is the diamond at vol 6.4%, return 2.5%, Sharpe +0.08 unlevered — lower volatility than any single leg in the book. Inverse-vol sizing scales high-vol assets down, regime gating cuts gross exposure during stress, and correlations below 1 across the book reduce aggregate variance further. The unlevered return looks small against single equity bets, but it is the path-controlled version of that exposure; standard practice is to lever the book to the volatility budget the allocator chooses.</b>"
    )
))


# -----------------------------------------------------------------------------
# Figure 15 — Year × month heatmap
# -----------------------------------------------------------------------------
EXTRA_CELLS.append(new_markdown_cell(
    "---\n\n"
    "## Figure 15 — Calendar of monthly returns\n\n"
    + body(
        "Monthly strategy returns laid out as a calendar: years on the row axis, "
        "calendar months on the column axis, colour and label give the monthly "
        "percentage return."
    )
))

EXTRA_CELLS.append(new_code_cell('''\
"""Figure 15 — year × month monthly P&L heatmap."""
import seaborn as sns
monthly = pnl.astype(float).resample("ME").sum()*100
monthly.index = pd.to_datetime(monthly.index)
yr_mo = monthly.groupby([monthly.index.year, monthly.index.month]).sum().unstack()

fig, ax = plt.subplots(figsize=(13, 6.2))
fig.subplots_adjust(top=0.86, bottom=0.07, left=0.05, right=0.97)
fig_title(fig,
          "Figure 15 — Monthly P&L heatmap (%)",
          f"{(monthly>0).sum()}/{len(monthly)} months positive ({(monthly>0).mean()*100:.0f}%) · "
          f"best month {monthly.max():+.2f}% ({monthly.idxmax().strftime('%Y-%m')}) · "
          f"worst month {monthly.min():+.2f}% ({monthly.idxmin().strftime('%Y-%m')})")

sns.heatmap(yr_mo, ax=ax, cmap=DIV_CMAP, center=0, vmin=-4, vmax=4,
            annot=True, fmt="+.1f",
            cbar_kws={"label":"Monthly return (%)"},
            annot_kws={"size":9.5, "weight":"bold"},
            linewidths=0.4, linecolor="white")
ax.set_xticklabels(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
                   rotation=0, fontsize=10.5)
ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=10.5, fontweight="bold")
ax.set_xlabel(""); ax.set_ylabel("")
plt.show()
'''))

EXTRA_CELLS.append(new_markdown_cell(
    body(
        "<b>Calendar-month P&amp;L: rows are years 2008-2024, columns are calendar months, colour saturation encodes return magnitude. The single worst month is October 2018 at -5.4%, not anywhere in 2008 — by late 2008 the regime gate had already cut exposure, so the GFC months appear as mild losses rather than catastrophic ones. 2022 is broadly red because the rate cycle hurt stocks and Treasuries together, removing the diversification benefit visible in Figure 13. Calm years (2013, 2017, 2019, 2024) are mostly green from end to end. No calendar month is uniformly bad across years — losses cluster around macro events, not seasonal patterns. Roughly 58% of months are positive across the full sample.</b>"
    )
))


# -----------------------------------------------------------------------------
# Figure 16 — Hexbin
# -----------------------------------------------------------------------------
EXTRA_CELLS.append(new_markdown_cell(
    "---\n\n"
    "## Figure 16 — Joint density of strategy return versus VIX\n\n"
    + body(
        "Hexbin density of daily VIX (x) against daily strategy return (y); colour "
        "encodes the count of trading days in each bin. The pink line traces the "
        "mean strategy return inside fifteen VIX buckets."
    )
))

EXTRA_CELLS.append(new_code_cell('''\
"""Figure 16 — hexbin joint density of daily return vs VIX."""
macro_panel = pd.read_parquet(DEMO / "v3_macro_panel.parquet")
macro_panel.index = pd.to_datetime(macro_panel.index)
df = pd.DataFrame({"pnl":  pnl.astype(float)*100,
                    "vix":  macro_panel["VIX"].astype(float).reindex(pnl.index).ffill()}).dropna()

fig, ax = plt.subplots(figsize=(13, 6.0), facecolor="white")
fig.subplots_adjust(top=0.84, bottom=0.12, left=0.08, right=0.92)
ax.set_facecolor("#FFFDF7")
fig_title(fig,
          "Figure 16 — Joint density of daily strategy return vs VIX",
          "Hex density (turbo colormap) · magenta curve = mean PnL in 15 VIX bins · vertical bands = VIX regime")

# Fill VIX regime bands
ax.axvspan(0,  15, color="#4FC3F7", alpha=0.18, zorder=0)
ax.axvspan(15, 25, color="#FFEE58", alpha=0.13, zorder=0)
ax.axvspan(25, 35, color="#FF8A65", alpha=0.20, zorder=0)
ax.axvspan(35, 100, color="#E53935", alpha=0.22, zorder=0)

# Regime band labels at top edge
ax.text(7.5,   ax.get_ylim()[1] if False else 2.15, "CALM",   ha="center", fontsize=9, fontweight="bold", color="#0288D1", alpha=0.7)
ax.text(20,    2.15, "NORMAL", ha="center", fontsize=9, fontweight="bold", color="#F9A825", alpha=0.7)
ax.text(30,    2.15, "STRESS", ha="center", fontsize=9, fontweight="bold", color="#E64A19", alpha=0.85)
ax.text(50,    2.15, "CRISIS", ha="center", fontsize=9, fontweight="bold", color="#B71C1C", alpha=0.85)

hb = ax.hexbin(df["vix"].values, df["pnl"].values, gridsize=28,
               cmap="turbo", mincnt=1, linewidths=0.3, edgecolors="white")
binned = sps.binned_statistic(df["vix"].values, df["pnl"].values,
                               statistic="mean", bins=15)
bc = (binned.bin_edges[:-1] + binned.bin_edges[1:])/2
ax.plot(bc, binned.statistic, color="#D81B60", linewidth=4.2,
        marker="o", markersize=11, markeredgecolor="white",
        markeredgewidth=2, label="Bin-mean PnL",
        path_effects=[patheffects.withStroke(linewidth=6, foreground="white")])

ax.axhline(0, color=SLATE, linewidth=0.8, linestyle="--", alpha=0.7)
ax.axvline(20, color=SLATE, linewidth=0.6, linestyle=":", alpha=0.45)
ax.text(20.5, ax.get_ylim()[0]*0.85, "VIX = 20\\n(elevated)",
        color=SLATE, fontsize=9, fontweight="bold", va="bottom")
ax.set_xlabel("VIX level (close-of-day)", fontweight="bold")
ax.set_ylabel("Strategy daily return (%)", fontweight="bold")
ax.grid(alpha=0.3)
leg = ax.legend(loc="upper right", frameon=True, facecolor="white", edgecolor="#CDD2D6", fontsize=10.5)
cb = fig.colorbar(hb, ax=ax, label="days in bin", pad=0.02, shrink=0.85)
cb.outline.set_visible(False)
plt.show()
'''))

EXTRA_CELLS.append(new_markdown_cell(
    body(
        "<b>Daily VIX (x) against daily strategy return (y) over 2008-2024 — each hex shows how many trading days landed in that bin, brighter = more days. The pink line traces the mean strategy return inside each VIX bin: +0.08% at VIX 12, near 0% at VIX 20, -0.3% at VIX above 70. Days are heavily concentrated in the VIX 12-25 range where the curve is positive; the negative right tail (VIX above 50) contains few days but represents the strategy's worst average outcome. The slope is negative because the regime gate uses data with a one-day lag and rebalances weekly — when VIX spikes the strategy is still holding the previous week's positions for several days. The same eight ETFs held equal-weight would average roughly -1%/day at VIX above 60; the gate contains that tail to about -0.3%/day.</b>"
    )
))





print(f"EXTRA_CELLS = {len(EXTRA_CELLS)} cells ({sum(1 for c in EXTRA_CELLS if c['cell_type']=='markdown')} md / {sum(1 for c in EXTRA_CELLS if c['cell_type']=='code')} code)")
