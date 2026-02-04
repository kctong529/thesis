#!/usr/bin/env python3

"""
Thesis Boilerplate Generator

Generates thesis chapter structure with support for custom templates and YAML configuration.
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional
import yaml

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Default chapters and sections for thesis
DEFAULT_CHAPTERS = {
    "intro": {
        "title": "Introduction",
        "sections": [
            "motivation",
            "problem-statement",
            "objectives-scope",
            "thesis-outline"
        ],
        "description": "Motivation, problem statement, objectives, scope and limitations, and thesis outline"
    },
    "migration": {
        "title": "Connection Migration in QUIC",
        "sections": [
            "design-goals-assumptions",
            "connection-identifiers",
            "nat-rebinding-path-validation",
            "anti-amplification-limits",
            "security-privacy-implications"
        ],
        "description": "Design goals, connection identifiers, path validation, anti-amplification, security and privacy"
    },
    "multipath": {
        "title": "Multipath QUIC",
        "sections": [
            "motivation-use-cases",
            "path-establishment-management",
            "identifiers-acknowledgements",
            "standardization-status"
        ],
        "description": "Motivation, path management, per-path acknowledgements, and standardization state"
    },
    "tradeoffs": {
        "title": "Design Trade-offs and Practical Considerations",
        "sections": [
            "complexity-implementation-cost",
            "performance-pitfalls",
            "middleboxes-deployment-constraints",
            "privacy-considerations"
        ],
        "description": "Complexity, performance, deployment challenges, and privacy implications"
    },
    "evaluation": {
        "title": "Exploratory Evaluation",
        "sections": [
            "experimental-setup",
            "migration-scenarios",
            "multipath-scenarios",
            "results-analysis"
        ],
        "description": "Controlled scenarios illustrating migration and multipath behavior"
    },
    "conclusion": {
        "title": "Conclusion",
        "sections": [
            "summary-findings",
            "research-questions-answers",
            "limitations",
            "future-work"
        ],
        "description": "Summary of findings, answers to research questions, limitations, and future work"
    }
}


class ThesisGenerator:
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.chapters_dir = self.root_dir / "chapters"
        
    def ensure_chapters_dir(self):
        """Ensure chapters directory exists"""
        self.chapters_dir.mkdir(parents=True, exist_ok=True)
        print(f"{Colors.OKGREEN}✓{Colors.ENDC} Chapters directory exists: {self.chapters_dir}")
    
    def title_case(self, text: str) -> str:
        """Convert kebab-case to Title Case"""
        return ' '.join(word.capitalize() for word in text.split('-'))
    
    def create_section_file(self, chapter: str, section: str, force: bool = False) -> bool:
        """Create a single section markdown file"""
        section_file = self.chapters_dir / chapter / f"{section}.md"
        
        if section_file.exists() and not force:
            print(f"{Colors.WARNING}⚠{Colors.ENDC}  {section_file} already exists (skip with --force)")
            return False
        
        title = self.title_case(section)
        
        # Simple template with TODO comments
        content = f"""## {title}

Write your content here.

<!-- TODO: Add introduction -->

<!-- TODO: Add main content -->

<!-- TODO: Add conclusion -->
"""
        
        section_file.parent.mkdir(parents=True, exist_ok=True)
        section_file.write_text(content, encoding='utf-8')
        print(f"{Colors.OKGREEN}✓{Colors.ENDC} Created {section_file}")
        return True
    
    def create_config_yaml(self, chapter: str, sections: List[str], force: bool = False) -> bool:
        """Create chapter config.yaml with chapter title and section order"""
        config_file = self.chapters_dir / chapter / "config.yaml"
        
        if config_file.exists() and not force:
            print(f"{Colors.WARNING}⚠{Colors.ENDC}  {config_file} already exists (skip with --force)")
            return False
        
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Get chapter title from DEFAULT_CHAPTERS or generate from chapter name
        chapter_title = DEFAULT_CHAPTERS.get(chapter, {}).get("title", self.title_case(chapter))
        
        # Write config with title on first line (used by Makefile)
        # Then list sections (one per line, no YAML object format)
        content = f"title: {chapter_title}\n"
        content += f"# List section files in order (without .md extension)\n\n"
        content += '\n'.join(sections)
        
        config_file.write_text(content, encoding='utf-8')
        print(f"{Colors.OKGREEN}✓{Colors.ENDC} Created {config_file}")
        return True
    
    def create_chapter(self, chapter: str, sections: Optional[List[str]] = None, 
                       force: bool = False, verbose: bool = False) -> bool:
        """Create a complete chapter with config and section files"""
        
        # Use default sections if not provided
        if sections is None:
            if chapter not in DEFAULT_CHAPTERS:
                print(f"{Colors.FAIL}✗{Colors.ENDC} Unknown chapter: {chapter}")
                return False
            sections = DEFAULT_CHAPTERS[chapter]["sections"]
        
        chapter_dir = self.chapters_dir / chapter
        
        # Check if chapter exists
        if chapter_dir.exists() and not force:
            print(f"{Colors.WARNING}⚠{Colors.ENDC}  Chapter '{chapter}' already exists at {chapter_dir}")
            print(f"   Use --force to overwrite")
            return False
        
        # Create chapter directory
        chapter_dir.mkdir(parents=True, exist_ok=True)
        print(f"{Colors.OKGREEN}✓{Colors.ENDC} Created chapter directory: {chapter_dir}")
        
        if verbose and chapter in DEFAULT_CHAPTERS:
            desc = DEFAULT_CHAPTERS[chapter]["description"]
            print(f"   Description: {desc}\n")
        
        # Create config.yaml
        self.create_config_yaml(chapter, sections, force=force)
        
        # Create section files
        for section in sections:
            self.create_section_file(chapter, section, force=force)
        
        return True
    
    def create_all_chapters(self, force: bool = False, verbose: bool = False) -> bool:
        """Create all default chapters"""
        self.ensure_chapters_dir()
        print()
        
        success_count = 0
        for chapter in DEFAULT_CHAPTERS.keys():
            print(f"{Colors.OKBLUE}→{Colors.ENDC} Chapter: {chapter}")
            if self.create_chapter(chapter, force=force, verbose=verbose):
                success_count += 1
            print()
        
        print(f"{Colors.OKGREEN}✅ Generated {success_count}/{len(DEFAULT_CHAPTERS)} chapters{Colors.ENDC}")
        return True
    
    def list_chapters(self):
        """List all available default chapters"""
        print(f"\n{Colors.BOLD}Available Default Chapters:{Colors.ENDC}\n")
        
        for chapter, info in DEFAULT_CHAPTERS.items():
            print(f"  {Colors.OKGREEN}{chapter}{Colors.ENDC}")
            print(f"    Title: {info['title']}")
            print(f"    Description: {info['description']}")
            print(f"    Sections: {', '.join(info['sections'])}")
            print()
    
    def verify_structure(self) -> Dict[str, List[str]]:
        """Verify existing chapter structure matches config"""
        if not self.chapters_dir.exists():
            print(f"{Colors.FAIL}✗{Colors.ENDC} No chapters directory found")
            return {}
        
        structure = {}
        
        for chapter_dir in sorted(self.chapters_dir.iterdir()):
            if not chapter_dir.is_dir():
                continue
            
            config_file = chapter_dir / "config.yaml"
            if not config_file.exists():
                print(f"{Colors.WARNING}⚠{Colors.ENDC}  Missing config: {config_file}")
                continue
            
            # Read config - first line is title, rest are sections
            sections = []
            with open(config_file, 'r') as f:
                for i, line in enumerate(f):
                    line = line.strip()
                    # Skip the title line and comment lines
                    if i == 0 and line.startswith('title:'):
                        continue
                    if line and not line.startswith('#'):
                        sections.append(line)
            
            structure[chapter_dir.name] = sections
            
            # Verify section files exist
            missing = []
            for section in sections:
                section_file = chapter_dir / f"{section}.md"
                if not section_file.exists():
                    missing.append(section)
            
            if missing:
                print(f"{Colors.WARNING}⚠{Colors.ENDC}  {chapter_dir.name}: Missing sections: {', '.join(missing)}")
            else:
                print(f"{Colors.OKGREEN}✓{Colors.ENDC}  {chapter_dir.name}: {len(sections)} sections")
        
        return structure


def main():
    parser = argparse.ArgumentParser(
        description='Thesis Boilerplate Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 gen_thesis.py --all                 Generate all default chapters
  python3 gen_thesis.py --chapter intro       Generate intro chapter
  python3 gen_thesis.py --chapter custom -s sec1 sec2 sec3    Custom chapter
  python3 gen_thesis.py --verify              Verify existing structure
  python3 gen_thesis.py --list                List available chapters
        """
    )
    
    parser.add_argument('-a', '--all', action='store_true',
                        help='Generate all default chapters')
    parser.add_argument('-c', '--chapter', type=str,
                        help='Generate specific chapter')
    parser.add_argument('-s', '--sections', nargs='+',
                        help='Custom sections for chapter (space-separated)')
    parser.add_argument('-l', '--list', action='store_true',
                        help='List all available chapters')
    parser.add_argument('-v', '--verify', action='store_true',
                        help='Verify existing chapter structure')
    parser.add_argument('-f', '--force', action='store_true',
                        help='Overwrite existing files')
    parser.add_argument('--verbose', action='store_true',
                        help='Verbose output')
    parser.add_argument('-d', '--directory', default='.',
                        help='Root directory for thesis (default: current)')
    
    args = parser.parse_args()
    
    gen = ThesisGenerator(args.directory)
    
    if args.list:
        gen.list_chapters()
        return 0
    
    if args.verify:
        print(f"\n{Colors.OKBLUE}Verifying thesis structure...{Colors.ENDC}\n")
        gen.verify_structure()
        return 0
    
    gen.ensure_chapters_dir()
    
    if args.all:
        print(f"\n{Colors.OKBLUE}Generating all chapters...{Colors.ENDC}\n")
        gen.create_all_chapters(force=args.force, verbose=args.verbose)
        
        print(f"\n{Colors.BOLD}Next steps:{Colors.ENDC}")
        print(f"  1. Review generated chapters: ls -la chapters/")
        print(f"  2. Edit section files to add content")
        print(f"  3. Run: {Colors.OKCYAN}make pdf{Colors.ENDC} to build thesis")
        print()
        return 0
    
    if args.chapter:
        chapter = args.chapter
        sections = args.sections if args.sections else None
        
        print(f"\n{Colors.OKBLUE}Generating chapter: {chapter}{Colors.ENDC}\n")
        
        if gen.create_chapter(chapter, sections=sections, force=args.force, verbose=args.verbose):
            print(f"\n{Colors.BOLD}Next steps:{Colors.ENDC}")
            print(f"  1. Edit chapter files: ls -la chapters/{chapter}/")
            print(f"  2. Run: {Colors.OKCYAN}make pdf{Colors.ENDC}")
            print()
            return 0
        else:
            return 1
    
    parser.print_help()
    return 0


if __name__ == '__main__':
    sys.exit(main())
