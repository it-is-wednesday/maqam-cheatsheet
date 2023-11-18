# Developing
``` shell
python -m venv .venv
.venv/bin/pip install '.[dev]'
.venv/bin/supervisord
```

Now open a web broser at localhost:42488

# Nginx Setup with GeoIP
You may wanna compile the GeoIP2 first: https://github.com/leev/ngx_http_geoip2_module

Don't forget to change `MAQAM_LOVE_PATH`!

```
map $geoip2_data_country_code $maqam_love_lang {
    default en;
    AE ar;
    BH ar;
    DZ ar;
    EG ar;
    IL he;
    IQ ar;
    JO ar;
    KM ar;
    KW ar;
    LB ar;
    LY ar;
    MA ar;
    MR ar;
    OM ar;
    PS ar;
    QA ar;
    SA ar;
    SD ar;
    SO ar;
    SS ar;
    SY ar;
    TD ar;
    TN ar;
    YE ar;
}

server {
    server_name maqam.love;
    listen 443 ssl http2;
    listen [::]:443 ssl http2;

    root MAQAM_LOVE_PATH;

    location = / {
        return 301 /$maqam_love_lang/;
    }
}
```

