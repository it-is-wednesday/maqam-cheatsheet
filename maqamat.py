import csv
from pathlib import Path
import re
from dataclasses import dataclass
from itertools import accumulate
from operator import add
from typing import Any, Optional
import gettext

from jinja2 import Environment, PackageLoader

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
        joined = ARROW.join(PRETTY_FRACTIONS[i] for i in self.intervals)
        return ARROW.lstrip() + joined


def intervals_binary(intervals: list[int]) -> int:
    """
    >>> 0b001000000000000000000000 == intervals_binary([2])
    True
    >>> 0b101000001000100000100100 == intervals_binary([2, 6, 4, 6, 3, 3])
    True
    """
    return sum(2 ** ((24 - num - 1) % 24) for num in accumulate(intervals, add))


@dataclass
class Maqam:
    name: str
    tonic: Jins
    ghammaz_option1: Optional[Jins] = None
    ghammaz_option2: Optional[Jins] = None

    def to_binary(self) -> list[int]:
        t = self.tonic.intervals
        result = [intervals_binary(t)]

        if g := self.ghammaz_option1:
            result.append(intervals_binary(t + g.intervals))

        if g := self.ghammaz_option2:
            result.append(intervals_binary(t + g.intervals))

        return result


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


def make_html(locale: str) -> str:
    ajnas_dict = get_ajnas()
    maqamat = get_maqamat(ajnas_dict)

    gnu_translations = gettext.translation(
        domain='index',
        localedir="locale/",
        languages=[locale]
    )
    jinja_env = Environment(
        loader=PackageLoader("maqamat"),
        autoescape=False,
        extensions=["jinja2.ext.i18n"],
    )
    jinja_env.install_gettext_translations(gnu_translations, newstyle=True)

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
    for locale in ["en_US", "ar"]:
        p = Path(f"static/{locale}/index.html")
        p.parent.mkdir(exist_ok=True)
        with p.open("w") as f:
            f.write(make_html(locale))


if __name__ == "__main__":
    main()
