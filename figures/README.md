# Manuscript Figures

This directory contains publication-oriented vector figures for the manuscript.

## Figure Set

1. `src/figure-1-ontological-prototype.svg` — the ontological prototype of SIO.
2. `src/figure-2-operational-closure.svg` — the canonical operational closure `AB → C → AB`.
3. `src/figure-3-criteria-conjunction.svg` — the logical relation of N1–N5 to N6.
4. `output/figure-4-comparative-matrix.svg` — the categorical comparison matrix generated from `data/comparative-assessments.csv`.
5. `src/figure-5-research-program.svg` — the formal and empirical research program.

The conceptual figures are maintained directly as SVG so that wording, arrows, and layout remain explicit and editable. Figure 4 is generated from the fixed Chapter 5 assessment data:

```sh
MPLBACKEND=Agg MPLCONFIGDIR=/tmp/sio-matplotlib python3 figures/src/figure-4-comparative-matrix.py
```

The script produces both SVG and PDF output. The matrix is categorical and non-additive; it does not rank the comparison cases.

## Proposed Captions

**Figure 1. Ontological prototype of Subjectivity Intersection Ontology.** Relative Subjectivity R is differentiated through the projection of Absolute Subjectivity S, and Intersection Subjectivity X emerges through the constitutive intersection of S and R. The diagram represents a triadic ontological closure, not a temporal sequence or an empirical mechanism.

**Figure 2. Canonical operational closure among multiple Relative Subjectivities.** Relative Subjectivities A and B constitute Intersection Subjectivity C through perspective intersection; C in turn reconstitutes A and B. The arrows indicate direction of constitution rather than simple chronological succession.

**Figure 3. Logical relation among the comparative criteria.** N1–N5 are independent, non-additive structural criteria. N6 is their conjunction condition and not an additional score.

**Figure 4. Distribution of criterion-level assessments across the comparison set.** Rows follow the order of the historical review. The categories are non-additive and do not rank the philosophical value or historical importance of the comparison cases. N6 is separated visually because it assesses the conjunction of N1–N5. P retains the single category defined in Chapter 3—partial or interpretation-dependent satisfaction—and does not imply that partial correspondence and interpretive dependence have identical grounds in every case; those grounds are reported separately in Chapter 4.

**Figure 5. SIO as a formal and empirical research program.** Ontological definition, formalization, operationalization, and empirical testing remain distinct stages. Empirical results may require revision or rejection of an operational hypothesis, formal model, or ontological assumption; no transition by itself validates the preceding level.
