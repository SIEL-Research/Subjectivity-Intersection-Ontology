#!/usr/bin/env python3
"""Convert the author-approved Markdown manuscript into LaTeX fragments."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT = ROOT / "manuscript"
GENERATED = Path(__file__).resolve().parent / "generated"

CHAPTERS = [
    "01-introduction.md",
    "02-subjectivity-intersection-ontology.md",
    "03-comparative-ontological-methodology.md",
    "04-historical-review.md",
    "05-comparative-evaluation.md",
    "06-philosophical-implications-and-research-program.md",
    "07-conclusion.md",
]

TABLE_CAPTIONS = {
    "02-subjectivity-intersection-ontology.md": [
        "Ontological observability and possible observable consequences."
    ],
    "03-comparative-ontological-methodology.md": [
        "Structural evaluation criteria N1--N6.",
        "Criterion-level assessment categories.",
        "Template separating textual evidence, interpretive reconstruction, and structural assessment.",
    ],
    "04-historical-review.md": [
        "Criterion-level assessments: ancient Greek philosophy.",
        "Criterion-level assessments: Indian philosophical traditions.",
        "Criterion-level assessment: Christian Trinitarian ontology.",
        "Criterion-level assessments: German Idealism.",
        "Criterion-level assessments: process ontology and phenomenology.",
        "Criterion-level assessments: contemporary relational theories.",
    ],
    "05-comparative-evaluation.md": [
        "Consolidated criterion-level assessments across the comparison set."
    ],
    "appendix-a-open-research-methodology.md": [
        "Structure and status of materials in the public research repository."
    ],
}

SPECIAL_REPLACEMENTS = {
    "—": "---",
    "–": "--",
    "‑": "-",
    "“": "``",
    "”": "''",
    "’": "'",
    "‘": "`",
}

MATH_SYMBOLS = {
    "→": r"\(\rightarrow\)",
    "←": r"\(\leftarrow\)",
    "↓": r"\(\downarrow\)",
    "↑": r"\(\uparrow\)",
    "≠": r"\(\neq\)",
    "≤": r"\(\leq\)",
    "≥": r"\(\geq\)",
    "×": r"\(\times\)",
    "□": r"\(\square\)",
}


def escape_plain(text: str) -> str:
    for old, new in SPECIAL_REPLACEMENTS.items():
        text = text.replace(old, new)
    text = text.replace("\\", r"\textbackslash{}")
    for char, replacement in [
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
    ]:
        text = text.replace(char, replacement)
    for symbol, replacement in MATH_SYMBOLS.items():
        text = text.replace(symbol, replacement)
    return text


TOKEN_PATTERN = re.compile(
    r"(\\\(.+?\\\)|\[[^\]]+\]\([^\)]+\)|https?://[^\s]+|`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*)"
)


def inline(text: str) -> str:
    parts: list[str] = []
    position = 0
    for match in TOKEN_PATTERN.finditer(text):
        parts.append(escape_plain(text[position : match.start()]))
        token = match.group(0)
        if token.startswith(r"\("):
            parts.append(token)
        elif token.startswith(("http://", "https://")):
            url = token.rstrip(".,;")
            punctuation = token[len(url) :]
            parts.append(r"\url{" + url.replace("%", r"\%") + "}" + punctuation)
        elif token.startswith("["):
            link = re.fullmatch(r"\[([^\]]+)\]\(([^\)]+)\)", token)
            assert link
            label, url = link.groups()
            if label.strip("`") == url:
                parts.append(r"\url{" + url.replace("%", r"\%") + "}")
            else:
                parts.append(r"\href{" + url.replace("%", r"\%") + "}{" + inline(label) + "}")
        elif token.startswith("`"):
            content = token[1:-1]
            if any(symbol in content for symbol in MATH_SYMBOLS):
                rendered = escape_plain(content)
                parts.append(r"\texttt{" + rendered + "}")
            else:
                rendered = escape_plain(content)
                parts.append(r"\texttt{" + rendered + "}")
        elif token.startswith("**"):
            parts.append(r"\textbf{" + inline(token[2:-2]) + "}")
        else:
            parts.append(r"\emph{" + inline(token[1:-1]) + "}")
        position = match.end()
    parts.append(escape_plain(text[position:]))
    return "".join(parts)


def strip_number(title: str) -> str:
    return re.sub(r"^(?:[A-Z]|\d+)(?:\.\d+)*\.?\s+", "", title).strip()


def heading_inline(text: str) -> str:
    rendered = inline(text)
    if any(symbol in text for symbol in MATH_SYMBOLS):
        plain = text
        for symbol, replacement in {
            "→": " to ",
            "←": " from ",
            "↓": " then ",
            "↑": " above ",
            "≠": " not equal to ",
            "≤": " at most ",
            "≥": " at least ",
            "×": " by ",
            "□": " ",
        }.items():
            plain = plain.replace(symbol, replacement)
        return r"\texorpdfstring{" + rendered + "}{" + escape_plain(plain) + "}"
    return rendered


def centered_code(lines: list[str]) -> str:
    normalized = [
        line.replace("├─", "+--")
        .replace("└─", "+--")
        .replace("──▶", "-->")
        .replace("─", "-")
        .replace("₁", "_1")
        .replace("₂", "_2")
        .replace("₃", "_3")
        .replace("ₙ", "_n")
        for line in lines
    ]
    rendered = [inline(line) if line else r"\strut" for line in normalized]
    body = r"\\".join(rendered)
    return (
        "\\begin{center}\n"
        "\\begin{minipage}{.88\\textwidth}\n"
        "\\centering\\ttfamily " + body + "\n"
        "\\end{minipage}\n"
        "\\end{center}\n"
    )


def assessment_code(value: str) -> str:
    return {
        "Clear satisfaction": "C",
        "Partial": "P",
        "Partial or interpretation-dependent satisfaction": "P",
        "Non-satisfaction": "N",
        "Insufficient evidence": "I",
        "—": "--",
    }.get(value, value)


def table_latex(
    rows: list[list[str]], filename: str, table_index: int, label_prefix: str
) -> str:
    header, data = rows[0], rows[1:]
    caption = TABLE_CAPTIONS.get(filename, [])[table_index - 1]
    columns = len(header)
    is_assessment = columns == 7 and header[1:] == [f"N{i}" for i in range(1, 7)]

    if is_assessment:
        spec = r">{\RaggedRight\arraybackslash}p{.31\textwidth}*{6}{>{\centering\arraybackslash}p{.075\textwidth}}"
        font = r"\scriptsize"
        data = [[row[0]] + [assessment_code(value) for value in row[1:]] for row in data]
    elif columns == 2:
        spec = r">{\RaggedRight\arraybackslash}p{.25\textwidth}>{\RaggedRight\arraybackslash}X"
        font = r"\small"
    elif columns == 3:
        spec = r">{\RaggedRight\arraybackslash}p{.20\textwidth}>{\RaggedRight\arraybackslash}p{.47\textwidth}>{\RaggedRight\arraybackslash}X"
        font = r"\scriptsize"
    elif columns == 5:
        spec = r">{\RaggedRight\arraybackslash}p{.08\textwidth}*{4}{>{\RaggedRight\arraybackslash}X}"
        font = r"\scriptsize"
    else:
        spec = "*{" + str(columns) + r"}{>{\RaggedRight\arraybackslash}X}"
        font = r"\scriptsize"

    def row_tex(row: list[str]) -> str:
        return " & ".join(inline(cell) for cell in row) + r" \\"

    output = [
        r"\begin{table}[htbp]",
        r"\centering",
        font,
        r"\setlength{\tabcolsep}{3pt}",
        r"\renewcommand{\arraystretch}{1.18}",
        r"\begin{tabularx}{\textwidth}{" + spec + "}",
        r"\toprule",
        row_tex(header),
        r"\midrule",
    ]
    output.extend(row_tex(row) for row in data)
    output.extend(
        [
            r"\bottomrule",
            r"\end{tabularx}",
            r"\caption{" + caption + "}",
            rf"\label{{tab:{label_prefix}-{table_index}}}",
        ]
    )
    if is_assessment:
        output.append(r"\assessmentlegend")
    output.append(r"\end{table}")
    return "\n".join(output) + "\n"


def is_block_start(line: str) -> bool:
    return bool(
        not line.strip()
        or re.match(r"^#{1,6}\s+", line)
        or line.startswith("```")
        or line.startswith("|")
        or line.startswith("> ")
        or re.match(r"^[-*]\s+", line)
        or re.match(r"^\d+\.\s+", line)
        or line.strip() == r"\["
    )


def convert_chapter(path: Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    output: list[str] = []
    index = 0
    table_index = 0
    figure_one_inserted = False
    prototype_code_skipped = False
    figure_two_inserted = False
    figure_five_pending = False
    first_content = True

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped:
            index += 1
            continue

        if first_content and re.match(r"^(?:\d+|[A-Z])\.\s+", stripped):
            output.append(r"\section{" + inline(strip_number(stripped)) + "}\n")
            first_content = False
            index += 1
            continue
        first_content = False

        heading = re.match(r"^(#{2,4})\s+(.+)$", line)
        if heading:
            marks, raw_title = heading.groups()
            title = strip_number(raw_title)
            if len(marks) == 2:
                output.append(r"\subsection{" + heading_inline(title) + "}\n")
                figure_five_pending = path.name.startswith("06-") and "Formal and Empirical Research Program" in title
            elif len(marks) == 3:
                if raw_title.startswith(("Proposition", "Corollary", "Scope of Application")):
                    output.append(r"\subsubsection*{" + heading_inline(raw_title) + "}\n")
                else:
                    output.append(r"\subsubsection{" + heading_inline(title) + "}\n")
            else:
                output.append(r"\paragraph{" + inline(title.rstrip(".")) + "}\n")
            index += 1
            continue

        if stripped == r"\[":
            math_lines = [line]
            index += 1
            while index < len(lines):
                math_lines.append(lines[index])
                if lines[index].strip() == r"\]":
                    index += 1
                    break
                index += 1
            output.append("\n".join(math_lines) + "\n")
            continue

        if line.startswith("```"):
            code_lines: list[str] = []
            index += 1
            while index < len(lines) and not lines[index].startswith("```"):
                code_lines.append(lines[index])
                index += 1
            index += 1
            joined = "\n".join(code_lines).strip()
            if (
                path.name.startswith("02-")
                and "Absolute Subjectivity S" in joined
                and not prototype_code_skipped
            ):
                prototype_code_skipped = True
                continue
            if path.name.startswith("02-") and joined == "AB → C → AB" and not figure_two_inserted:
                output.append(r"\[\mathrm{AB}\rightarrow C\rightarrow\mathrm{AB}\]" + "\n")
                output.append(r"\SIOFigureTwo" + "\n")
                figure_two_inserted = True
            else:
                output.append(centered_code(code_lines))
            continue

        if line.startswith("|"):
            table_lines: list[str] = []
            while index < len(lines) and lines[index].startswith("|"):
                table_lines.append(lines[index])
                index += 1
            parsed = [
                [cell.strip() for cell in row.strip().strip("|").split("|")]
                for row in table_lines
            ]
            rows = [parsed[0]] + parsed[2:]
            table_index += 1
            if path.name.startswith("05-") and table_index == 1:
                output.append(r"\SIOFigureFour" + "\n")
            else:
                output.append(
                    table_latex(rows, path.name, table_index, path.stem.replace("_", "-"))
                )
            if path.name.startswith("03-") and table_index == 1:
                output.append(r"\SIOFigureThree" + "\n")
            continue

        if line.startswith("> "):
            quote_lines: list[str] = []
            while index < len(lines) and lines[index].startswith("> "):
                quote_lines.append(lines[index][2:].strip())
                index += 1
            output.append(r"\begin{quote}\itshape " + inline(" ".join(quote_lines)) + r"\end{quote}" + "\n")
            continue

        if re.match(r"^[-*]\s+", line):
            items: list[str] = []
            while index < len(lines):
                if re.match(r"^[-*]\s+", lines[index]):
                    items.append(re.sub(r"^[-*]\s+", "", lines[index]).strip())
                    index += 1
                elif not lines[index].strip():
                    index += 1
                else:
                    break
            output.append("\\begin{itemize}\n" + "\n".join(r"\item " + inline(item) for item in items) + "\n\\end{itemize}\n")
            continue

        if line.startswith("1. **Ontological proposition**"):
            items: list[tuple[str, str]] = []
            while index < len(lines) and len(items) < 4:
                item_match = re.match(r"^\d+\.\s+\*\*(.+?)\*\*\s*$", lines[index])
                if not item_match:
                    break
                title = item_match.group(1)
                index += 1
                while index < len(lines) and not lines[index].strip():
                    index += 1
                description_lines: list[str] = []
                while index < len(lines) and lines[index].strip() and not re.match(r"^\d+\.\s+", lines[index]):
                    description_lines.append(lines[index].strip())
                    index += 1
                while index < len(lines) and not lines[index].strip():
                    index += 1
                items.append((title, " ".join(description_lines)))
            output.append("\\begin{enumerate}\n")
            for title, description in items:
                output.append(r"\item \textbf{" + inline(title) + ".} " + inline(description) + "\n")
            output.append("\\end{enumerate}\n")
            continue

        if re.match(r"^\d+\.\s+", line):
            items: list[str] = []
            while index < len(lines):
                if re.match(r"^\d+\.\s+", lines[index]):
                    items.append(re.sub(r"^\d+\.\s+", "", lines[index]).strip())
                    index += 1
                elif not lines[index].strip():
                    index += 1
                else:
                    break
            output.append("\\begin{enumerate}\n" + "\n".join(r"\item " + inline(item) for item in items) + "\n\\end{enumerate}\n")
            continue

        paragraph_lines = [line.strip()]
        index += 1
        while index < len(lines) and not is_block_start(lines[index]):
            paragraph_lines.append(lines[index].strip())
            index += 1
        paragraph = " ".join(paragraph_lines)
        output.append(inline(paragraph) + "\n\n")

        if path.name.startswith("02-") and paragraph == "This structure may be represented schematically as follows:" and not figure_one_inserted:
            output.append(r"\SIOFigureOne" + "\n")
            figure_one_inserted = True
        if figure_five_pending:
            output.append(r"\SIOFigureFive" + "\n")
            figure_five_pending = False

    return "".join(output)


def convert_abstract() -> str:
    lines = (MANUSCRIPT / "00-abstract.md").read_text(encoding="utf-8").splitlines()
    paragraphs: list[str] = []
    current: list[str] = []
    for line in lines:
        if line.startswith("#"):
            continue
        if not line.strip():
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        current.append(line.strip())
    if current:
        paragraphs.append(" ".join(current))
    body = [r"\begin{abstract}"]
    body.extend(inline(paragraph) + "\n\n" for paragraph in paragraphs)
    body.append(r"\end{abstract}" + "\n")
    return "".join(body)


def convert_appendix() -> str:
    path = MANUSCRIPT / "appendix-a-open-research-methodology.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    title = lines[2].strip()
    temporary = GENERATED / "appendix-a-open-research-methodology.md"
    temporary.write_text("A. " + title + "\n" + "\n".join(lines[3:]) + "\n", encoding="utf-8")
    try:
        converted = convert_chapter(temporary)
        return converted.replace(
            r"\section{Open Research Methodology and Repository Documentation}",
            r"\section{\texorpdfstring{Open Research Methodology and Repository\\Documentation}{Open Research Methodology and Repository Documentation}}",
        )
    finally:
        temporary.unlink(missing_ok=True)


def convert_references() -> str:
    lines = (MANUSCRIPT / "references.md").read_text(encoding="utf-8").splitlines()
    output = [r"\section*{References}", r"\addcontentsline{toc}{section}{References}", r"\begingroup\small\setstretch{1.08}"]
    paragraph: list[str] = []

    def flush() -> None:
        if paragraph:
            output.append(r"\referenceentry{" + inline(" ".join(paragraph)) + "}")
            paragraph.clear()

    for line in lines:
        if line.startswith("# References"):
            continue
        if line.startswith("## "):
            flush()
            output.append(r"\subsection*{" + inline(line[3:].strip()) + "}")
        elif not line.strip():
            flush()
        else:
            paragraph.append(line.strip())
    flush()
    output.append(r"\endgroup")
    return "\n\n".join(output) + "\n"


def main() -> None:
    GENERATED.mkdir(parents=True, exist_ok=True)
    (GENERATED / "00-abstract.tex").write_text(convert_abstract(), encoding="utf-8")
    for filename in CHAPTERS:
        source = MANUSCRIPT / filename
        (GENERATED / filename.replace(".md", ".tex")).write_text(
            convert_chapter(source), encoding="utf-8"
        )
    (GENERATED / "appendix-a-open-research-methodology.tex").write_text(
        convert_appendix(), encoding="utf-8"
    )
    (GENERATED / "references.tex").write_text(convert_references(), encoding="utf-8")


if __name__ == "__main__":
    main()
