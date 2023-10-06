from maqamat import Jins, get_ajnas, get_maqamat, parse_jins_combination

ajnas_dict = get_ajnas()
maqamat = {maqam.name: maqam for maqam in get_maqamat(ajnas_dict)}


def test_parse_jins_combination() -> None:
    expected = Jins(name="hijaz", intervals=[2, 6, 2])
    assert expected == parse_jins_combination("hijaz", ajnas_dict)

    expected = Jins(name="saba3 + hijaz", intervals=[3, 3, 2, 6, 2])
    assert expected == parse_jins_combination("saba3 + hijaz", ajnas_dict)

    name = "ajam3 + kurd + nahawand3"
    expected = Jins(name, intervals=[4, 4, 2, 4, 4, 4, 2])
    assert expected == parse_jins_combination(name, ajnas_dict)


def test_maqamat_binary() -> None:
    ### Sikah
    # intervals: 3, 4 (jins sikah)
    only_tonic = 0b000100010000000000000000
    # intervals: 3, 4, 4, 3, 3, 4, 3 (jins upper_rast + rast3)
    with_opt1 = 0b100100010001001001000100
    result = list(maqamat["sikah"].to_binary())
    assert result[0] == only_tonic
    assert result[1] == with_opt1

    ### Nahawand Murassaa
    # (jins nahawand_murassaa4 + hijaz + extra_tone)
    # intervals: 4, 2, 4, 2, 6, 2, 4
    only_tonic = 0b100010100010100000101000
    result = list(maqamat["nahawand_murassaa"].to_binary())
    assert result[0] == only_tonic
