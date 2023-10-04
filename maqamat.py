import csv
from typing import Optional
import re
from dataclasses import dataclass
from pathlib import Path
from string import Template

PRETTY_FRACTIONS = {
    0.25: "¼",
    0.5: "½",
    0.75: "¾",
    1: "1",
    1.25: "1¼",
    1.5: "1½",
}


@dataclass
class Jins:
    name: str
    intervals: list[int]
    arabic_name: str
    hebrew_name: str

    def __init__(self, name, intervals, arabic_name, hebrew_name):
        self.name = name
        self.intervals = [int(x) for x in intervals.split(" ")]
        self.arabic_name = arabic_name
        self.hebrew_name = hebrew_name


def get_ajnas() -> dict[str, Jins]:
    with open("data/ajnas.csv", newline="") as csvfile:
        return {row["name"]: Jins(**row) for row in csv.DictReader(csvfile)}


def pairs(iterable):
    """
    >>> pairs([1, 2, 3, 4, 5, 6])
    [(1, 2), (3, 4), (5, 6)]
    """
    return list(zip(*[iter(iterable)] * 2, strict=True))


def parse_jins_combination(comb, ajnas):
    """
    >>> ajnas = get_ajnas()
    >>> parse_jins_combination("hijaz", ajnas)
    [2, 6, 2]
    >>> parse_jins_combination("saba 3+ hijaz", ajnas)
    [2, 6, 2]
    >>>
    """
    if "+" not in comb:
        return ajnas[comb].intervals
    result = []
    for jins, overlap in pairs(re.split(r" (\d)?\+ ", comb) + [None]):
        intervals = ajnas[jins].intervals
        overlap = int(overlap or len(intervals) + 1)
        result.extend(intervals[: overlap - 1])
    return result


@dataclass
class Maqam:
    name: str
    tonic: str
    ghammaz_option1: Optional[str]
    ghammaz_option2: Optional[str]

    def __init__(self, name, tonic, ghammaz_option1, ghammaz_option2, ajnas):
        self.name = name
        self.tonic = parse_jins_combination(tonic, ajnas)
        self.ghammaz_option1 = (
            parse_jins_combination(ghammaz_option1, ajnas)
            if ghammaz_option1
            else None
        )
        self.ghammaz_option2 = (
            parse_jins_combination(ghammaz_option2, ajnas)
            if ghammaz_option2
            else None
        )


def get_maqamat() -> dict[str, Maqam]:
    ajnas = get_ajnas()
    with open("data/maqamat.csv", newline="") as csvfile:
        return {
            row["name"]: Maqam(**row, ajnas=ajnas) for row in csv.DictReader(csvfile)
        }


def get_template(name: str) -> Template:
    return Template(Path(f"templates/{name}.html").read_text())


def make_html():
    jins_template = get_template("jins-tag")
    ajnas = {"hijaz": jins_template.substitute(name="hijaz", intervals=[0.25])}

    maqam_template = get_template("maqam-tag")
    maqamat_tags = "".join(maqam_template.substitute(name="hijaz", ajnas=ajnas["hijaz"]))

    main = get_template("index").substitute(maqamat=maqamat_tags)

    return main


def main():
    print(get_ajnas())


if __name__ == "__main__":
    main()
