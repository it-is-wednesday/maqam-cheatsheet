python := ".venv/bin/python"
pip := ".venv/bin/pip"

watch:
    watchexec -w maqamat.py -w ./templates -w ./data -- python maqamat.py
