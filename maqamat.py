import csv
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from string import Template
from typing import Any, Optional

PRETTY_FRACTIONS = {
    1: "¼",
    2: "½",
    3: "¾",
    4: "1",
    5: "1¼",
    6: "1½",
}

ARROW = " ⇨ "


@dataclass
class Jins:
    name: str
    intervals: list[int]


@dataclass
class Maqam:
    name: str
    tonic: Jins
    ghammaz_option1: Optional[Jins] = None
    ghammaz_option2: Optional[Jins] = None


Ajnas = dict[str, Jins]


def get_ajnas() -> Ajnas:
    with open("data/ajnas.csv", newline="") as csvfile:
        return {
            row["name"]: Jins(
                name=row["name"],
                intervals=[int(i) for i in row["intervals"].split(" ")],
            )
            for row in csv.DictReader(csvfile)
        }


def get_maqamat(ajnas: Ajnas) -> dict[str, Maqam]:
    with open("data/maqamat.csv", newline="") as csvfile:
        return {
            row["name"]: Maqam(
                row["name"],
                parse_jins_combination(row["tonic"], ajnas),
                parse_jins_combination(g, ajnas)
                if (g := row["ghammaz_option1"])
                else None,
                parse_jins_combination(g, ajnas)
                if (g := row["ghammaz_option2"])
                else None,
            )
            for row in csv.DictReader(csvfile)
        }


def pairs(iterable: list[Any]) -> list[tuple[Any, Any]]:
    """
    >>> pairs([1, 2, 3, 4, 5, 6])
    [(1, 2), (3, 4), (5, 6)]
    """
    return list(zip(*[iter(iterable)] * 2, strict=True))


def parse_jins_combination(comb: str, ajnas: Ajnas) -> Jins:
    """
    >>> parse_jins_combination('saba3 + hijaz + nikriz', get_ajnas())
    Jins(name='saba3 + hijaz + nikriz', intervals=[3, 3, 2, 6, 2, 4, 2, 6, 2])
    """
    intervals = []
    for jins_raw in comb.split(" + "):
        if match_ := re.search(r"([a-z_]+)(\d)?", jins_raw):
            jins, overlap = match_.groups()
            jins_intervals = ajnas[jins].intervals
            overlap = int(overlap or len(jins_intervals) + 1)
            intervals.extend(jins_intervals[: overlap - 1])
    return Jins(comb, intervals)


def get_template(name: str) -> Template:
    return Template(Path(f"templates/{name}.html").read_text())


def make_ajnas_tags_in_maqam(maqam: Maqam, ajnas_dict: Ajnas) -> str:
    jins_template = get_template("jins-tag")
    result = ""
    for jins in [
        maqam.tonic,
        maqam.ghammaz_option1,
        maqam.ghammaz_option2,
    ]:
        if jins:
            result += jins_template.substitute(
                name=jins.name,
                intervals=ARROW.join(
                    PRETTY_FRACTIONS[i] for i in jins.intervals
                ),
            )
    return result.strip()


def make_html() -> str:
    ajnas_dict = get_ajnas()

    maqam_template = get_template("maqam-tag")
    maqamat_tags = "".join(
        maqam_template.substitute(
            name=name,
            ajnas=make_ajnas_tags_in_maqam(maqam, ajnas_dict),
        )
        for (name, maqam) in get_maqamat(ajnas_dict).items()
    )

    main = get_template("index").substitute(maqamat=maqamat_tags.strip())

    return main


def main() -> None:
    with open("out.html", "w") as f:
        proc = subprocess.run(
            args=["tidy", "-indent", "--tidy-mark", "no"],
            capture_output=True,
            text=True,
            input=make_html(),
        )
        f.write(proc.stdout)


if __name__ == "__main__":
    main()
