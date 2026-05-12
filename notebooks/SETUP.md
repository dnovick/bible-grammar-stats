# Notebook Setup Guide

**Prerequisites:** Python 3.11 or later and VS Code must be installed.
- Python: https://www.python.org/downloads/
- VS Code: https://code.visualstudio.com/

---

## Quick setup — two commands

Open a terminal in the project root folder and run:

**Mac / Linux:**
```bash
bash setup.sh
python scripts/build_db.py
```

**Windows:**
```bat
setup.bat
python scripts/build_db.py
```

`setup.sh` / `setup.bat` creates the virtual environment, installs all dependencies,
and registers the Jupyter kernel (2–5 minutes on first run).

`scripts/build_db.py` builds the processed data cache that all notebooks rely on
(~5–30 seconds, one-time only — does not re-run on subsequent launches).

---

## After the scripts finish

1. Open VS Code. If you haven't already, install the **Jupyter** extension
   (click the Extensions icon in the left sidebar, search "Jupyter", install
   the one published by Microsoft).

2. Open any notebook — for example `notebooks/ot/verbs/qal.ipynb`.

3. Click **Select Kernel** in the top-right corner of the notebook, choose
   **Jupyter Kernel**, then select **Berean Bible Bots**.

4. Click **Run All** (or press `Shift+Enter` to run cells one at a time).

The first cell loads the MACULA data from the cache and runs in 1–2 seconds.

---

## Opening a new terminal later

VS Code auto-activates the `.venv` when it detects it in the workspace root.
If you open a standalone terminal outside VS Code, re-activate manually:

**Mac / Linux:**
```bash
source .venv/bin/activate
```

**Windows:**
```bat
.venv\Scripts\activate
```

---

## What the scripts do (for reference)

| Step | Command |
|---|---|
| Create virtual environment | `python3 -m venv .venv` |
| Activate | `source .venv/bin/activate` |
| Install dependencies | `pip install -r requirements-notebooks.txt` |
| Register Jupyter kernel | `python -m ipykernel install --user --name berean-bible-bots --display-name "Berean Bible Bots"` |
| Build data cache | `python scripts/build_db.py` |

Running `setup.sh` / `setup.bat` again is safe — it skips the venv creation if `.venv`
already exists and re-installs/upgrades packages as needed.
`scripts/build_db.py` only needs to be run once; subsequent runs simply rebuild the cache.

---

## Troubleshooting

**"Python 3.11 or later is required" error:**
Install Python 3.11+ from https://www.python.org/downloads/ and re-run
the script.

**The kernel "Berean Bible Bots" doesn't appear in the kernel picker:**
Make sure the script completed without errors. Click the kernel picker
again — VS Code may need a moment to refresh. If it still doesn't appear,
reload VS Code (`Cmd+Shift+P` → "Reload Window").

**"Module not found" error when running a cell:**
You selected a different kernel. Click the kernel name in the top-right
corner and switch to **Berean Bible Bots**.

**"File not found" or "No such parquet" error on the first cell:**
Run `python scripts/build_db.py` from the project root (with the `.venv`
activated). This only needs to be done once.

**Text-Fabric data download prompt on first run:**
Some notebooks use MACULA Hebrew/Greek data via Text-Fabric. On first use
it will ask to download the dataset (~200 MB). Follow the prompt — it only
downloads once and caches locally.

---

## Notebook index

See [README.md](README.md) for a full table of all notebooks and what each
one covers.
