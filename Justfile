PYTHON := ".venv/bin/python"

watch:
    watchexec -w static -w data -w templates -w maqamat.py  \
      --ignore "*.mo" -- just build

build:
    mkdir -p out
    test -f out/alpine.min.js || curl -l unpkg.com/alpinejs > out/alpine.min.js
    pybabel compile --domain=translations --directory=data/locale --use-fuzzy
    cp static/js/index.js static/style.css static/img/* static/svg/* out
    {{PYTHON}} maqamat.py

serve:
    {{PYTHON}} -m http.server 42488 --bind 0.0.0.0 --directory out
