# Team Command Hierarchy

To prevent circular dependencies, infinite loops, and "Spaghetti Delegation," the following reporting lines are strictly established:

## 1. Leadership Layer
- **Chief Economist (Main Agent)**:
    - **Commands**: All Subagents.
    - **Focus**: Strategy, high-level planning, and final user communication.

## 2. Synthesis Layer
- **`report_writer`**:
    - **Commands**: `econometrician`, `viz_expert`, `qualitative_analyst`.
    - **Focus**: Integrating models, visuals, and qualitative Research Briefs into a cohesive narrative.

## 3. Specialist Layer
- **`econometrician`**:
    - **Commands**: `data_transformer`.
    - **Focus**: Statistical modeling and forecasting. (Note: Does NOT command `viz_expert`).
- **`viz_expert`**:
    - **Commands**: `data_transformer`.
    - **Focus**: Professional-grade visualization.

## 4. Infrastructure Layer
- **`data_transformer`**:
    - **Commands**: `ceic_fetcher`, `bot_fetcher`, `eia_fetcher`.
    - **Focus**: Data engineering and preparation.

## 5. Field Layer (Fetchers & Data Discovery)
- **`ceic_fetcher`, `bot_fetcher`, `eia_fetcher`**: Raw data acquisition (Quantitative).
- **`qualitative_analyst`**: Deep economic research and crawling (Qualitative).
- **Commands**: None.
- **Focus**: Gathering qualitative economic, institutional, policy, and market context.

## Coordination Rules
- **One-Way Upward Feedback**: Subagents report results (file paths, summaries) back to their requester.
- **Dependency Check**: Before invoking an agent "below," always check `PROJECT_STATE.json` to see if the work has already been done.
- **Context Preservation**: Avoid nesting more than 3 agents deep. If a chain is too long, the Chief Economist should orchestrate the steps individually.
