from rayuela.base.semiring import Boolean, Real
from rayuela.base.symbol import Sym, ε
from rayuela.fsa.fsa import FSA, State
from rayuela.fsa.fsa_testing import fsa_structural_equality_report
from rayuela.fsa.fst import FST


def _make_fsa1():
    fsa = FSA(R=Boolean)

    fsa.add_states({State(i) for i in [0, 1, 2]})
    fsa.set_I(State(0), Boolean(True))
    fsa.set_F(State(2), Boolean(True))

    fsa.add_arc(State(0), ε, State(0), Boolean(True))
    fsa.add_arc(State(0), Sym("b"), State(0), Boolean(True))
    fsa.add_arc(State(0), Sym("c"), State(0), Boolean(True))
    fsa.add_arc(State(0), Sym("a"), State(2), Boolean(True))
    fsa.add_arc(State(2), Sym("a"), State(0), Boolean(True))
    fsa.add_arc(State(1), Sym("a"), State(0), Boolean(True))
    fsa.add_arc(State(2), Sym("c"), State(1), Boolean(True))
    fsa.add_arc(State(1), ε, State(2), Boolean(True))
    fsa.add_arc(State(1), Sym("b"), State(2), Boolean(True))
    fsa.add_arc(State(1), Sym("c"), State(2), Boolean(True))

    return fsa


def _make_fsa2():
    fsa = FSA(R=Boolean)

    fsa.add_states({State(i) for i in [0, 1, 2, 3]})
    fsa.set_I(State(0), Boolean(True))
    fsa.set_F(State(2), Boolean(True))

    fsa.add_arc(State(0), ε, State(0), Boolean(True))
    fsa.add_arc(State(0), Sym("c"), State(0), Boolean(True))
    fsa.add_arc(State(0), Sym("a"), State(2), Boolean(True))
    fsa.add_arc(State(2), Sym("a"), State(0), Boolean(False))
    fsa.add_arc(State(1), Sym("a"), State(0), Boolean(True))
    fsa.add_arc(State(2), Sym("c"), State(1), Boolean(True))
    fsa.add_arc(State(1), ε, State(2), Boolean(True))
    fsa.add_arc(State(1), Sym("b"), State(2), Boolean(True))
    fsa.add_arc(State(1), Sym("c"), State(2), Boolean(True))
    fsa.add_arc(State(1), Sym("d"), State(3), Boolean(True))

    return fsa


def _make_fst1():
    fst = FST(R=Real)

    fst.add_states({State(i) for i in [0, 1]})
    fst.set_I(State(0), Real(29.0))
    fst.set_F(State(1), Real(2.0))

    fst.add_arc(State(0), ε, Sym("b"), State(0), Real(0.0))
    fst.add_arc(State(0), Sym("b"), ε, State(1), Real(35.0))
    fst.add_arc(State(1), Sym("b"), Sym("b"), State(0), Real(43.0))
    fst.add_arc(State(1), Sym("a"), Sym("b"), State(0), Real(25.0))
    fst.add_arc(State(1), ε, Sym("a"), State(1), Real(25.0))

    return fst


def _make_fst2():
    fst = FST(R=Real)

    fst.add_states({State(i) for i in [0, 1, 2]})
    fst.set_I(State(0), Real(8.0))
    fst.set_F(State(1), Real(2.5))

    fst.add_arc(State(0), ε, Sym("b"), State(0), Real(0.0))
    fst.add_arc(State(0), Sym("b"), ε, State(1), Real(35.0))
    fst.add_arc(State(1), Sym("b"), Sym("b"), State(0), Real(43.1))
    fst.add_arc(State(1), Sym("a"), Sym("a"), State(0), Real(25.0))
    fst.add_arc(State(1), ε, Sym("a"), State(1), Real(25.0))
    fst.add_arc(State(0), Sym("b"), Sym("b"), State(1), Real(35.0))
    fst.add_arc(State(2), ε, ε, State(2), Real(0.0))

    return fst


# Create instances of FSA or FST for testing
fsa1 = _make_fsa1()
fsa2 = _make_fsa2()
fst1 = _make_fst1()
fst2 = _make_fst2()


def test_commutativity():
    report1 = fsa_structural_equality_report(fsa1, fsa2)
    report2 = fsa_structural_equality_report(fsa2, fsa1)
    assert report1.structurally_equal == report2.structurally_equal


def test_fsa_structural_equality():
    report = fsa_structural_equality_report(fsa1, fsa2)
    assert not report.structurally_equal

    # Just for visualization
    print(report)

    report = fsa_structural_equality_report(fsa1, fsa1)
    assert report.structurally_equal


def test_fst_structural_equality():
    report = fsa_structural_equality_report(fst1, fst2)
    assert not report.structurally_equal

    report = fsa_structural_equality_report(fst1, fst1)
    assert report.structurally_equal


def test_fsa_fst_structural_inequality():
    report = fsa_structural_equality_report(fsa1, fst1)
    assert not report.structurally_equal
