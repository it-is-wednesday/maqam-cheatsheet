python := ".venv/bin/python"
pip := ".venv/bin/pip"

watch:
    watchexec --clear --restart -w maqamat.py -w ./templates -w ./data -- python maqamat.py
