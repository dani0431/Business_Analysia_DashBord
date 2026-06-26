# AI Business Analysis Dashboard

Upload a CSV/Excel dataset, get automatic statistics, interactive charts, and AI-generated business insights (via Claude).

## Setup (VS Code)

1. **Open this folder in VS Code.**

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate      # macOS/Linux
   venv\Scripts\activate         # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your API key:**
   - Copy `.env.example` to `.env`
   - Get an API key from https://console.anthropic.com
   - Paste it into `.env`:
     ```
     ANTHROPIC_API_KEY=sk-ant-xxxxxxxx
     ```

5. **Run the app:**
   ```bash
   streamlit run app.py
   ```
   It will open automatically in your browser at `http://localhost:8501`.

## How it works

- `data_loader.py` — reads and cleans uploaded CSV/Excel files
- `profiler.py` — computes stats, missing values, correlations; builds a compact text summary
- `ai_insights.py` — sends the summary (not raw data) to Claude and parses structured JSON insights
- `charts.py` — Plotly chart builders (bar, histogram, heatmap, time series, scatter)
- `app.py` — main Streamlit UI that ties it all together

## Notes

- Raw data is **never** sent to the AI — only the statistical profile (column stats, correlations, top categories, 5 sample rows). This keeps API costs low and avoids context limits on large files.
- AI insights are cached per profile (Streamlit `st.cache_data`) so you don't get charged repeatedly for the same dataset during a session.
- To switch models, change `MODEL_NAME` in `ai_insights.py`.

## Next steps / ideas to extend

- Add authentication if multiple users will use this
- Add export to PDF/PPT for the dashboard
- Add a "chat with your data" box that lets users ask free-form questions (send the question + profile to Claude)
- Migrate to FastAPI + React if you need a deployable multi-user product
