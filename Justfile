python := ".venv/bin/python"
pip := ".venv/bin/pip"

make-venv:
    test -d .venv || python -m venv .venv
    test -d .venv/lib/python3.11/site-packages/piptools || {{pip}} install -U pip pip-tools
    just generate-requirements
    {{pip}} install -r requirements.txt

generate-requirements:
    {{python}} -m piptools compile --annotation-style line --extra dev -o requirements.txt --strip-extras

watch:
    watchexec -w download.py -w ./templates python download.py
