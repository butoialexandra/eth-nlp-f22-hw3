"""
Functions for correctness testing on WFSAs and WFSTs.
"""
import textwrap
from collections import defaultdict

from tabulate import tabulate

from rayuela.fsa.fsa import FSA
from rayuela.fsa.fst import FST


class _FSAStructuralEqualityReport:
    """
    Formats the result of `report_fst_structural_equality` as a table.
    """

    def __init__(
        self, report_sections: dict[list], title: str = None, maxwidth: int = 80
    ):
        """Creates a report formatter.

        Args:
            report_sections (dict[list]): Dict of report sections. Keys are section
                titles and values are lists of strings.
            title (str, optional): Report title. Defaults to None.
            maxwidth (int, optional): Maximum cell width. Defaults to 80.
        """
        self.report_sections = report_sections
        self.title = title
        self.maxwidth = maxwidth

    @property
    def structurally_equal(self):
        """
        Returns True if the two FSTs are structurally equal, False otherwise.
        """
        return len(self.report_sections) == 0

    def __str__(self):
        rows = []
        if len(self.report_sections) == 0:
            rows.append(["FSTs are structurally equal"])
        for key, values in self.report_sections.items():
            # Make key more readable
            key = key.replace("_", " ").capitalize()
            # Make sure that string width does not exceed 80 characters
            values = [
                textwrap.fill(value, width=self.maxwidth, subsequent_indent="    ")
                for value in values
            ]
            rows.extend([[key], ["\n".join(values)]])
        return tabulate(
            rows,
            headers=[self.title or "FST Structural Equality Report"],
            tablefmt="grid",
        )

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if not isinstance(other, _FSAStructuralEqualityReport):
            return False
        return set(self.report_sections.keys()) == set(
            other.report_sections.keys()
        ) and all(
            set(self.report_sections[key]) == set(other.report_sections[key])
            for key in self.report_sections.keys()
        )


def _arcs(fst: FSA | FST):
    """
    Returns a list of all arcs in the FST in the format (i, (a, b), j, w)

    Args:
        fst (FSA | FST): FSA or FST to get arcs from. If FSA, ab is just the symbol a.
            If FST, ab is the pair (a, b).
    """
    return {
        (i, ab, j, w)
        for i, ab_j_w in fst.δ.items()
        for ab, j_w in ab_j_w.items()
        for j, w in j_w.items()
    }


def fsa_structural_equality_report(fsa1: FSA | FST, fsa2: FSA | FST, title=None):
    """
    Returns a detailed report on structural differences between two WFSAs. Two WFSAs are
    considered structurally equal, if

    - They have the same semiring
    - They have the same input (and output, if FST) alphabet
    - They have the same set of states
    - Initial and final weight functions are functionally equal (i.e. agree on every
      state)
    - They have the same set of arcs, and the weight function is functionally equal
      (i.e. agree on every arc)

    Other quantities such as FSA.I and FSA.F are not checked, as they are derived from
    the above.

    Args:
        fsa1 (FSA | FST): First FSA
        fsa2 (FSA | FST): Second FSA
        title (str, optional): Title of the report. Defaults to None.

    Returns:
        _FSAStructuralEqualityReport: Report object. Can be printed or converted to
            string.
    """
    mismatches = defaultdict(list)

    # Check semiring
    if fsa1.R != fsa2.R:
        mismatches["semiring"].append(f"Semirings do not match: {fsa1.R} != {fsa2.R}")

    # Check input and output alphabets
    if fsa1.Sigma != fsa2.Sigma:
        mismatches["alphabet"].append(
            f"Input alphabets do not match: {fsa1.Sigma} != {fsa2.Sigma}"
        )
    if isinstance(fsa1, FST) and isinstance(fsa2, FST) and fsa1.Omega != fsa2.Omega:
        mismatches["alphabet"].append(
            f"Output alphabets do not match: {fsa1.Omega} != {fsa2.Omega}"
        )

    # Check states set equality. We want to report the following:
    # - States in fst1 but not in fst2
    # - States in fst2 but not in fst1
    missing_states1 = fsa1.Q - fsa2.Q
    missing_states2 = fsa2.Q - fsa1.Q
    if len(missing_states1) > 0:
        mismatches["states"].append(
            f"States in FST1 but not in FST2: {missing_states1}"
        )
    if len(missing_states2) > 0:
        mismatches["states"].append(
            f"States in FST2 but not in FST1: {missing_states2}"
        )

    # Check initial and final weights. The weight functions λ and ρ must be functionally equal, i.e.
    # agree on every value on the domain (all states).
    for q in fsa1.Q:
        if fsa1.λ[q] != fsa2.λ[q]:
            mismatches["state_weights"].append(
                f"Initial weight for state {q} does not match: {fsa1.λ[q]} != {fsa2.λ[q]}"
            )
        if fsa1.ρ[q] != fsa2.ρ[q]:
            mismatches["state_weights"].append(
                f"Final weight for state {q} does not match: {fsa1.ρ[q]} != {fsa2.ρ[q]}"
            )

    # Check arcs. We first flatten the arcs into a list of tuples (i, (a, b), j, w) and compare.
    # We report:
    # - Missing arcs (i, (a, b), j) in FST1
    # - Missing arcs (i, (a, b), j) in FST2
    # - Mismatching weights
    arcs1 = _arcs(fsa1)
    arcs2 = _arcs(fsa2)

    def _unweighted(arcs):
        return {(i, ab, j) for i, ab, j, _ in arcs}

    missing_arcs1 = _unweighted(arcs2) - _unweighted(arcs1)
    missing_arcs2 = _unweighted(arcs1) - _unweighted(arcs2)
    if len(missing_arcs1) > 0:
        mismatches["arcs"].append(f"Missing arcs in FST1: {missing_arcs1}")
    if len(missing_arcs2) > 0:
        mismatches["arcs"].append(f"Missing arcs in FST2: {missing_arcs2}")

    def _arc_weight_mismatch(arcs1, arcs2):
        return {
            (tuple(arc1), w1, w2)
            for *arc1, w1 in arcs1
            for *arc2, w2 in arcs2
            if arc1 == arc2 and w1 != w2
        }

    arc_weight_mismatches = _arc_weight_mismatch(arcs1, arcs2)
    for arc, w1, w2 in arc_weight_mismatches:
        mismatches["arc_weights"].append(
            f"Weight for arc {arc} does not match: {w1} != {w2}"
        )

    return _FSAStructuralEqualityReport(mismatches, title=title)


def fsa_structurally_equal(fsa1: FSA | FST, fsa2: FSA | FST):
    """
    Returns True if the two FSTs are structurally equal, False otherwise. See
    `report_fst_structural_equality` for more details.

    Args:
        fsa1 (FSA | FST): First FSA
        fsa2 (FSA | FST): Second FSA

    Returns:
        bool: True if the two FSTs are structurally equal, False otherwise.
    """
    return fsa_structural_equality_report(fsa1, fsa2).structurally_equal
