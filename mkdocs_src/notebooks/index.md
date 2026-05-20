# Notebooks

Interactive analysis notebooks covering the full `bible_grammar` toolkit — Hebrew OT, Greek NT, Septuagint, Peshitta, and Targumim.

Each notebook below is rendered statically with its outputs. To run a notebook interactively, see [Running Notebooks Locally](#running-locally).

## Running Locally

To execute notebooks on your own machine:

```bash
git clone https://github.com/dnovick/berean-bible-bots.git
cd berean-bible-bots
python -m venv .venv && source .venv/bin/activate
pip install -r binder/requirements.txt
# Download processed data (one-time, ~295 MB)
bash binder/postBuild
jupyter lab
```

Then open any notebook from the `notebooks/` directory.
