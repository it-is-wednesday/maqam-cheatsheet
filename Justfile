python := ".venv/bin/python"
pip := ".venv/bin/pip"

make-venv:
    python -m venv .venv
    {{pip}} install -U pip pip-tools
    just generate-requirements
    {{pip}} install -r requirements.txt

generate-requirements:
    {{python}} -m piptools compile --annotation-style line --extra dev -o requirements.txt --strip-extras
