# Strategy notebook — audit table

Every quantitative claim in `final_project_notebook_v3.ipynb` ("Sizing, Not Signaling") with a recipe to verify it from the parquet/JSON files in this folder. All recipes assume:

```python
import json, numpy as np, pandas as pd
from pathlib import Path
D = Path(".")   # this folder

EQ      = pd.read_parquet(D / "v3_full_equity.parquet")["equity"]
pnl     = pd.read_parquet(D / "v3_full_pnl.parquet")["pnl"]
W       = pd.read_parquet(D / "v3_full_weights.parquet")
pnl_pa  = pd.read_parquet(D / "v3_full_pnl_per_asset.parquet")
regime  = pd.read_parquet(D / "v3_full_regime.parquet")["regime"]
gross   = pd.read_parquet(D / "v3_full_gross_mult.parquet")["gross_mult"]
stress  = pd.read_parquet(D / "v3_full_composite_stress.parquet")["composite_stress"]
signal  = pd.read_parquet(D / "v3_full_signal.parquet")
spot    = pd.read_parquet(D / "v3_spot_panel.parquet")
macro   = pd.read_parquet(D / "v3_macro_panel.parquet")
SPEC    = json.load(open(D / "v3_frozen_params.json"))

IS_END    = pd.Timestamp("2017-12-31")
OOS_START = pd.Timestamp("2018-01-01")
BOOK = ["SPY","IWM","EFA","EEM","XLK","XLF","GLD","TLT"]
```

## Headline performance

| Claim | Value | Recipe |
|---|---:|---|
| Sample range | 2008-01-02 to 2024-12-31, 4,279 trading days | `EQ.index.min(), EQ.index.max(), len(EQ)` |
| Starting capital | USD 1.00M | `EQ.iloc[0]` (= 1,000,000) |
| Ending equity | USD 1.48M | `EQ.iloc[-1]` |
| Total return | +48.2% | `EQ.iloc[-1] / EQ.iloc[0] - 1` |
| Maximum drawdown | -14.5% | `((EQ / EQ.cummax()) - 1).min()` |
| Full-sample Sharpe | +0.40 | `pnl.mean()/pnl.std()*np.sqrt(252)` |
| In-sample Sharpe (2008-2017) | +0.47 | `r=pnl.loc[:IS_END]; r.mean()/r.std()*np.sqrt(252)` |
| Out-of-sample Sharpe (2018-2024) | +0.28 | `r=pnl.loc[OOS_START:]; r.mean()/r.std()*np.sqrt(252)` |
| Strategy underperforms benchmark by | ~USD 1.16M | `EQ.iloc[-1] - 2.643e6` (see Benchmark section for full recipe) |

## Benchmark (daily-rebalanced equal-weight 8 ETFs, SIMPLE returns)

The earlier version of this audit and the earlier build script used `np.log(spot/spot.shift(1))` then `(1+r).cumprod()` to construct the benchmark. That mixes log-return arithmetic with simple-return compounding and under-reports the benchmark by roughly USD 1M. The corrected benchmark uses `spot.pct_change()`.

| Claim | Value | Recipe |
|---|---:|---|
| Benchmark ending equity (daily-rebalanced) | USD 2.64M | `r=spot.pct_change().fillna(0); w=pd.DataFrame(1/8,index=r.index,columns=BOOK); pb=(w.shift(1)*r).sum(axis=1); (1+pb).cumprod().iloc[-1]*1e6` |
| Benchmark max drawdown | -45.24% on 2009-03-09 | `eq=(1+pb).cumprod(); (eq/eq.cummax()-1).min()` |
| Benchmark annualised return | 7.16% | `pb.mean()*252` |
| Benchmark annualised vol | 16.93% | `pb.std()*np.sqrt(252)` |
| Benchmark Sharpe | +0.42 | `pb.mean()/pb.std()*np.sqrt(252)` |
| Strategy underperformance vs benchmark | USD 1.16M (2,643,324 − 1,482,105) | `EQ.iloc[-1] - eq.iloc[-1]*1e6` |
| For reference: true equal-weight buy-and-hold (no rebalancing) | USD 2.90M ending, -41.95% max DD | `init=(1e6/8)/spot.iloc[0]; bh=(spot*init).sum(axis=1); bh.iloc[-1]; (bh/bh.cummax()-1).min()` |

## Distributional moments of strategy daily returns

| Claim | Value | Recipe |
|---|---:|---|
| Skewness | -0.60 | `pnl.skew()` |
| Excess kurtosis | +3.60 | `pnl.kurtosis()` |
| n daily observations | 4,279 | `len(pnl.dropna())` |
| Student-t fit df | ≈3.9 | `from scipy import stats; stats.t.fit(pnl.dropna())[0]` |
| Daily mean return | +0.010% | `pnl.mean()*100` |

## Regime engine — time allocation

| Claim | Value | Recipe |
|---|---:|---|
| Calm (gate 1.5×) | 24% | `(regime==0).mean()` |
| Normal (gate 1.0×) | 62% | `(regime==1).mean()` |
| Stress (gate 0.5×) | 13% | `(regime==2).mean()` |
| Crisis (gate 0×) | 1.2%, ~52 days | `(regime==3).mean()`, `(regime==3).sum()` |

## Within-regime daily returns (Figure 7 / Figure 8)

| Claim | Value | Recipe |
|---|---:|---|
| Calm μ | +0.081%/d (~+8 bps/d) | `pnl[regime==0].mean()*100` |
| Normal μ | +0.004%/d | `pnl[regime==1].mean()*100` |
| Stress μ | -0.086%/d (~-9 bps/d) | `pnl[regime==2].mean()*100` |
| Crisis μ | -0.040%/d | `pnl[regime==3].mean()*100` |
| Calm n | 1,026 days | `(regime==0).sum()` |
| Crisis n | 52 days | `(regime==3).sum()` |

## Rolling 252-day Sharpe (Figure 5)

| Claim | Value | Recipe |
|---|---:|---|
| % of dates with positive trailing-year Sharpe | 71% | `r=pnl.rolling(252).mean()/pnl.rolling(252).std()*np.sqrt(252); (r>0).mean()` |
| Peak trailing-year Sharpe | +3.27 (≈ 2018-01) | `r.max()`, `r.idxmax()` |
| Trough trailing-year Sharpe | -2.14 (≈ 2022-11) | `r.min()`, `r.idxmin()` |

## Per-asset attribution (Figure 3 / 16)

Per-leg cumulative USD P&L on a USD 1M book, computed as `(pnl_pa.cumsum().iloc[-1] * 1e6).round().astype(int)`:

| Asset | Cumulative USD P&L |
|---|---:|
| XLK | +140,120 |
| SPY | +111,149 |
| GLD | +91,453 |
| XLF | +68,410 |
| IWM | +58,825 |
| TLT | +8,500 |
| EFA | -9,726 |
| EEM | -11,806 |

## IS → OOS per-leg Sharpe (Figure 10 / 16)

Recipe for any leg: `def sh(s,a,b): r=s.loc[a:b]; return r.mean()/r.std()*np.sqrt(252)` then `sh(pnl_pa["<TICKER>"],"2008","2017"), sh(pnl_pa["<TICKER>"],"2018","2024")`. For the book, replace `pnl_pa["<TICKER>"]` with `pnl`.

| Leg | IS Sharpe | OOS Sharpe |
|---|---:|---:|
| XLK | +0.70 | +0.64 |
| SPY | +0.63 | +0.44 |
| IWM | +0.47 | +0.01 |
| BOOK | +0.47 | +0.28 |
| XLF | +0.39 | +0.23 |
| GLD | +0.21 | +0.79 |
| TLT | +0.14 | -0.15 |
| EFA | +0.07 | -0.26 |
| EEM | -0.01 | -0.19 |

## iid Bootstrap Sharpe confidence intervals (Figure 2)

| Claim | Value | Recipe |
|---|---|---|
| IS Sharpe 5-95% CI | ≈ [-0.14, +0.99] | `rng=np.random.default_rng(42); r=pnl.loc[:IS_END].values; b=np.random.choice(r,(1000,len(r))); s=b.mean(1)/b.std(1)*np.sqrt(252); np.percentile(s,[5,95])` |
| OOS Sharpe 5-95% CI | ≈ [-0.33, +0.98] | same with `r=pnl.loc[OOS_START:].values` |
| Persistence test | Each point Sharpe sits inside the other window's bootstrap 5-95% interval | confirm `+0.28 ∈ [-0.14, +0.99]` and `+0.47 ∈ [-0.33, +0.98]` |

## Monthly return distribution (Figure 13)

| Claim | Value | Recipe |
|---|---:|---|
| Total months | 204 (Jan 2008 – Dec 2024) | `len(pnl.resample("ME").sum())` |
| Positive months | 118 (58%) | `m=pnl.resample("ME").sum()*100; (m>0).sum()` |
| Best month | +4.37% (Nov 2023) | `m.max()`, `m.idxmax()` |
| Worst month | -5.38% (Oct 2018) | `m.min()`, `m.idxmin()` |

## VIX vs strategy return (Figure 15)

| Claim | Value | Recipe |
|---|---:|---|
| Strategy bin-mean PnL at VIX≈12 | ≈ +0.08%/d | `vix=macro["VIX"].reindex(pnl.index).ffill(); from scipy import stats; b=stats.binned_statistic(vix,pnl*100,"mean",bins=15); b.statistic[0]` |
| Strategy bin-mean PnL at VIX≈20 | modestly negative, around -0.03 to -0.04%/d | `b.statistic[mid]` |
| Strategy bin-mean PnL at VIX>70 | ≈ -0.3%/d | `b.statistic[-1]` |

## Carry-trade five-axis diagnostic (Figure 9)

| Claim | Strategy | SPY benchmark | Recipe |
|---|---:|---:|---|
| P(r ≥ 0) | 0.552 | 0.549 | `(pnl>=0).mean()` |
| Skewness | -0.60 | -0.36 | `pnl.skew()`, `rets["SPY"].skew()` |
| ρ(r, SPY) | +0.73 | +1.00 | `pnl.corr(rets["SPY"])` — raw correlation; Figure 9 displays this on a negated axis labelled "−ρ" so the radar polygon shape matches carry-trade-exposure convention |
| ρ(r, ΔVIX) | -0.63 | -0.81 | `pnl.corr(macro["VIX"].diff().reindex(pnl.index).ffill())` |
| Excess kurtosis | +3.60 | +13.59 | `pnl.kurtosis()`, `rets["SPY"].kurtosis()` |

## Cross-asset correlation matrix (Figure 11)

| Claim | Value | Recipe |
|---|---:|---|
| Six-equity cluster cross-correlations | +0.7 to +0.9 | `rets=np.log(spot/spot.shift(1)).fillna(0); rets[["SPY","IWM","EFA","EEM","XLK","XLF"]].corr()` |
| TLT–equity correlations | ≈ -0.3 | `rets[["TLT","SPY","IWM","EFA","EEM","XLK","XLF"]].corr().loc["TLT"]` |
| GLD–equity correlations | near 0 (~±0.05) | `rets[["GLD","SPY","IWM","EFA","EEM","XLK","XLF"]].corr().loc["GLD"]` |

## Risk-return point statistics (Figure 12)

| Claim | Value | Recipe |
|---|---:|---|
| Per-asset (vol%, ret%, Sharpe over RF=2%) | see recipe | `for s in BOOK: r=rets[s]; v=r.std()*np.sqrt(252)*100; rr=r.mean()*252*100; print(s, round(v,1), round(rr,2), round((rr-2)/v,2))` |
| Strategy book | vol 6.4%, ret 2.5%, Sharpe (RF=2%) +0.08 | `pnl.std()*np.sqrt(252)*100`, `pnl.mean()*252*100` |

## Verifying the sizing rule itself (the full-loop reproduction)

The notebook's central claim is that per-leg weights follow

`w_{i,t} = (v_tgt · s_{i,t} · g_t) / (σ^IV_{i,t} · N)`

with v_tgt = 10%, N = 8. **Important:** weights `W` are held constant between weekly Friday rebalances while `signal`, `gross`, and `sigma_iv` move daily. Comparing all dates therefore returns a large diff. Filter to dates where `W` actually changes:

```python
v_tgt = SPEC["vol_target_per_leg"]   # 0.10
N = len(BOOK)

# Pull the 30-day ATM IV from each ticker's IV-extras file
ivs = {}
for tk in BOOK:
    iv_df = pd.read_parquet(D / f"v3_iv_extras_{tk.lower()}.parquet")
    ivs[tk] = iv_df.filter(regex="30.*atm", axis=1).iloc[:, 0]
sigma_iv = pd.DataFrame(ivs)
sigma_iv.index = pd.to_datetime(sigma_iv.index)

# Predicted weights from the formula
predicted_w = (v_tgt * signal * gross.values[:, None]) / (sigma_iv.reindex(W.index) * N)

# Filter to rebalance dates only (days where any weight actually changes)
changed = W[BOOK].diff().abs().sum(axis=1) > 1e-12
rebal_dates = W.index[changed]

diff = (W.loc[rebal_dates, BOOK] - predicted_w.loc[rebal_dates, BOOK]).abs()
print(f"Mean abs diff on rebalance dates: {diff.values.mean():.2e}")
print(f"Max  abs diff on rebalance dates: {diff.values.max():.2e}")
# Both should be near machine precision (< 1e-6)
```

## Frozen parameter spec (v3_frozen_params.json)

| Parameter | Value |
|---|---:|
| Per-leg vol target | 10% |
| Gross-exposure cap | 3.5× |
| Maximum regime multiplier (calm bucket) | 1.5× |
| Realised maximum gross exposure | ~1.31× |
| Regime multipliers (calm/normal/stress/crisis) | 1.5 / 1.0 / 0.5 / 0.0 |
| Regime percentile thresholds | 33 / 85 / 97 |
| Rebalance frequency | weekly, Friday close |
| Round-trip transaction cost | 4 bps |
| Drawdown kill-switch (resume) | -20% (resume at -7%) |
| IS Sharpe (frozen) | +0.4652 |
| OOS Sharpe (frozen) | +0.2811 |
| Full Sharpe (frozen) | +0.3961 |
| Full max drawdown | -14.47% |
| Full total return | +48.21% |

Verify any of these with `SPEC[…]`.
