def test_passing():
    assert (1, 2, 3) == (1, 2, 3)

def test_failing():
    assert (3, 2, 1) == (3, 2, 2)