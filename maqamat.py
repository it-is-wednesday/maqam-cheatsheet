import csv
import re
import subprocess
from dataclasses import dataclass
from typing import Any, Optional

from jinja2 import Environment, PackageLoader, select_autoescape

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

    def pretty_intervals(self) -> str:
        return ARROW.join(PRETTY_FRACTIONS[i] for i in self.intervals)


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


def get_maqamat(ajnas: Ajnas) -> list[Maqam]:
    with open("data/maqamat.csv", newline="") as csvfile:
        return [
            Maqam(
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
        ]


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


def make_html() -> str:
    ajnas_dict = get_ajnas()
    maqamat = get_maqamat(ajnas_dict)

    jinja_env = Environment(
        loader=PackageLoader("maqamat"),
        autoescape=select_autoescape(),
    )

    print(
        "{:^20}{:^20}{:^20}{:^20}".format(
            "maqam", "tonic", "ghammaz1", "ghammaz2"
        )
    )
    for maqam in maqamat:
        print(
            "{:^20}{:^20}{:^20}{:^20}".format(
                maqam.name,
                sum(maqam.tonic.intervals)
                if not maqam.ghammaz_option1 and not maqam.ghammaz_option2
                else "",
                sum(maqam.tonic.intervals) + sum(g.intervals)
                if (g := maqam.ghammaz_option1)
                else "",
                sum(maqam.tonic.intervals) + sum(g.intervals)
                if (g := maqam.ghammaz_option2)
                else "",
            )
        )

    template = jinja_env.get_template("index.html")
    return template.render(maqamat=maqamat)


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
