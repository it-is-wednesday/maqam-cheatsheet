
from maqamat import Jins, Maqam, get_ajnas, parse_jins_combination

ajnas_dict = get_ajnas()
sample_maqam = Maqam(
    name="hijazkar",
    tonic=Jins(name="hijaz", intervals=[2, 6, 2]),
    ghammaz_option1=Jins(
        name="nikriz3 + hijazkar",
        intervals=[4, 2, 6, 2, 2, 6],
    ),
)


def test_parse_jins_combination() -> None:
    expected = Jins(name="hijaz", intervals=[2, 6, 2])
    assert expected == parse_jins_combination("hijaz", ajnas_dict)

    expected = Jins(name="saba3 + hijaz", intervals=[3, 3, 2, 6, 2])
    assert expected == parse_jins_combination("saba3 + hijaz", ajnas_dict)

    name = "ajam3 + kurd + nahawand3"
    expected = Jins(name, intervals=[4, 4, 2, 4, 4, 4, 2])
    assert expected == parse_jins_combination(name, ajnas_dict)
