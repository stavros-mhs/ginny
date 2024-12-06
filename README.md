## Disclaimer: This is Alpha Software
Demo depends on third party software and will allow the LLM to access your terminal! Do ***not*** run on non-virtualized environments. Handle with care.

## Install
Set up a virtual environment using:
```
python3 -m venv venv
. ./venv/bin/active
```
and then run 
```
poetry install
```

if you haven't install poetry, you can do it through ```pip install poetry``` or your package manager (e.g., ```apt install poetry``` on Ubuntu).

## Running
To run, the app needs access to an AI provider, the simplest one is through:

```export OPENAI_API_KEY="...you key here..."```

to run the demo use:

```poetry run main "what you want the LLM assistant to do for you"```

(keep in mind the System Prompt on blocks.py)