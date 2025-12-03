# analysis_renewal_panel.py
# -------------------------------------------------------
# Using city renewal intensity and housing price panel data, perform:
# 1) Descriptive statistics
# 2) Baseline Fixed Effects regression (City FE + Year FE, City-clustered robust SE)
# 3) Robustness checks: Differenced dependent variable, removing outliers (winsorizing), limiting sample
# 4) Heterogeneity analysis: Grouped by "High/Middle/Low" renewal intensity
# 5) Plotting: Annual mean trend + Baseline coefficient confidence interval plot
#
# Upon completion, all results will be saved in the ./results/ directory
# -------------------------------------------------------

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from linearmodels.panel import PanelOLS

# ======================= Basic Configuration =======================

DATA_PATH = "data/2013-2018renewal_empirical.dta"

# Adjust column names here if they differ from your data
CITY_COL = "city"           # City identifier
YEAR_COL = "year"           # Year
DEP_VAR = "lhp_deflate"     # Housing price (deflated log)
TREAT_VAR = "lnrenewal_lag" # Log of renewal intensity (lagged 1 period)

OUT_DIR = "results"

# Font settings (Commented out SimHei as it is for Chinese support; 
# standard fonts work fine for English)
# plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# ======================= Helper Functions =======================

def ensure_outdir(path=OUT_DIR):
    if not os.path.exists(path):
        os.makedirs(path)


def winsorize_series(s, lower=0.01, upper=0.99):
    """Winsorize series by quantiles to handle outliers."""
    q_low, q_high = s.quantile([lower, upper])
    return s.clip(lower=q_low, upper=q_high)


def run_fe_regression(df, dep, treat, controls=None, sample_label="full"):
    """
    Run City FE + Year FE PanelOLS regression on sample df.
    Model: y_it = beta * treat_it + gamma'X_it + mu_i + lambda_t + e_it
    Returns a result dictionary + the original regression result object.
    """
    if controls is None:
        controls = []

    cols = [CITY_COL, YEAR_COL, dep, treat] + controls
    data = df[cols].dropna().copy()

    # Set panel index
    data = data.set_index([CITY_COL, YEAR_COL]).sort_index()

    y = data[dep]
    X = data[[treat] + controls]

    # Fixed Effects Model
    mod = PanelOLS(y, X, entity_effects=True, time_effects=True)

    # Fit with clustered standard errors
    res = mod.fit(cov_type="clustered", cluster_entity=True)

    coef = res.params[treat]
    se = res.std_errors[treat]
    pval = res.pvalues[treat]
    ci_low = coef - 1.96 * se
    ci_high = coef + 1.96 * se

    nobs = int(res.nobs)
    n_city = data.index.get_level_values(0).nunique()
    n_year = data.index.get_level_values(1).nunique()
    r2_within = res.rsquared_within

    print("\n" + "=" * 80)
    print(f"Sample: {sample_label} | Dep Var: {dep} | Treat Var: {treat}")
    print("=" * 80)
    print(res.summary)

    result_dict = {
        "sample": sample_label,
        "dep_var": dep,
        "treat_var": treat,
        "coef": coef,
        "se": se,
        "p": pval,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "nobs": nobs,
        "n_city": n_city,
        "n_year": n_year,
        "r2_within": r2_within,
    }

    return result_dict, res


# ======================= Main Process =======================

def main():
    ensure_outdir()

    # ---------- 1. Load Data ----------
    print(">>> Loading data...")
    df = pd.read_stata(DATA_PATH)
    print("Data loaded. Shape:", df.shape)
    print("Columns:", df.columns.tolist())

    # If needed, filter for specific years (e.g., 2013-2018)
    # df = df[(df[YEAR_COL] >= 2013) & (df[YEAR_COL] <= 2018)].copy()

    # ---------- 2. Construct Derived Variables ----------
    # 2.1 Sort by city and year
    df = df.sort_values([CITY_COL, YEAR_COL]).copy()

    # 2.2 Housing price change (difference): Δlhp_deflate_it = lhp_deflate_it - lhp_deflate_i,t-1
    df["d_" + DEP_VAR] = df.groupby(CITY_COL)[DEP_VAR].diff()

    # 2.3 Construct "City Average Renewal Intensity" groups: High/Middle/Low (tercile)
    city_avg_renewal = df.groupby(CITY_COL)[TREAT_VAR].mean()
    q1, q2 = city_avg_renewal.quantile([0.33, 0.66])

    def map_renewal_group(x):
        if x <= q1:
            return "low"
        elif x <= q2:
            return "middle"
        else:
            return "high"

    renewal_group_map = city_avg_renewal.apply(map_renewal_group)
    df["renewal_group"] = df[CITY_COL].map(renewal_group_map)

    # 2.4 Count observations per city for sample restriction (e.g., at least 3 periods)
    city_obs_count = df.groupby(CITY_COL)[YEAR_COL].transform("count")
    df["city_obs_count"] = city_obs_count

    # Save processed data for inspection
    df.to_csv(os.path.join(OUT_DIR, "panel_data_cleaned.csv"), index=False)

    # ---------- 3. Descriptive Statistics ----------
    print(">>> Generating descriptive statistics...")

    # 3.1 General description of core variables
    desc_cols = [DEP_VAR, TREAT_VAR, "d_" + DEP_VAR]
    desc_table = df[desc_cols].describe().T
    desc_table.to_csv(os.path.join(OUT_DIR, "desc_core_vars.csv"))

    # 3.2 Mean by year (for trend plot)
    mean_by_year = (
        df.groupby(YEAR_COL)[[TREAT_VAR, DEP_VAR]].mean().reset_index()
    )
    mean_by_year.to_csv(os.path.join(OUT_DIR, "mean_by_year.csv"), index=False)

    # 3.3 Mean by "Renewal Intensity High/Mid/Low" groups
    mean_by_group = (
        df.groupby("renewal_group")[[TREAT_VAR, DEP_VAR]].mean().reset_index()
    )
    mean_by_group.to_csv(os.path.join(OUT_DIR, "mean_by_group.csv"), index=False)

    # ---------- 4. Plot Annual Trend ----------
    print(">>> Plotting annual mean trend...")

    plt.figure(figsize=(8, 4))
    plt.plot(
        mean_by_year[YEAR_COL],
        mean_by_year[TREAT_VAR],
        marker="o",
        label=TREAT_VAR,
    )
    plt.plot(
        mean_by_year[YEAR_COL],
        mean_by_year[DEP_VAR],
        marker="o",
        label=DEP_VAR,
    )
    plt.xlabel("Year")
    plt.ylabel("Mean Value")
    plt.title("Annual Mean Trend: Renewal Intensity vs. Housing Price (Deflated)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "fig_trend_yearly_mean.png"), dpi=300)
    plt.close()

    # ---------- 5. Regressions: Baseline + Robustness + Heterogeneity ----------
    print(">>> Running Fixed Effects regressions...")

    results_list = []

    # 5.1 Baseline Model: Price Level ~ Renewal Intensity (City FE + Year FE)
    base_res_dict, base_res = run_fe_regression(
        df, dep=DEP_VAR, treat=TREAT_VAR, controls=None, sample_label="baseline_level"
    )
    results_list.append(base_res_dict)

    # 5.2 Robustness 1: Use price change (difference) as dependent variable
    d_dep = "d_" + DEP_VAR
    d_res_dict, d_res = run_fe_regression(
        df, dep=d_dep, treat=TREAT_VAR, controls=None, sample_label="delta_dep"
    )
    results_list.append(d_res_dict)

    # 5.3 Robustness 2: Winsorize core variables (1%-99%) before regression
    df_w = df.copy()
    df_w[DEP_VAR] = winsorize_series(df_w[DEP_VAR])
    df_w[TREAT_VAR] = winsorize_series(df_w[TREAT_VAR])

    win_res_dict, win_res = run_fe_regression(
        df_w,
        dep=DEP_VAR,
        treat=TREAT_VAR,
        controls=None,
        sample_label="winsor_1_99",
    )
    results_list.append(win_res_dict)

    # 5.4 Robustness 3: Keep only cities with observation count >= 3
    df_long = df[df["city_obs_count"] >= 3].copy()
    long_res_dict, long_res = run_fe_regression(
        df_long,
        dep=DEP_VAR,
        treat=TREAT_VAR,
        controls=None,
        sample_label="city_obs>=3",
    )
    results_list.append(long_res_dict)

    # 5.5 Heterogeneity: Regressions by "High/Mid/Low" renewal groups
    for g_name, g_df in df.groupby("renewal_group"):
        label = f"hetero_renewal_{g_name}"
        g_res_dict, g_res = run_fe_regression(
            g_df,
            dep=DEP_VAR,
            treat=TREAT_VAR,
            controls=None,
            sample_label=label,
        )
        results_list.append(g_res_dict)

    # ---------- 6. Save All Regression Results (for tabulation) ----------
    results_df = pd.DataFrame(results_list)
    results_df.to_csv(os.path.join(OUT_DIR, "fe_regression_summary.csv"), index=False)
    print(">>> Regression results saved to fe_regression_summary.csv")

    # ---------- 7. Plot Coefficient + 95% CI (Baseline) ----------
    print(">>> Plotting confidence interval for baseline treatment effect...")

    coef = base_res_dict["coef"]
    ci_low = base_res_dict["ci_low"]
    ci_high = base_res_dict["ci_high"]

    plt.figure(figsize=(6, 2.5))
    y_pos = [0]  # Only one coefficient
    plt.errorbar(
        x=[coef],
        y=y_pos,
        xerr=[[coef - ci_low], [ci_high - coef]],
        fmt="o",
        capsize=5,
    )
    plt.axvline(x=0, linestyle="--", linewidth=1)
    plt.yticks(y_pos, [DEP_VAR])
    plt.xlabel("Coefficient and 95% Confidence Interval")
    plt.title(f"Estimated Effect of Renewal Intensity ({TREAT_VAR}) on Housing Price ({DEP_VAR})")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "fig_coef_ci_baseline.png"), dpi=300)
    plt.close()
    
# ---------- 8. Plot "High/Mid/Low Renewal Group" Coefficient Comparison ----------
    print(">>> Plotting coefficient confidence intervals for different renewal intensity groups...")

    # In step 5.5 above, the sample names we assigned were:
    # "hetero_renewal_low", "hetero_renewal_middle", "hetero_renewal_high"
    hetero_keys = ["hetero_renewal_low", "hetero_renewal_middle", "hetero_renewal_high"]
    hetero_labels = ["Low Renewal Group", "Middle Renewal Group", "High Renewal Group"]

    coefs = []
    ci_lows = []
    ci_highs = []

    for k in hetero_keys:
        # Find the corresponding result dictionary in results_list
        r = next(item for item in results_list if item["sample"] == k)
        coefs.append(r["coef"])
        ci_lows.append(r["ci_low"])
        ci_highs.append(r["ci_high"])

    y_pos = np.arange(len(hetero_keys))

    # Calculate error bar lengths
    xerr_lower = [c - cl for c, cl in zip(coefs, ci_lows)]
    xerr_upper = [ch - c for c, ch in zip(coefs, ci_highs)]

    plt.figure(figsize=(6, 3))
    plt.errorbar(
        x=coefs,
        y=y_pos,
        xerr=[xerr_lower, xerr_upper],
        fmt="o",
        capsize=5,
    )
    plt.axvline(x=0, linestyle="--", linewidth=1)
    plt.yticks(y_pos, hetero_labels)
    plt.xlabel("Coefficient and 95% Confidence Interval")
    plt.title("Estimated Effect of lnrenewal_lag by Renewal Intensity Group")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "fig_coef_hetero.png"), dpi=300)
    plt.close()

    print(">>> All analyses completed. Results output to ./results/ directory.")


if __name__ == "__main__":
    main()
