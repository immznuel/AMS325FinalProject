import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mtick
import scipy.stats as stats
import statsmodels.api as sm

# Data Import and Configuration
file_path = r'C:/Users/Owner/Downloads/saeyjbmom4ynwg2m.csv'  
permnos_port = [89996, 90878, 89997, 91952, 89998, 90347]
tickers_port = ['VGT','VTI','VAW','BND','VPU','VDE']
weights = np.array([0.30,0.20,0.15,0.15,0.10,0.10])
permnos_all  = permnos_port + [12305]   # include S&P 500 ETF for comparison basis (CSPR permno 12305)

# 1) Load CRSP CSV file and pivot returns 
df = pd.read_csv(file_path, parse_dates=['date']).set_index('date')
ret_wide = (
    df[df['PERMNO'].isin(permnos_all)]
    .pivot(columns='PERMNO', values='RET')
    .sort_index()
    .loc[:, permnos_all]
)
# 2) Computing returns
port_ret  = ret_wide[permnos_port].dot(weights)   # portfolio monthly return
bench_ret = ret_wide[12305]                       # VOO monthly return

# 3) Cumulative returns 
cum_port  = (1 + port_ret).cumprod() - 1
cum_bench = (1 + bench_ret).cumprod() - 1

# 4) Drawdowns 
def drawdown(r):
    eq = (1+r).cumprod()
    return eq/eq.cummax() - 1

dd_port  = drawdown(port_ret)
dd_bench = drawdown(bench_ret)

# 5) 12-month Rolling metrics 
roll_vol_port  = port_ret.rolling(12).std() * np.sqrt(12)
roll_vol_bench = bench_ret.rolling(12).std() * np.sqrt(12)
roll_sharpe_port  = (port_ret.rolling(12).mean()*12) / (port_ret.rolling(12).std()*np.sqrt(12))
roll_sharpe_bench = (bench_ret.rolling(12).mean()*12) / (bench_ret.rolling(12).std()*np.sqrt(12))

# 6) Annuallized returns 
ann_port  = port_ret.resample('Y').apply(lambda x: (1+x).prod()-1)
ann_bench = bench_ret.resample('Y').apply(lambda x: (1+x).prod()-1)
years     = [d.year for d in ann_port.index]

# Plot I: Cumulative Returns 
fig, ax = plt.subplots(figsize=(10,6))
ax.plot(cum_port,  label='Portfolio', color='darkorange')
ax.plot(cum_bench, '--', label='VOO', color='navy')
ax.set_title('Cumulative Returns: Portfolio vs. VOO')
ax.set_xlabel('Date')
ax.set_ylabel('Cumulative Return (%)')
ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
ax.legend()
ax.grid(True)
plt.tight_layout()
plt.show()

# Plot II: Drawdown Comparison versus VOO
fig, ax = plt.subplots(figsize=(10,6))
ax.plot(dd_port,  label='Portfolio Drawdown', color='darkorange')
ax.plot(dd_bench, '--', label='VOO Drawdown', color='navy')
ax.set_title('Drawdown Comparison')
ax.set_xlabel('Date')
ax.set_ylabel('Drawdown (%)')
ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
ax.legend()
ax.grid(True)
plt.tight_layout()
plt.show()

# Plot III: 12-Month Rolling Volatility 
fig, ax = plt.subplots(figsize=(10,6))
ax.plot(roll_vol_port,  label='Portfolio Volatility', color='darkorange')
ax.plot(roll_vol_bench, '--', label='VOO Volatility', color='navy')
ax.set_title('12-Month Rolling Volatility')
ax.set_xlabel('Date')
ax.set_ylabel('Volatility (%)')
ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
ax.legend()
ax.grid(True)
plt.tight_layout()
plt.show()

# Plot IV: 12-Month Rolling Sharpe Ratio 
fig, ax = plt.subplots(figsize=(10,6))
ax.plot(roll_sharpe_port,  label='Portfolio Sharpe', color='darkorange')
ax.plot(roll_sharpe_bench, '--', label='VOO Sharpe', color='navy')
ax.set_title('12-Month Rolling Sharpe Ratio')
ax.set_xlabel('Date')
ax.set_ylabel('Sharpe Ratio (unitless)')
ax.legend()
ax.grid(True)
plt.tight_layout()
plt.show()

# Plot V: Annual Returns Comparison 
fig, ax = plt.subplots(figsize=(10,6))
ax.bar([y-0.2 for y in years], ann_port.values,  width=0.4, label='Portfolio', color='darkorange')
ax.bar([y+0.2 for y in years], ann_bench.values, width=0.4, label='VOO',       color='navy')
ax.set_title('Annual Returns: Portfolio vs. VOO')
ax.set_xlabel('Year')
ax.set_ylabel('Annual Return (%)')
ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
ax.legend()
ax.grid(True)
plt.tight_layout()
plt.show()

# Plot VI: Sector Contribution Analysis 
# Find dot product by weight, sum all
weighted_returns = ret_wide[permnos_port] * weights
total_contributions = weighted_returns.sum()

# Normalizing total portfolio return
portfolio_total_return = port_ret.sum()
percent_contributions = total_contributions / portfolio_total_return

# Contributions
print("\nSector Contribution to Total Portfolio Return")
for permno, ticker in zip(permnos_port, tickers_port):
    print(f"{ticker}: {percent_contributions[permno]:.2%} of total return")

# Bar chart for Distributions
plt.figure(figsize=(8, 5))
sns.barplot(x=tickers_port, y=[percent_contributions[p] for p in permnos_port], palette='tab10')
plt.title('Total Return Contribution by ETF (Relative %)')
plt.ylabel('Percent of Portfolio Return')
plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
plt.tight_layout()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()

# Heatmap Between ETF Operating Sectors
plt.figure(figsize=(8, 6))
sns.heatmap(ret_wide[permnos_port].corr(), annot=True, fmt=".2f",
            xticklabels=tickers_port, yticklabels=tickers_port, cmap='coolwarm')
plt.title('Correlation Between Sector ETFs')
plt.tight_layout()
plt.show()

# Best and Worst Years for the portfollio
sorted_annual = ann_port.sort_values()
print("\n Best and Worst Portfolio Years")
print(f"Best Year: {sorted_annual.idxmax().year} ({sorted_annual.max():.2%})")
print(f"Worst Year: {sorted_annual.idxmin().year} ({sorted_annual.min():.2%})")


# Plot VII: QQ-Plot vs Normal Distribution
sm.qqplot(port_ret, line='45', dist=stats.norm)
plt.title('QQ-Plot: Portfolio vs Normal Distribution')
plt.tight_layout()
plt.show()

# QQ-Plot vs Student's t-distribution
df_t, loc_t, scale_t = stats.t.fit(port_ret)
sm.qqplot(port_ret, line='45', dist=stats.t, distargs=(df_t,))
plt.title("QQ-Plot: Portfolio vs Student's t Distribution")
plt.tight_layout()
plt.show()

# Risk contributions: marginal risk * weight
cov_matrix = ret_wide[permnos_port].cov()
port_vol = np.sqrt(weights.T @ cov_matrix @ weights)
marginal_contrib = cov_matrix @ weights
risk_contrib = weights * marginal_contrib / port_vol

# Normalize to percentege
risk_contrib_percent = risk_contrib / risk_contrib.sum()

print("\nRisk Contribution by ETF")
for ticker, pct in zip(tickers_port, risk_contrib_percent):
    print(f"{ticker}: {pct:.2%} of total risk")

# Paired t‐test: is the mean difference portfollios != 0?
t_stat, p_value = stats.ttest_rel(port_ret, bench_ret)
print(f"Paired t‐test: t = {t_stat:.2f}, p = {p_value:.3f}")

# Kolmogorov–Smirnov test (KS Test): do the two porfollios come from the same distribution?
ks_stat, ks_p = stats.ks_2samp(port_ret, bench_ret)
print(f"KS‐test: statistic = {ks_stat:.3f}, p = {ks_p:.3f}")

