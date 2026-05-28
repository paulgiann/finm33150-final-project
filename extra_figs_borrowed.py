"""Figures 17-18 — persistence quadrants, regime x asset Sharpe.

Neutral palette, deck-standard font sizes, compact figsize, centered output.
"""
from nbformat.v4 import new_markdown_cell, new_code_cell


def body(text):
    return ('<div style="font-size:1.13em; line-height:1.65; text-align:justify;">\n\n'
            + text
            + '\n\n</div>')


BORROWED_CELLS = []


# Figure 17 — Quadrant IS-vs-OOS scatter
BORROWED_CELLS.append(new_markdown_cell(
    "---\n\n"
    "## Figure 17 — The persistence diagnostic\n\n"
    + body(
        "Each asset\'s in-sample Sharpe (2008-2017, x-axis) plotted against its "
        "out-of-sample Sharpe (2018-2024, y-axis). The strategy book is the diamond. "
        "The dashed line marks y = x — points above improved out-of-sample, points "
        "below deteriorated. Quadrant tints encode the sign combination."
    )
))

BORROWED_CELLS.append(new_code_cell('''\
"""Figure 17 — IS vs OOS persistence quadrants (deck-standard fonts, compact)."""
P = PALETTE

def leg_sharpe(series, start, end):
    s = series.loc[start:end].dropna()
    if s.std() == 0 or len(s) < 30: return 0.0
    return s.mean()/s.std()*np.sqrt(252)

rows = []
for sec in BOOK:
    rows.append({"sec": sec,
                  "is":  leg_sharpe(pnl_pa[sec].astype(float), "2008-01-01", "2017-12-31"),
                  "oos": leg_sharpe(pnl_pa[sec].astype(float), "2018-01-01", "2024-12-31")})
book_is  = leg_sharpe(pnl.astype(float), "2008-01-01", "2017-12-31")
book_oos = leg_sharpe(pnl.astype(float), "2018-01-01", "2024-12-31")

fig, ax = plt.subplots(figsize=(13, 6.4), facecolor="white")
fig.subplots_adjust(top=0.84, bottom=0.13, left=0.08, right=0.96)
fig_title(fig,
          "Figure 17 — IS vs OOS Sharpe per leg (persistence quadrants)",
          "45° dashed line = perfect persistence · quadrants encode sign · diamond = book")

xs = [r["is"]  for r in rows]
ys = [r["oos"] for r in rows]
lo = min(min(xs), min(ys), book_is, book_oos) - 0.25
hi = max(max(xs), max(ys), book_is, book_oos) + 0.25

# Quadrant tints (Tableau-10)
ax.fill_between([0, hi], 0, hi, color="#76B7B2", alpha=0.34, zorder=0)   # +/+ Tableau teal
ax.fill_between([lo, 0], 0, hi, color="#F28E2B", alpha=0.28, zorder=0)   # -/+ Tableau orange
ax.fill_between([0, hi], lo, 0, color="#F28E2B", alpha=0.28, zorder=0)   # +/- Tableau orange
ax.fill_between([lo, 0], lo, 0, color="#E15759", alpha=0.30, zorder=0)   # -/- Tableau red

ax.plot([lo, hi], [lo, hi], color="#6B0F1A", linewidth=1.4, linestyle="--", alpha=0.75, zorder=1)
ax.axhline(0, color="#3D3D3D", linewidth=0.7, alpha=0.65, zorder=1)
ax.axvline(0, color="#3D3D3D", linewidth=0.7, alpha=0.65, zorder=1)

ax.text(hi*0.97, hi*0.97, "POS / POS", ha="right", va="top",
        fontsize=9, fontweight="bold", color="#1F6F6F", alpha=0.95)
ax.text(lo*0.97, hi*0.97, "NEG / POS", ha="left", va="top",
        fontsize=9, fontweight="bold", color="#9A5314", alpha=0.95)
ax.text(hi*0.97, lo*0.97, "POS / NEG", ha="right", va="bottom",
        fontsize=9, fontweight="bold", color="#9A5314", alpha=0.95)
ax.text(lo*0.97, lo*0.97, "NEG / NEG", ha="left", va="bottom",
        fontsize=9, fontweight="bold", color="#8C2D2F", alpha=0.95)

label_offsets = {"XLF": (-22, -8), "SPY": (7, 5), "IWM": (7, 5),
                 "EFA": (7, 5), "EEM": (7, 5), "XLK": (7, 5),
                 "GLD": (7, 5), "TLT": (7, 5)}
for r in rows:
    c = P[r["sec"]]
    ax.scatter([r["is"]], [r["oos"]], s=180, color=c, alpha=0.28, zorder=3)
    ax.scatter([r["is"]], [r["oos"]], s=85, color=c,
               edgecolor="white", linewidth=1.4, zorder=5)
    dx, dy = label_offsets.get(r["sec"], (7, 5))
    ha_ = "right" if dx < 0 else "left"
    ax.annotate(r["sec"], xy=(r["is"], r["oos"]),
                xytext=(dx, dy), textcoords="offset points",
                fontsize=9, fontweight="bold", color=c, ha=ha_,
                path_effects=[patheffects.withStroke(linewidth=1.8, foreground="white")])

ax.scatter([book_is], [book_oos], s=240, facecolors="none",
           edgecolors="#1E40AF", linewidths=2.0, marker="D", zorder=7)
ax.scatter([book_is], [book_oos], s=42, color="#1E40AF",
           marker="x", linewidths=1.7, zorder=8)
ax.annotate("BOOK", xy=(book_is, book_oos),
            xytext=(lo + 0.06, hi - 0.14),
            fontsize=9.5, fontweight="bold", color="#1E40AF", zorder=10,
            ha="left", va="center",
            arrowprops=dict(arrowstyle="-", color="#1E40AF", linewidth=0.9, alpha=0.7),
            bbox=dict(boxstyle="round,pad=0.28", facecolor="white",
                      edgecolor="#1E40AF", linewidth=1.2))
ax.text(lo + 0.06, hi - 0.22,
        f"IS {book_is:+.2f} → OOS {book_oos:+.2f}",
        fontsize=8, color="#1E40AF", zorder=10,
        ha="left", va="center", family="monospace",
        bbox=dict(boxstyle="round,pad=0.18", facecolor="white",
                  edgecolor="#CDD2D6", linewidth=0.5))

ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
ax.set_xlabel("In-sample Sharpe (2008-2017)", fontweight="bold", color=INK, fontsize=10)
ax.set_ylabel("Out-of-sample Sharpe (2018-2024)", fontweight="bold", color=INK, fontsize=10)
ax.tick_params(labelsize=9, colors=SLATE)
ax.grid(alpha=0.22)

plt.show()
'''))

BORROWED_CELLS.append(new_markdown_cell(
    body(
        "<b>Each circle plots one asset's in-sample (2008-2017) Sharpe on x against its out-of-sample (2018-2024) Sharpe on y; the diamond is the book; the dashed line is y = x (perfect persistence). Six observations sit in the POS/POS quadrant: SPY, IWM, XLK, XLF, GLD and the book itself. EEM is the lone NEG/NEG point. EFA and TLT moved from POS in-sample to NEG out-of-sample — the only two legs whose sign flipped between windows. The negative OOS flips are consistent with major macro headwinds, especially developed-international weakness after 2018 and the 2022 rate-tightening cycle for long-duration Treasuries. GLD is the one point clearly above the y = x line, meaning its OOS Sharpe (+0.79) was materially higher than its IS Sharpe (+0.21). The dominance of the POS/POS quadrant is the chart-level confirmation of Figure 7 — the IS-to-OOS decay is partial and asset-specific, not a wholesale collapse of the book.</b>"
    )
))


# Figure 18 — Regime x asset Sharpe heatmap with bootstrap CIs
BORROWED_CELLS.append(new_markdown_cell(
    "---\n\n"
    "## Figure 18 — Regime × asset Sharpe with bootstrap intervals\n\n"
    + body(
        "An 8×4 grid: rows are the eight assets, columns are the four regime "
        "buckets. Each cell shows the within-regime annualised Sharpe ratio; "
        "grey text marks cells whose bootstrap 5-95% interval still crosses zero."
    )
))

BORROWED_CELLS.append(new_code_cell('''\
"""Figure 18 — regime x asset Sharpe heatmap."""
import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap

# Diverging colormap for Sharpe values
# Negative Sharpe maps to low end, positive Sharpe to high end
SAAS_DIV = LinearSegmentedColormap.from_list(
    "purple_amber", ["#4A148C", "#A78BFA", "#FFFFFF", "#FBBF24", "#B8860B"], N=256
)

P = PALETTE

n_boot = 500
rng_h = np.random.default_rng(42)

def bootstrap_sharpe_arr(returns):
    r = returns.dropna().values
    if len(r) < 30 or r.std() == 0:
        return np.array([0.0])
    idx = rng_h.integers(0, len(r), size=(n_boot, len(r)))
    m = r[idx].mean(axis=1); s = r[idx].std(axis=1)
    return (m / np.where(s > 0, s, 1)) * np.sqrt(252)

reg_aligned = regime.reindex(pnl_pa.index).ffill()

rows = BOOK
cols = [0, 1, 2, 3]
point  = np.full((len(rows), len(cols)), np.nan)
lo_mat = np.full((len(rows), len(cols)), np.nan)
hi_mat = np.full((len(rows), len(cols)), np.nan)

for i, sec in enumerate(rows):
    for j, r_val in enumerate(cols):
        sub = pnl_pa[sec].astype(float)[reg_aligned == r_val].dropna()
        if len(sub) < 30 or sub.std() == 0:
            continue
        point[i, j] = sub.mean()/sub.std()*np.sqrt(252)
        b = bootstrap_sharpe_arr(sub)
        lo_mat[i, j], hi_mat[i, j] = np.percentile(b, [5, 95])

fig, ax = plt.subplots(figsize=(13, 5.4), facecolor="white")
fig.subplots_adjust(top=0.82, bottom=0.12, left=0.08, right=0.95)
fig_title(fig,
          "Figure 18 — Regime × asset Sharpe with bootstrap 5-95% intervals",
          "amber = positive · purple = negative · grey text marks cells where the bootstrap CI contains zero")

vmax = np.nanmax(np.abs(point)) * 1.05

# Heatmap cells fill a rectangular area (4 cols x 8 rows) -> rectangular cells in 11x5.4
for i in range(len(rows)):
    for j in range(len(cols)):
        v = point[i, j]
        x0, y0, w, h = j, len(rows)-1-i, 1, 1
        if np.isnan(v):
            ax.add_patch(plt.Rectangle((x0, y0), w, h, facecolor="#EFEFEF",
                                       edgecolor="white", linewidth=1))
            continue
        norm_v = (v + vmax) / (2*vmax)
        color = SAAS_DIV(norm_v)
        ax.add_patch(plt.Rectangle((x0, y0), w, h, facecolor=color,
                                   edgecolor="white", linewidth=1))
        ci_crosses = (lo_mat[i, j] < 0) and (hi_mat[i, j] > 0)
        text_color = "#7C7C7C" if ci_crosses else ("white" if abs(v) > vmax*0.45 else INK)
        ax.text(x0 + 0.5, y0 + 0.5, f"{v:+.2f}",
                ha="center", va="center", fontsize=10, fontweight="bold", color=text_color)

ax.set_xlim(0, len(cols)); ax.set_ylim(0, len(rows))
ax.set_xticks([j+0.5 for j in range(len(cols))])
ax.set_xticklabels([REGIME_LBL[r] for r in cols], fontsize=10, fontweight="bold", color=INK)
ax.set_yticks([len(rows)-1-i+0.5 for i in range(len(rows))])
ax.set_yticklabels(rows, fontsize=10, fontweight="bold", color=INK)
ax.tick_params(top=False, bottom=False, left=False, right=False)
ax.set_aspect("auto")
for sp in ("top", "right", "bottom", "left"): ax.spines[sp].set_visible(False)

norm = mpl.colors.Normalize(vmin=-vmax, vmax=vmax)
sm = mpl.cm.ScalarMappable(cmap=SAAS_DIV, norm=norm)
cb = fig.colorbar(sm, ax=ax, pad=0.02, shrink=0.85, label="Sharpe")
cb.outline.set_visible(False)
cb.ax.tick_params(labelsize=8.5, colors=SLATE)
cb.set_label("Sharpe", fontweight="bold", color=INK, fontsize=9.5)

plt.show()
'''))


BORROWED_CELLS.append(new_markdown_cell(
    body(
        "<b>Eight rows (assets) by four columns (regimes); each cell shows the within-regime annualised Sharpe ratio, with grey text where the bootstrap 5-95% CI still crosses zero. Calm column: every equity leg posts Sharpe between +1.9 (EEM) and +4.1 (SPY), all amber-gold and intervals clearly above zero. Stress and crisis columns: equity legs turn deeply negative (-2.5 to -3.6), shown in purple. GLD has positive point estimates in calm (+0.62) and stress (+1.04), but the bootstrap intervals are not cleanly above zero. TLT has a positive point estimate in the crisis bucket (+1.69), but that bucket has only 52 days, so the estimate should be treated as descriptive. The strongest pattern in the grid is simpler: equity sleeves perform well in calm regimes and poorly in stress regimes. The grid supports the purpose of the gate — reduce exposure when the regime shifts into states where sleeve returns are weaker — without claiming to show the no-gate counterfactual directly.</b>"
    )
))


print(f"BORROWED_CELLS = {len(BORROWED_CELLS)} cells")
