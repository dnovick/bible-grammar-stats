# Notebook Setup Guide

This guide walks you through getting the notebooks running in VS Code.
It should take about 5–10 minutes.

**Prerequisites:** Python 3.11 or later and VS Code must be installed.
If you need them:
- Python: https://www.python.org/downloads/
- VS Code: https://code.visualstudio.com/

---

## Step 1 — Open the project in VS Code

Open VS Code and use **File → Open Folder**, then select the
`berean-bible-bots` folder (the one that contains this `notebooks/`
directory).

---

## Step 2 — Open a terminal in VS Code

Use **Terminal → New Terminal** from the menu bar.
The terminal should open at the root of the project folder.

---

## Step 3 — Create the virtual environment

Paste this command and press Enter:

```bash
python3 -m venv .venv
```

This creates a `.venv` folder in the project root. It only needs to be
done once.

---

## Step 4 — Activate the virtual environment

**Mac / Linux:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

You should see `(.venv)` appear at the start of your terminal prompt.

> You will need to activate the venv each time you open a new terminal
> session. VS Code can do this automatically — see the tip at the end.

---

## Step 5 — Install the dependencies

```bash
pip install -r requirements-notebooks.txt
```

This installs Jupyter, pandas, matplotlib, and all other required
packages. It may take a few minutes the first time.

---

## Step 6 — Install the VS Code Jupyter extension

In VS Code, click the **Extensions** icon in the left sidebar (or press
`Ctrl+Shift+X` / `Cmd+Shift+X`), search for **Jupyter**, and install
the extension published by Microsoft.

---

## Step 7 — Register the venv as a Jupyter kernel

With the venv still active (you should see `(.venv)` in your terminal),
run:

```bash
python3 -m ipykernel install --user --name berean-bible-bots --display-name "Berean Bible Bots"
```

This registers the venv with Jupyter so VS Code can find it. It only
needs to be done once.

---

## Step 8 — Open a notebook and select the kernel

1. In the VS Code file explorer, navigate to `notebooks/` and open any
   `.ipynb` file (for example, `ot/verbs/qal.ipynb`).
2. In the top-right corner of the notebook, click **Select Kernel**.
3. Choose **Jupyter Kernel**, then select **Berean Bible Bots**.

VS Code will remember this kernel choice for future notebooks in the
same workspace.

---

## Step 9 — Run the notebook

Click **Run All** at the top of the notebook, or run cells one at a
time with `Shift+Enter`.

The first run loads the MACULA data files and may take 10–20 seconds.
Subsequent cells run much faster.

---

## Tip — Auto-activate the venv in VS Code

To have VS Code automatically activate `.venv` whenever you open a
terminal:

1. Open **Settings** (`Cmd+,` / `Ctrl+,`)
2. Search for `python.terminal.activateEnvironment`
3. Make sure it is checked (enabled)

VS Code also auto-selects `.venv` as the default Python interpreter if
it detects it in the workspace root.

---

## Notebook index

See [README.md](README.md) for a full table of all notebooks and what
each one covers.

---

## Troubleshooting

**The kernel "Berean Bible Bots" doesn't appear in the kernel picker:**
Make sure you ran the `ipykernel install` command in Step 7 with the
venv active. After running it, click the kernel picker again — VS Code
may need a moment to refresh. If it still doesn't appear, reload VS
Code (`Cmd+Shift+P` → "Reload Window").

**"Module not found" error when running a cell:**
Make sure you selected the **Berean Bible Bots** kernel (Step 8), not
the system Python. Click the kernel name in the top-right corner to
change it.

**The venv prompt disappeared / `(.venv)` is not showing:**
Re-run the activation command from Step 4.

**Text-Fabric data download prompt on first run:**
Some notebooks use MACULA Hebrew/Greek data via Text-Fabric. On first
use it will ask to download the dataset (~200 MB). Follow the prompt —
it only downloads once and caches locally.
