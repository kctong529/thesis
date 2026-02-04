#!/usr/bin/env python3
"""
Extract metadata from YAML and generate LaTeX config files.

This script ONLY reads from metadata.yaml. All data comes from the YAML file.
Sensible defaults are only used for optional fields that aren't in the YAML.
"""

import sys
import yaml
from pathlib import Path

def extract_metadata(metadata_file, output_tex, output_xmpdata):
    """Extract metadata from YAML and generate both files."""
    
    try:
        with open(metadata_file, 'r') as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(f"Error reading {metadata_file}: {e}", file=sys.stderr)
        return False
    
    if not data:
        print(f"Error: {metadata_file} is empty", file=sys.stderr)
        return False
    
    # Required fields - error if missing
    required = ['title', 'author', 'supervisor', 'advisor', 'date']
    for field in required:
        if field not in data:
            print(f"Error: Missing required field '{field}' in {metadata_file}", file=sys.stderr)
            return False
    
    # Extract all fields from YAML
    title = data['title']
    author = data['author']
    supervisor = data['supervisor']
    advisor = data['advisor']
    date = data['date']
    
    # Optional fields - only use defaults if not in YAML
    degree = data.get('degree', 'MSc')
    school = data.get('school', 'School of Electrical Engineering')
    department = data.get('department', 'Department of Communications and Networking')
    program = data.get('program', "Master's Programme in Electrical Engineering")
    major = data.get('major', 'Communications and Networking')
    license_text = data.get('license', 'CC BY-NC-SA 4.0')
    keywords = data.get('keywords', '')
    
    # Convert keywords to LaTeX format if provided
    if keywords:
        keywords_latex = '\\spc '.join(keywords.split())
    else:
        keywords_latex = 'thesis'
    
    # Generate metadata_config.tex
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

% Abstract (single paragraph from metadata)
\\thesisabstract{{ABSTRACT_PLACEHOLDER}}
"""
    
    try:
        with open(output_tex, 'w') as f:
            f.write(tex_content)
        print(f"✓ Generated: {output_tex}", file=sys.stderr)
    except Exception as e:
        print(f"Error writing {output_tex}: {e}", file=sys.stderr)
        return False
    
    # Generate main.xmpdata
    xmpdata_content = f"""\\Title {{{title}}}
\\Author {{{author}}}
\\Language {{en}}
\\Copyright {{© {date.split('-')[0]} {author}}}
\\CopyrightURL {{}}
\\Subject {{thesis}}
\\Keywords {{{keywords if keywords else 'thesis'}}}
"""
    
    try:
        with open(output_xmpdata, 'w') as f:
            f.write(xmpdata_content)
        print(f"✓ Generated: {output_xmpdata}", file=sys.stderr)
    except Exception as e:
        print(f"Error writing {output_xmpdata}: {e}", file=sys.stderr)
        return False
    
    return True

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <metadata.yaml> <output.tex> <output.xmpdata>")
        sys.exit(1)
    
    if extract_metadata(sys.argv[1], sys.argv[2], sys.argv[3]):
        sys.exit(0)
    else:
        sys.exit(1)
