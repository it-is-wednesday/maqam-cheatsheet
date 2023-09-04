import re
from pathlib import Path
from string import Template
from typing import Iterable

import requests
from bs4 import BeautifulSoup

PRETTY_FRACTIONS = {
    0.25: "¼",
    0.5: "½",
    0.75: "¾",
    1: "1",
    1.25: "1¼",
    1.5: "1½",
}

BASE_URL = "http://maqamworld.com/en"

AJNAS = {
    "ajam": [1, 1, 0.5, 1],
    "ajam_murassaa": [1, 1, 1, 0.5],
    "athar_kurd": [0.5, 1, 1.5, 0.5],
    "bayati": [0.75, 0.75, 1],
    "hijaz": [0.5, 1.5, 0.5],
    "hijaz_murassaa": [0.5, 1.5, 0.5, 0.5],
    "hijazkar": [1.5, 0.5, 0.5, 1.5],
    "jiharkah": [1, 1, 0.5, 1],
    "kurd": [0.5, 1, 1],
    "lami": [0.5, 1, 1, 0.5],
    "mukhalif_sharqi": [0.75, 0.5],
    "mustaar": [1.25, 0.5],
    "nahawand": [1, 0.5, 1, 1],
    "nahawand_murassaa": [1, 0.5, 1, 0.5],
    "nikriz": [1, 0.5, 1.5, 0.5],
    "rast": [1, 0.75, 0.75, 1],
    "saba": [0.75, 0.75, 0.5, 1.5, 0.5],
    "saba_dalanshin": [0.75, 0.75, 0.5, 1.5, 0.5],
    "saba_zamzam": [0.5, 1, 0.5, 1.5, 0.5],
    "sazkar": [1.5, 0.25, 0.75, 1],
    "sikah": [0.75, 1],
    "upper_ajam": [1, 1, 0.5],
    "upper_rast": [1, 0.75, 0.75],
}


def fetch_maqam(name: str) -> BeautifulSoup:
    f = Path("maqam-pages-cache").joinpath(name)
    f.parent.mkdir(exist_ok=True)
    if f.exists():
        print(f"Found {name} in cache")
        resp = f.read_text()

    else:
        resp = requests.get(f"{BASE_URL}/maqam/{name}.php").text
        print(f"Fetched {name} from le interwebs")
        f.write_text(resp)

    return BeautifulSoup(resp, "html.parser")


def get_template(name: str) -> Template:
    return Template(Path(f"templates/{name}.html").read_text())


def jins_in_maqam(maqam_name: str) -> Iterable[str]:
    page = fetch_maqam(maqam_name)
    jins_template = get_template("jins-tag")
    interval_template = get_template("interval-tag")
    for jins in page.find_all(class_="mapLink"):
        href = jins.attrs["href"]
        if match_ := re.search(r"../jins/(.*).php", href):
            jins_name = match_.group(1)
            intervals = "".join(
                interval_template.substitute(text=PRETTY_FRACTIONS[x])
                for x in AJNAS[jins_name]
            )
            yield jins_template.substitute(name=jins_name, intervals=intervals)


def fetch_maqams() -> Iterable[str]:
    # random maqam picked, we just need the sidebar menu
    page = fetch_maqam("ajam")

    maqam_template = get_template("maqam-tag")
    for row in page.find(class_="sub-menu").find_all("a"):  # type: ignore
        href = row.attrs["href"]
        if href == "#":
            continue

        if match_ := re.search(r"/en/maqam/(.*).php", href):
            maqam_name = match_.group(1)
            if maqam_name == "sikah_baladi":
                continue
            yield maqam_template.substitute(
                name=maqam_name,
                img_url=f"https://maqamworld.com/note/maqam/{maqam_name}.png",
                ajnas="".join(jins for jins in jins_in_maqam(maqam_name)),
            )


def main():
    maqamat_tags = list(fetch_maqams())
    out = get_template("index").substitute(maqamat="".join(maqamat_tags))
    with open("out.html", "w") as f:
        f.write(out)


if __name__ == "__main__":
    main()
