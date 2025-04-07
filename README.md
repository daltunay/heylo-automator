# Heylo Automator

Automates event registration for Heylo events with Midnight Runners.

## Setup

1. Install uv:

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2. Install Python dependencies:

    ```bash
    uv sync
    ```

3. Make sure you have Google Chrome installed

## Usage

Run the script with one of the following commands:

```bash
# For Montmartre Stairs Challenge
uv run python main.py montmartre

# For Tuesday Bootcamp Run
uv run python main.py bootcamp
```

You can also activate the virtual environment via `source .venv/bin/activate` to run the python script directly.
