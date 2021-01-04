from factories import CustomerFactory


def test_terminal(terminals):
    terminal = terminals[0]
    assert terminal.active
