#!/usr/bin/env python3
"""
Extract metadata from YAML and generate LaTeX config files.

This script reads from metadata.yaml and generates:
- build/metadata_config.tex  (LaTeX macros for the thesis template)
- build/main.xmpdata         (PDF metadata for hyperxmp)
- build/abstract.tex         (plain LaTeX content to be \input{}'d)

Usage:
  python3 extract_metadata.py metadata.yaml build/metadata_config.tex build/main.xmpdata build/abstract.tex
"""

import sys
import yaml


def latex_escape(s: str) -> str:
    """Escape common LaTeX special characters in plain text."""
    if s is None:
        return ""
    return (
        s.replace("\\", r"\textbackslash{}")
        .replace("&", r"\&")
        .replace("%", r"\%")
        .replace("$", r"\$")
        .replace("#", r"\#")
        .replace("_", r"\_")
        .replace("{", r"\{")
        .replace("}", r"\}")
        .replace("~", r"\textasciitilde{}")
        .replace("^", r"\textasciicircum{}")
    )


def extract_metadata(metadata_file, output_tex, output_xmpdata, output_abstract_tex):
    """Extract metadata from YAML and generate metadata_config.tex, main.xmpdata, and abstract.tex."""
    try:
        with open(metadata_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(f"Error reading {metadata_file}: {e}", file=sys.stderr)
        return False

    if not data:
        print(f"Error: {metadata_file} is empty", file=sys.stderr)
        return False

    required = ["title", "author", "supervisor", "advisor", "date"]
    for field in required:
        if field not in data:
            print(f"Error: Missing required field '{field}' in {metadata_file}", file=sys.stderr)
            return False

    # Required fields (escape for LaTeX safety)
    title = latex_escape(str(data["title"]))
    author = latex_escape(str(data["author"]))
    supervisor = latex_escape(str(data["supervisor"]))
    advisor = latex_escape(str(data["advisor"]))
    date = str(data["date"])  # keep as-is if it's YYYY-MM-DD

    # Optional fields
    degree = latex_escape(str(data.get("degree", "MSc")))
    school = latex_escape(str(data.get("school", "School of Electrical Engineering")))
    department = latex_escape(str(data.get("department", "Department of Communications and Networking")))
    program = latex_escape(str(data.get("program", "Master's Programme in Electrical Engineering")))
    major = latex_escape(str(data.get("major", "Communications and Networking")))
    license_text = latex_escape(str(data.get("license", "CC BY-NC-SA 4.0")))

    keywords_raw = str(data.get("keywords", "") or "").strip()
    if keywords_raw:
        keywords_latex = latex_escape(r"\spc ".join(keywords_raw.split()))
        keywords_xmp = keywords_raw
    else:
        keywords_latex = "thesis"
        keywords_xmp = "thesis"

    abstract_raw = str(data.get("abstract", "") or "").strip()
    abstract_one_para = " ".join(abstract_raw.split())
    abstract_tex = latex_escape(abstract_one_para)

    # 1) Write abstract.tex (plain LaTeX content)
    try:
        with open(output_abstract_tex, "w", encoding="utf-8") as f:
            f.write(abstract_tex + "\n")
        print(f"✓ Generated: {output_abstract_tex}", file=sys.stderr)
    except Exception as e:
        print(f"Error writing {output_abstract_tex}: {e}", file=sys.stderr)
        return False

    # 2) Write metadata_config.tex
    tex_content = f"""% Auto-generated from metadata.yaml
% Do not edit manually - regenerate using: python3 extract_metadata.py

\\thesistitle{{{title}}}
\\author{{{author}}}
\\thesisauthor{{{author}}}
\\supervisor{{{supervisor}}}
\\advisor{{{advisor}}}
\\date{{{date}}}

% Aalto thesis class requirements
\\univdegree{{{degree}}}
\\school{{{school}}}
\\department{{{department}}}
\\degreeprogram{{{program}}}
\\major{{{major}}}
\\collaborativepartner{{}}
\\uselogo{{aalto!}}

% Copyright and keywords
\\copyrighttext{{\\noexpand\\textcopyright\\ \\number\\year. {author}. This work is licensed under {license_text}.}}{{\\noindent\\textcopyright\\ \\number\\year\\ {author}. This work is licensed under {license_text}.}}
\\keywords{{{keywords_latex}}}
"""

    try:
        with open(output_tex, "w", encoding="utf-8") as f:
            f.write(tex_content)
        print(f"✓ Generated: {output_tex}", file=sys.stderr)
    except Exception as e:
        print(f"Error writing {output_tex}: {e}", file=sys.stderr)
        return False

    # 3) Write main.xmpdata
    year = date.split("-")[0] if "-" in date else date
    xmpdata_content = f"""\\Title {{{title}}}
\\Author {{{author}}}
\\Language {{en}}
\\Copyright {{© {year} {author}}}
\\CopyrightURL {{}}
\\Subject {{thesis}}
\\Keywords {{{keywords_xmp}}}
"""

    try:
        with open(output_xmpdata, "w", encoding="utf-8") as f:
            f.write(xmpdata_content)
        print(f"✓ Generated: {output_xmpdata}", file=sys.stderr)
    except Exception as e:
        print(f"Error writing {output_xmpdata}: {e}", file=sys.stderr)
        return False

    return True


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(
            f"Usage: {sys.argv[0]} <metadata.yaml> <output.tex> <output.xmpdata> <abstract.tex>",
            file=sys.stderr,
        )
        sys.exit(1)

    metadata_yaml = sys.argv[1]
    out_tex = sys.argv[2]
    out_xmp = sys.argv[3]
    out_abs = sys.argv[4]

    ok = extract_metadata(metadata_yaml, out_tex, out_xmp, out_abs)
    sys.exit(0 if ok else 1)
