from dna_storage.utils.oligo_utils import recommend_rs_parameters, pretty_recommendation


def test_basic_recommendation():
    r = recommend_rs_parameters(oligo_len=150, overhead=40)
    assert r["usable_bases"] == 110
    assert r["n_max"] == 27
    rec = r["recommended"]
    assert rec["n"] <= 27
    assert rec["k"] <= rec["n"]


def test_pretty():
    s = pretty_recommendation(150, 40)
    assert "recommended n=" in s


def test_zero_space():
    r = recommend_rs_parameters(oligo_len=50, overhead=60)
    assert r["n_max"] == 0
    assert r["recommended"] is None
