
# Urban Renewal, Demolition, and Housing Prices in Chinese Prefecture-Level Cities

This repository contains the analysis code accompanying the term paper:

> **“Urban Choices in the Era of Stock Urbanization:  
> Demolition, Urban Renewal, and Housing Prices  
> — Evidence from Panel Data of Chinese Prefecture-Level Cities”**

**Author:** Jichuan Huang  
**Program:** B.Sc. in Data Science and Big Data Technology, School of Big Data, Fudan University  
**Course:** *Economy and Society* (Instructor: Prof. Jianfeng Wu, Fudan School of Economics & China Center for Economic Research)

The repository is designed to provide a **clean, reproducible implementation** of the empirical analysis based on a **publicly available panel dataset** on Chinese urban renewal and housing prices.

---

## 1. Research Overview

The paper investigates whether **stronger urban renewal and demolition intensity** in existing built-up areas systematically leads to **higher housing prices** in Chinese cities in the context of “stock urbanization”, where incremental land expansion is increasingly constrained.

Using a panel of **203 prefecture-level (and above) cities** from **2015–2018** (403 city–year observations), the analysis estimates two-way fixed-effects models of the form:

- **Dependent variable**
  - `lhp_deflate`: log of inflation-adjusted average commercial housing prices
- **Key regressor**
  - `lnrenewal_lag`: lagged log urban renewal intensity (e.g., project area or investment amount)

### Main empirical findings (high-level)

1. **Near-zero average effect**

   In the full sample, the coefficient on lagged urban renewal intensity is **close to zero**, both statistically and economically, after controlling for city and year fixed effects.  
   → Simple “more demolition → higher prices” logic is **not supported** on average.

2. **Heterogeneous effects by long-run renewal intensity**

   When cities are grouped into **low**, **medium**, and **high** long-run renewal-intensity terciles:

   - In **medium-intensity** cities, higher renewal intensity is associated with a **borderline-significant positive effect** on housing prices (coefficient ≈ 0.031, significant at the 10% level).
   - In **low** and **high** intensity cities, the effect is statistically insignificant.

   This pattern is broadly consistent with an **“inverted-U”** story: **moderate and sustained** renewal seems more beneficial than either very low or very high demolition intensity.

3. **Policy interpretation**

   The results suggest that:

   - Large-scale demolition is **not a reliable average policy instrument** for raising housing prices in a stock-urbanization setting.
   - **Moderate, continuous, and “organic” renewal** appears more conducive to stable housing market performance than one-off, high-intensity demolition waves.
   - The **design and composition** of renewal (what and how to renew) matters more than the **raw volume** of demolished area.

All results are interpreted as **conditional correlations**, not fully identified causal effects, given the limitations of the data and identification strategy.

---

## 2. Repository Structure

A typical layout of this repository is:

```bash
.
├── analysis_renewal_panel.py      # Main analysis script
│                                  #  - data cleaning & variable construction
│                                  #  - fixed-effects regressions
│                                  #  - summary tables and figures
├── data/
│   └── 2013-2018renewal_empirical.dta   # Public city-level Stata dataset (see Section 3)
├── results/
│   ├── desc_core_vars.csv         # Descriptive statistics of core variables
│   ├── fe_regression_summary.csv  # Fixed-effects regression summaries (baseline & robustness)
│   ├── mean_by_group.csv          # Group means by long-run renewal-intensity terciles
│   ├── fig_trend_yearly_mean.png  # Annual mean trends (renewal intensity & prices)
│   ├── fig_coef_ci_baseline.png   # Baseline coefficient & 95% CI plot
│   └── fig_coef_hetero.png        # Heterogeneity coefficients by intensity group
└── README.md
````

You may adapt this structure as needed, but the script assumes a `data/` folder containing the `.dta` file and writes all outputs into `results/`.

---

## 3. Data

### 3.1 Dataset source and access

The analysis is based on a **publicly available** empirical dataset on urban renewal and housing prices in Chinese cities:

* **Filename:** `2013-2018renewal_empirical.dta`
* **Content:** city–year panel data on:

  * urban renewal / demolition intensity,
  * new commercial housing prices,
  * additional city-level controls and identifiers.

You can download the dataset directly from its public source.
For reproducibility, please:

1. Download the Stata file `2013-2018renewal_empirical.dta` from the original public source;
2. Place it under the `data/` directory of this repository.

> **Note:**
> Since URLs and hosting may evolve over time, please refer to the original course materials / dataset documentation / data provider’s website for the most recent download link and licensing information.

### 3.2 Core variables used in the analysis

The main variables used include:

* `city`
  Prefecture-level (and above) city identifier.

* `year`
  Calendar year (2013–2018).

* `lhp_deflate`
  Log of inflation-adjusted average commercial housing price in the city–year.

* `lnrenewal` (raw) / `lnrenewal_lag` (constructed)
  Log urban renewal intensity indicator (e.g. total area or investment volume).
  `lnrenewal_lag` is constructed as the **one-year lag** of `lnrenewal` and used as the key regressor.

* `d_lhp_deflate`
  Within-city first difference of `lhp_deflate` (housing price growth).
  Mainly used in robustness checks.

The baseline regression sample covers **2015–2018** for **203 cities** (403 usable city–year observations), with earlier years (2013–2014) used to construct lags and differences.

---

## 4. Software and Dependencies

The project is implemented in **Python**. A modern Python environment (e.g. Python 3.9 or later) is recommended.

Core dependencies:

* [`pandas`](https://pandas.pydata.org/)
  Data manipulation and I/O.

* [`numpy`](https://numpy.org/)
  Numerical computation.

* [`matplotlib`](https://matplotlib.org/)
  Visualization.

* [`linearmodels`](https://bashtage.github.io/linearmodels/)
  Panel data regression (e.g. `PanelOLS` with fixed effects).

* [`statsmodels`](https://www.statsmodels.org/) *(optional)*
  Additional diagnostics and regression utilities.

* [`openpyxl`](https://openpyxl.readthedocs.io/) *(optional)*
  Exporting tables to Excel, if needed.

You can install them via:

```bash
pip install pandas numpy matplotlib linearmodels statsmodels openpyxl
```

If you would like to pin a specific environment, you can generate a `requirements.txt`:

```bash
pip freeze > requirements.txt
```

and then share or recreate your environment with:

```bash
pip install -r requirements.txt
```

---

## 5. How to Reproduce the Results

Assuming you have cloned this repository and installed the required Python packages, follow these steps:

### Step 1 — Prepare the data

1. Download the public Stata dataset `2013-2018renewal_empirical.dta` from its original source.
2. Place it under:

   ```bash
   data/2013-2018renewal_empirical.dta
   ```

### Step 2 — Run the main analysis script

From the repository root:

```bash
python analysis_renewal_panel.py
```

The script will:

1. Read the Stata data;
2. Construct the panel index (`city`, `year`);
3. Create derived variables (e.g. `d_lhp_deflate`, long-run renewal-intensity groups);
4. Estimate two-way fixed-effects models using `PanelOLS` with city-clustered robust standard errors;
5. Write descriptive statistics, regression summaries, and figures into the `results/` directory.

### Step 3 — Check outputs

After successful execution, you should obtain:

* `results/desc_core_vars.csv`
  → Descriptive statistics of core variables (used in **Table 1** of the paper).

* `results/mean_by_group.csv`
  → Group means by long-run renewal-intensity terciles (used in **Table 2**).

* `results/fe_regression_summary.csv`
  → Regression coefficients, standard errors, p-values, confidence intervals, and R² within for:

  * `baseline_level`, `delta_dep`, `winsor_1_99`, `city_obs>=3` (baseline + robustness);
  * `hetero_renewal_low`, `hetero_renewal_middle`, `hetero_renewal_high` (heterogeneity analysis).

* `results/fig_trend_yearly_mean.png`
  → Annual mean trends for urban renewal intensity and inflation-adjusted housing prices (Figure 1).

* `results/fig_coef_ci_baseline.png`
  → Baseline coefficient (`lnrenewal_lag`) with 95% confidence interval (Figure 2).

* `results/fig_coef_hetero.png`
  → Coefficients by low / medium / high long-run renewal-intensity groups with 95% CIs (Figure 3).

These outputs map directly to the tables and figures referenced in the LaTeX manuscript.

---

## 6. Mapping Between Code and Paper

For clarity, here is the mapping from code outputs to the paper’s main tables and figures:

* **Table 1 (Descriptive statistics)**

  * Source: `results/desc_core_vars.csv`
  * Variables: `lhp_deflate`, `lnrenewal_lag`, `d_lhp_deflate`.

* **Table 2 (Mean comparison by renewal-intensity group)**

  * Source: `results/mean_by_group.csv`
  * Groups: low / medium / high long-run `lnrenewal_lag` terciles.

* **Table 3 (Baseline & robustness regressions)**

  * Source: `results/fe_regression_summary.csv`
  * Rows:

    * `baseline_level` → Column (1)
    * `delta_dep`      → Column (2)
    * `winsor_1_99`    → Column (3)
    * `city_obs>=3`    → Column (4)

* **Table 4 (Heterogeneity by renewal intensity)**

  * Source: `results/fe_regression_summary.csv`
  * Rows:

    * `hetero_renewal_low`
    * `hetero_renewal_middle`
    * `hetero_renewal_high`

* **Figure 1 (Annual mean trends)**

  * Source: `results/fig_trend_yearly_mean.png`

* **Figure 2 (Baseline coefficient & CI)**

  * Source: `results/fig_coef_ci_baseline.png`

* **Figure 3 (Heterogeneity coefficients & CIs)**

  * Source: `results/fig_coef_hetero.png`

---

## 7. Limitations and Intended Use

Although the underlying dataset is publicly available, the current implementation is written with a **course term paper** in mind:

* The identification strategy is intentionally **conservative**:

  * simple lag structure,
  * city and year fixed effects,
  * city-clustered robust standard errors,
  * no strong external instruments or quasi-experimental design.

* Hence, the paper and code **do not claim fully causal estimates**.
  The results should be read as **conditionally controlled correlations** given the chosen specification and sample.

Recommended uses of this repository:

* As a **reproducible example** of:

  * panel data cleaning,
  * variable construction,
  * fixed-effects estimation in Python using `linearmodels`;
* As a **teaching / learning resource** for empirical urban economics and public economics;
* As a **starting point** for more advanced work (e.g. instrumental variables, difference-in-differences, spatial models), provided that the researcher appropriately extends the methodology.

If you plan to build on this code for a more formal research project, please carefully review:

* the original data documentation and citation requirements;
* the econometric assumptions and potential identification issues.

---

## 8. Contact

For questions about the code or the empirical implementation (within the scope of academic use), please contact:

* **Email:** `23307110331@m.fudan.edu.cn`

Comments and suggestions on coding style, empirical strategy, or potential extensions are very welcome.

