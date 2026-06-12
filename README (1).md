# ARM Market Intelligence — Public Demo App

Fully standalone Streamlit app with synthetic data.  
No Databricks, no credentials, no setup beyond Python.

---

## Option 1 — Streamlit Community Cloud (FREE, public URL in 2 min)

This is the recommended option. Gives you a permanent public URL like:  
`https://your-app-name.streamlit.app`

### Step-by-step

**1. Create a free GitHub repo**
- Go to https://github.com/new
- Name it: `arm-mi-demo` (or anything you like)
- Set it to **Public**
- Click **Create repository**

**2. Upload the two files**
Upload both files to the repo root:
- `app.py`
- `requirements.txt`

You can drag-and-drop directly on the GitHub web UI.

**3. Create a free Streamlit account**
- Go to https://share.streamlit.io
- Sign in with GitHub (same account)

**4. Deploy**
- Click **New app**
- Repository: `your-username/arm-mi-demo`
- Branch: `main`
- Main file path: `app.py`
- Click **Deploy!**

Streamlit installs the packages from `requirements.txt` automatically.  
Your app is live at `https://arm-mi-demo.streamlit.app` in about 60 seconds.  
**Share that URL with anyone — no login required.**

---

## Option 2 — Run locally (zero cost, local access only)

```bash
# Install Python 3.10+ if not already installed
pip install streamlit pandas plotly numpy

# Run
streamlit run app.py
```

Opens at http://localhost:8501 — only you can see it.

---

## Option 3 — Render.com (free tier, always-on public URL)

1. Push the two files to a GitHub repo (same as Option 1 step 1-2)
2. Go to https://render.com → New → Web Service
3. Connect your GitHub repo
4. Set:
   - **Runtime**: Python 3
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
5. Click **Create Web Service**

Free tier sleeps after 15 min idle. Paid tier ($7/mo) stays always-on.

---

## Option 4 — Hugging Face Spaces (free, always-on)

1. Go to https://huggingface.co/new-space
2. Choose **Streamlit** as the SDK
3. Upload `app.py` and `requirements.txt`
4. Your app is live at `https://huggingface.co/spaces/your-username/arm-mi-demo`

---

## Files in this package

| File               | Purpose                              |
|--------------------|--------------------------------------|
| `app.py`           | Full 5-tab Streamlit dashboard       |
| `requirements.txt` | Python dependencies (4 packages)     |
| `README.md`        | This deployment guide                |

---

## Connecting to real Databricks (production upgrade)

Once you want live data instead of synthetic data, add these secrets in  
Streamlit Cloud → App settings → Secrets:

```toml
DATABRICKS_HOST      = "https://your-workspace.azuredatabricks.net"
DATABRICKS_TOKEN     = "your-pat-token"
DATABRICKS_HTTP_PATH = "/sql/1.0/warehouses/your-warehouse-id"
```

Then swap the synthetic data functions in `app.py` for the  
`query()` function from the production `arm_mi_app.py`.
