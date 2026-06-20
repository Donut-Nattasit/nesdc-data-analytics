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
├── .claude/               # AI agent definitions, slash commands, and skill playbooks
├── .env.example           # Non-sensitive template for local API key configs
├── README.md              # This master workspace introduction portal
├── assets/                # Visual assets, logos, and custom localized typography
├── bin/                   # Launcher (python.ps1), setup utilities, and x13as.exe*
├── database/              # Central SQLite Databases (GTA, DBD, CEIC, IMF, MOC, WB)†
├── input/                 # Raw manual spreadsheets and user-supplied CSV files†
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

> **\* `bin/x13as.exe`** is required for X-13 ARIMA seasonal adjustment but is **not** stored in Git (it is a platform binary). Download the Windows X-13ARIMA-SEATS build from the [U.S. Census Bureau](https://www.census.gov/data/software/x13as.html) and place `x13as.exe` in `bin/`. The setup health check will flag it if missing.
>
> **† `database/`, `input/`, `output/`, and `report/`** hold large or machine-local artifacts and are gitignored. A fresh clone starts with these folders empty (the setup script recreates the structure). Source databases and raw input spreadsheets are shared out-of-band via OneDrive, not Git.

---

## ⚙️ How to Set Up This Project (For Economists)

Welcome! If you are new to coding, don't worry. This project is designed to run automatically. You just need to complete a one-time, automated setup process to get your computer ready.

Think of this setup like building a small "sandbox" on your computer. This sandbox will hold all the specific math calculators, charting tools, and AI agents the project needs, without messing up anything else on your computer.

### The 1-Step Setup Process
**Important:** Do not copy the sandbox from another teammate's computer! You must build your own.

To configure your computer, open your File Explorer, go to the project folder, and **double-click the `setup.bat` file**.

*(This will open a black Terminal window and run a Setup Wizard. It will automatically build your sandbox, install the math tools, ask you to paste your secret API passwords, and run a final health check!)*

That's it! Once the wizard finishes and shows a green "Health Check" table, you are 100% ready to start asking the AI to analyze data.
