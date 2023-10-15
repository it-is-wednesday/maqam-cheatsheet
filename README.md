# Developing
``` shell
python -m venv .venv
.venv/bin/pip install '.[dev]'
.venv/bin/supervisord
```

Now open a web broser at localhost:42488

# Nginx
```
server {
    server_name maqam.love;
    listen 443 ssl http2;
    listen [::]:443 ssl http2;

    root ...;

    location = / {
        index /en/index.html;
    }
}
```

