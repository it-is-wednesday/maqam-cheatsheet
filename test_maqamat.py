from textwrap import dedent

from maqamat import (Jins, Maqam, get_ajnas, make_ajnas_tags_in_maqam,
                     parse_jins_combination)

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


def test_make_ajnas_tags_in_maqam() -> None:
    expected = """
      <div class="jins">
        <h3>hijaz</h3>
        <div class="jins-intervals">
          ½ ⇨ 1½ ⇨ ½
        </div>
      </div>
      <div class="jins">
        <h3>nikriz3 + hijazkar</h3>
        <div class="jins-intervals">
          1 ⇨ ½ ⇨ 1½ ⇨ ½ ⇨ ½ ⇨ 1½
        </div>
      </div>
    """
    result = make_ajnas_tags_in_maqam(sample_maqam, ajnas_dict)
    assert dedent(expected).strip() == result
