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


def get_template(name: str) -> Template:
    return Template(Path(f"templates/{name}.html").read_text())


def main():
    jins_template = get_template("jins-tag")
    ajnas = {"hijaz": jins_template.substitute(name="hijaz", intervals=[0.25])}

    maqam_template = get_template("maqam-tag")
    maqamat_tags = "".join(maqam_template.substitute(name="hijaz", ajnas=ajnas["hijaz"]))

    main = get_template("index").substitute(maqamat=maqamat_tags)

    print(main)


if __name__ == "__main__":
    main()
