import csv
import gettext
import re
from collections.abc import Callable
from dataclasses import dataclass
from functools import partial
from itertools import accumulate
from operator import add
from pathlib import Path
from typing import Any

from jinja2 import Environment, PackageLoader

GettextFunc = Callable[[str], str]

PRETTY_FRACTIONS = {
    1: "¼",
    2: "½",
    3: "¾",
    4: "1",
    5: "1¼",
    6: "1½",
}


@dataclass
class Jins:
    name: str
    intervals: list[int]

    def __init__(
        self, name: str, intervals: list[int], gettext: GettextFunc
    ) -> None:
        self.name = name
        self.intervals = intervals
        self.gettext = gettext

    def pretty_intervals(self) -> list[str]:
        return [PRETTY_FRACTIONS[i] for i in self.intervals]

    def translate(self) -> str:
        no_digits = re.sub(r"\d", "", self.name)
        translated = [
            self.gettext(s) for s in no_digits.split(" + ") if s != "extra_tone"
        ]
        return " & ".join(translated)


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
    ghammaz_option1: Jins | None = None
    ghammaz_option2: Jins | None = None

    def to_binary(self) -> list[int]:
        t = self.tonic.intervals
        result = [intervals_binary(t)]

        if g := self.ghammaz_option1:
            result.append(intervals_binary(t + g.intervals))

        if g := self.ghammaz_option2:
            result.append(intervals_binary(t + g.intervals))

        return result


Ajnas = dict[str, Jins]


def get_ajnas(gettext: GettextFunc) -> Ajnas:
    with Path("data/ajnas.csv").open(newline="") as csvfile:
        return {
            row["name"]: Jins(
                name=row["name"],
                intervals=[int(i) for i in row["intervals"].split(" ")],
                gettext=gettext,
            )
            for row in csv.DictReader(csvfile)
        }


def get_maqamat(ajnas: Ajnas, gettext: GettextFunc) -> list[Maqam]:
    parse = partial(parse_jins_combination, ajnas=ajnas, gettext=gettext)
    with Path("data/maqamat.csv").open(newline="") as csvfile:
        return [
            Maqam(
                row["name"],
                parse(row["tonic"]),
                parse(g) if (g := row["ghammaz_option1"]) else None,
                parse(g) if (g := row["ghammaz_option2"]) else None,
            )
            for row in csv.DictReader(csvfile)
        ]


def pairs(iterable: list[Any]) -> list[tuple[Any, Any]]:
    """
    >>> pairs([1, 2, 3, 4, 5, 6])
    [(1, 2), (3, 4), (5, 6)]
    """
    return list(zip(*[iter(iterable)] * 2, strict=True))


def parse_jins_combination(
    comb: str, ajnas: Ajnas, gettext: GettextFunc
) -> Jins:
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
    return Jins(comb, intervals, gettext)


def make_html(locale: str) -> str:
    gnu_translations = gettext.translation(
        domain="translations", localedir="data/locale/", languages=[locale]
    )

    ajnas_dict = get_ajnas(gnu_translations.gettext)
    maqamat = get_maqamat(ajnas_dict, gnu_translations.gettext)

    jinja_env = Environment(
        loader=PackageLoader("maqamat"),
        autoescape=False,
        extensions=["jinja2.ext.i18n"],
    )
    jinja_env.install_gettext_translations(gnu_translations, newstyle=True)

    template = jinja_env.get_template("index.html")
    return template.render(maqamat=maqamat, locale=locale)


def main() -> None:
    for locale in ["en", "ar", "he"]:
        p = Path(f"out/{locale}/index.html")
        p.parent.mkdir(exist_ok=True)
        print(f"generating {locale}")
        with p.open("w") as f:
            f.write(make_html(locale))


if __name__ == "__main__":
    main()
