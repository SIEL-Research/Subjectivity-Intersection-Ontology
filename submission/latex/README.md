# Submission PDF build

The integrated submission manuscript is generated from the author-approved Markdown files in `manuscript/`. The generated chapter fragments under `generated/` are build artifacts; the Markdown files remain authoritative.

From the repository root, regenerate the comparative matrix and LaTeX fragments:

```sh
mkdir -p submission/latex/build/matplotlib output/pdf
MPLBACKEND=pdf MPLCONFIGDIR=submission/latex/build/matplotlib \
  python3 -B figures/src/figure-4-comparative-matrix.py
python3 -B submission/latex/build_manuscript.py
```

Compile twice with XeLaTeX so that page references and PDF bookmarks settle:

```sh
cd submission/latex
xelatex -interaction=nonstopmode -halt-on-error \
  -jobname=subjectivity-intersection-ontology-submission \
  -output-directory=build sio-manuscript.tex
xelatex -interaction=nonstopmode -halt-on-error \
  -jobname=subjectivity-intersection-ontology-submission \
  -output-directory=build sio-manuscript.tex
cp build/subjectivity-intersection-ontology-submission.pdf ../../output/pdf/
```

The final deliverable is:

`output/pdf/subjectivity-intersection-ontology-submission.pdf`

The layout is A4, single-column, 11 pt Latin Modern, with margins and title-page treatment matched to the author's reference paper.
