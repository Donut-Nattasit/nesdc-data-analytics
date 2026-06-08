# 📈 AI-Driven Economic Research Lab

Welcome to the **`data-analysis` workspace**, a specialized, modular, and AI-driven economic research and forecasting environment. 

This project is designed as a premium collaborative portal where human economists and specialized AI agents work together to execute sophisticated workflows. Our primary mission encompasses automated macroeconomic data acquisition, rigorous time-series transformations, advanced predictive modeling (machine learning and classical econometrics), qualitative policy research, and the generation of publication-ready reports.

---

## 🤖 Meet the Analytical Team (AI Agents)

This workspace operates using a highly structured, top-down multi-agent system. The team is led by the **Chief Economist & Strategic Orchestrator**, who manages the deployment and collaboration of 9 specialized subagents to fulfill your analytical requests.

* **`data_fetcher`**: The acquisition specialist. Expert in querying global APIs (CEIC, BOT, EIA, PortWatch, World Bank) and extracting complex records from local SQL databases.
* **`data_transformer`**: The data wrangler. Specializes in cleaning raw data, executing frequency conversions (e.g., daily to quarterly), applying seasonal adjustments, and enforcing the mandatory wide-format standard for timeseries modeling.
* **`db_manager`**: The database administrator. Custodian of the schema registry, handling SQLite query optimization, database migrations, and structural documentation.
* **`econometrician`**: The classical modeling and trade expert. Excels in statistical verification (ADF, ARDL, VAR, ARIMA) and advanced trade mathematics, such as calculating Revealed Comparative Advantage (RCA) and the Herfindahl-Hirschman Index (HHI).
* **`data_scientist`**: The modern predictive modeler. Focuses on advanced forecasting and nowcasting leveraging machine learning techniques (XGBoost, MIDAS, DFM).
* **`viz_expert`**: The visualization artist. An expert in producing professional-grade, publication-ready charts. Manages custom Matplotlib themes, rigorous layout standards, and localized Thai B.E. typography.
* **`qualitative_analyst`**: The researcher. A specialist in deep qualitative economic context, market research, policy analysis, and compiling fact-checked Research Briefs.
* **`weekly_news_writer`**: The intelligence synthesizer. Dedicated to periodically scanning, synthesizing, and reporting on high-impact economic news and market intelligence.
* **`report_writer`**: The senior editor. Synthesizes statistical findings, model diagnostics, visual assets, and qualitative briefs into comprehensive, formal economic reports (Markdown/HTML).

---

## 🗄️ Core Knowledge Repositories (Central Databases)

The workspace houses robust, locally optimized SQLite analytical databases directly in the `./database/` directory. These databases provide the team with instant access to extensive, localized historical intelligence:

* **`GTA.db`** (Global Trade Atlas): A massive repository of global transaction series mapping global trade flows, including HS 2-Digit chapters and ISO country metadata.
* **`DBD.db`** (Department of Business Development): Houses detailed TSIC industry structure mappings and comprehensive financial reports of registered Thai firms.
* **`CEIC.db`**: Features macroeconomic indicators and metadata sourced from CEIC World Trend Plus, tracking series like Middle East real GDP growth and historical Dubai oil prices.
* **`IMF.db`** (International Monetary Fund): Contains extensive macro metrics, including global GDP growth rates, ASEAN-4 GDP growth, and long-term inflation forecasts for Thailand.
* **`MOC.db`** (Ministry of Commerce): Tracks daily domestic product price series compiled structurally in wide format.
* **`WB.db`** (World Bank): Dedicated repository for storing global development indicators and macroeconomic metadata retrieved via the World Bank API.
* **`api_cache.db`**: An intelligent, persistent caching layer that intercepts queries to external endpoints (World Bank, EIA, BOT, PortWatch, etc.) to dramatically optimize fetch speeds and preserve API quotas.

---

## 🗺️ Workspace Infrastructure & Directory Map

To maintain a pristine environment, the lab operates on a strict **Modular Directory Standard**. Inputs, intermediates, source code, and final reports are dynamically and predictably routed:

```text
data-analysis/
├── .agents/               # AI Agent definitions, rules, and skill playbooks
├── .cursorrules           # Chief Economist system mandates and conventions
├── .env.example           # Non-sensitive template for local API key configs
├── README.md              # This master workspace introduction portal
├── assets/                # Visual assets, logos, and custom localized typography
├── bin/                   # Compiled binaries and environment resilience utilities
├── database/              # Central SQLite Databases (GTA, DBD, CEIC, IMF, MOC, WB)
│   └── data_dict/         # Static reference metadata and data dictionaries
├── input/                 # Raw manual spreadsheets and user-supplied CSV files
├── output/                # Consolidated artifact storage
│   ├── archive/           # Storage optimized archives
│   ├── chart/             # Standard, professional static visualizations (PNG)
│   ├── data/              # Workspace datasets (including raw API outputs)
│   └── model_summary/     # Saved model summaries and diagnostics (TXT)
├── report/                # Publication-grade Markdown/HTML reports and audits
├── src/                   # Python application codebase
│   ├── analysis/          # Analytical scripts and notebooks
│   ├── api/               # API Clients (CEIC, BOT, EIA, PortWatch, World Bank)
│   ├── data/              # Resampling, cleaning, and seasonal adjustment pipelines
│   ├── pipeline/          # Dedicated project orchestrators (e.g., Dubai Oil Prediction)
│   ├── utils/             # Helper utilities and registry automation
│   ├── visualization/     # Styling engines, chart utilities, and font localizers
│   └── validate_env.py    # Environment diagnostic and sanity checking suite
└── temp/                  # Session-specific temp files and logs (ignored in Git)
```

---

## ⚙️ Onboarding & Environment Resilience

This workspace is designed to sync seamlessly via OneDrive across different machine architectures and usernames. 

### Step 1: Provision Configuration
1. Duplicate `.env.example` and rename it to `.env` in the project root.
2. Fill in the required API keys for CEIC, BOT, EIA, and other connected external platforms.

### Step 2: Environment Resilience Check
If virtual environment paths break due to directory or machine differences, run the automated resilience utility to repair and align username-specific paths in the configuration (`pyvenv.cfg`):
```powershell
powershell -File .\bin\check_env.ps1
```

### Step 3: Run the Diagnostics Suite
Confirm that all third-party analytical libraries, local SQLite database engines, and binary dependencies are healthy:
```powershell
powershell -Command "$env:PYTHONPATH='.'; .\.venv\Scripts\python.exe src/validate_env.py"
```
*A successful diagnostic run will print a clean, green status audit table of all workspace modules.*
