################################################################################
# Thesis Build System
# 2-phase hybrid build: Markdown → LaTeX → PDF via Pandoc + pdflatex
################################################################################

BUILD_DIR = build
CHAPTERS_DIR = chapters
METADATA = metadata.yaml
MAIN_TEX = main.tex
FINAL_PDF = $(BUILD_DIR)/thesis.pdf
PANDOC_ARGS = --from=markdown --to=latex --top-level-division=section

# Color output
BOLD = \033[1m
GREEN = \033[92m
YELLOW = \033[93m
CYAN = \033[96m
RESET = \033[0m

.DEFAULT_GOAL := pdf

################################################################################
# HELP
################################################################################

help:
	@echo "$(BOLD)Thesis Build System$(RESET)"
	@echo ""
	@echo "$(BOLD)Usage:$(RESET)"
	@echo "  make [target]"
	@echo ""
	@echo "$(BOLD)Main Targets:$(RESET)"
	@echo "  $(CYAN)pdf$(RESET)            Build thesis PDF (default)"
	@echo "  $(CYAN)clean$(RESET)          Remove build artifacts"
	@echo "  $(CYAN)chapters$(RESET)       Generate thesis chapter structure"
	@echo ""
	@echo "$(BOLD)Utilities:$(RESET)"
	@echo "  $(CYAN)verify$(RESET)          Check chapter structure and files"
	@echo "  $(CYAN)log$(RESET)             Show last 100 lines of pdflatex log"
	@echo "  $(CYAN)open$(RESET)            Open compiled PDF in default viewer"
	@echo "  $(CYAN)status$(RESET)          Show build status"
	@echo "  $(CYAN)install-deps$(RESET)    Show dependency installation"
	@echo ""
	@echo "$(BOLD)Examples:$(RESET)"
	@echo "  make pdf             # Build PDF"
	@echo "  make clean && make   # Clean rebuild"
	@echo "  make verify          # Check structure"
	@echo "  make open            # View PDF"
	@echo ""
	@echo "$(BOLD)Configuration:$(RESET)"
	@echo "  Edit $(CYAN)metadata.yaml$(RESET) to change thesis metadata"
	@echo "  Edit chapter files in $(CYAN)chapters/*/$(RESET) to write content"

################################################################################
# PRIMARY BUILD TARGET
################################################################################

pdf: chapters $(FINAL_PDF)
	@echo ""
	@echo "$(GREEN)✓ Build complete$(RESET)"
	@echo "  Output: $(FINAL_PDF)"

$(FINAL_PDF): $(METADATA) $(MAIN_TEX) | $(BUILD_DIR)
	@echo "$(BOLD)=== PHASE 1: Prepare Thesis Content ===$(RESET)"
	@echo ""
	
	@echo "  [1/4] Extracting metadata..."
	@python3 extract_metadata.py $(METADATA) $(BUILD_DIR)/metadata_config.tex $(BUILD_DIR)/main.xmpdata
	@echo "        $(GREEN)✓$(RESET) Metadata extracted"
	
	@echo "  [2/4] Converting abstract..."
	@sed -n '/^abstract: |/,/^[a-z]/p' $(METADATA) | sed '1d;$$d' | pandoc $(PANDOC_ARGS) -o $(BUILD_DIR)/abstract.tex
	@echo "        $(GREEN)✓$(RESET) Abstract converted"
	
	@echo "  [3/4] Assembling chapters..."
	@rm -f $(BUILD_DIR)/full_body.md
	@for chap in intro migration multipath tradeoffs evaluation conclusion; do \
		if [ -d "$(CHAPTERS_DIR)/$$chap" ]; then \
			printf "        • $$chap ... "; \
			section_count=0; \
			chapter_title=$$(grep "^title:" $(CHAPTERS_DIR)/$$chap/config.yaml 2>/dev/null | sed 's/^title: //'); \
			echo "# $$chapter_title" >> $(BUILD_DIR)/full_body.md; \
			echo "" >> $(BUILD_DIR)/full_body.md; \
			while read -r line; do \
				if [ ! "$$(echo $$line | grep '^title:')" ] && [ ! "$$(echo $$line | grep '^#')" ]; then \
					section=$$(echo "$$line" | xargs); \
					if [ ! -z "$$section" ]; then \
						if [ -f "$(CHAPTERS_DIR)/$$chap/$$section.md" ]; then \
							cat "$(CHAPTERS_DIR)/$$chap/$$section.md" >> $(BUILD_DIR)/full_body.md; \
							printf "\n\n" >> $(BUILD_DIR)/full_body.md; \
							section_count=$$((section_count + 1)); \
						else \
							echo "$(YELLOW)⚠$(RESET) missing: $$section.md"; \
						fi \
					fi \
				fi \
			done < "$(CHAPTERS_DIR)/$$chap/config.yaml"; \
			echo "$$section_count sections"; \
		fi \
	done
	@echo "        $(GREEN)✓$(RESET) Chapters assembled"
	
	@echo "  [4/4] Converting to LaTeX..."
	@pandoc $(PANDOC_ARGS) $(BUILD_DIR)/full_body.md -o $(BUILD_DIR)/body.tex
	@echo "        $(GREEN)✓$(RESET) LaTeX conversion complete"
	
	@echo ""
	@echo "$(BOLD)=== PHASE 2: Compile to PDF ===$(RESET)"
	@echo ""
	
	@echo "  [1/2] First pass (build structure)..."
	@-pdflatex -interaction=nonstopmode -output-directory=$(BUILD_DIR) $(MAIN_TEX) > /dev/null 2>&1
	@echo "        $(GREEN)✓$(RESET) Structure built"
	
	@echo "  [2/2] Second pass (table of contents)..."
	@-pdflatex -interaction=nonstopmode -output-directory=$(BUILD_DIR) $(MAIN_TEX) > /dev/null 2>&1
	@echo "        $(GREEN)✓$(RESET) TOC generated"
	
	@echo ""
	@if [ -f $(BUILD_DIR)/main.pdf ]; then \
		mv $(BUILD_DIR)/main.pdf $(FINAL_PDF); \
		echo "$(GREEN)✓ PDF generated: $(FINAL_PDF)$(RESET)"; \
		ls -lh $(FINAL_PDF); \
	else \
		echo "$(YELLOW)✗ PDF generation failed - check 'make log'$(RESET)"; \
		exit 1; \
	fi

################################################################################
# BUILD DIRECTORY
################################################################################

$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)

################################################################################
# UTILITY TARGETS
################################################################################

chapters:
	@echo "Generating chapter structure..."
	@python3 gen_thesis.py --all
	@echo "$(GREEN)✓$(RESET) Chapters created in $(CHAPTERS_DIR)/"

verify:
	@echo "$(BOLD)Verifying thesis structure...$(RESET)"
	@echo ""
	@python3 gen_thesis.py --verify
	@echo ""
	@if [ -f "$(METADATA)" ]; then \
		echo "$(GREEN)✓$(RESET) metadata.yaml found"; \
	else \
		echo "$(YELLOW)✗$(RESET) metadata.yaml not found"; \
	fi
	@if [ -f "$(MAIN_TEX)" ]; then \
		echo "$(GREEN)✓$(RESET) main.tex found"; \
	else \
		echo "$(YELLOW)✗$(RESET) main.tex not found"; \
	fi
	@if [ -f "extract_metadata.py" ]; then \
		echo "$(GREEN)✓$(RESET) extract_metadata.py found"; \
	else \
		echo "$(YELLOW)✗$(RESET) extract_metadata.py not found"; \
	fi

log:
	@echo "$(BOLD)LaTeX Build Log (last 100 lines)$(RESET)"
	@echo ""
	@if [ -f $(BUILD_DIR)/main.log ]; then \
		tail -100 $(BUILD_DIR)/main.log; \
	else \
		echo "$(YELLOW)⚠$(RESET) No build log found. Run 'make build' first."; \
	fi

open:
	@if [ -f "$(FINAL_PDF)" ]; then \
		echo "Opening $(FINAL_PDF)..."; \
		open "$(FINAL_PDF)" 2>/dev/null || xdg-open "$(FINAL_PDF)" 2>/dev/null || echo "Could not open PDF"; \
	else \
		echo "$(YELLOW)✗$(RESET) PDF not found. Run 'make build' first."; \
	fi

status:
	@echo "$(BOLD)Thesis Build Status$(RESET)"
	@echo ""
	@if [ -f "$(FINAL_PDF)" ]; then \
		echo "$(GREEN)✓$(RESET) PDF built: $$(ls -lh $(FINAL_PDF) | awk '{print $$5, "- " $$6, $$7, $$8}')"; \
	else \
		echo "$(YELLOW)✗$(RESET) PDF not built"; \
	fi
	@echo "  Metadata: $(METADATA)"
	@echo "  Structure: $(CHAPTERS_DIR)/"
	@echo "  Output: $(FINAL_PDF)"

install-deps:
	@echo "$(BOLD)Installing dependencies...$(RESET)"
	@echo ""
	@echo "Required packages:"
	@echo "  • pandoc (markdown to LaTeX conversion)"
	@echo "  • texlive-latex-base (pdflatex)"
	@echo "  • texlive-fonts-recommended (fonts)"
	@echo "  • python3-yaml (YAML parsing)"
	@echo ""
	@echo "Ubuntu/Debian:"
	@echo "  sudo apt-get install pandoc texlive-latex-base texlive-latex-extra texlive-fonts-recommended python3-yaml"
	@echo ""
	@echo "macOS:"
	@echo "  brew install pandoc basictex"
	@echo "  pip3 install pyyaml"

################################################################################
# CLEANUP
################################################################################

clean:
	@echo "Cleaning build artifacts..."
	@rm -rf $(BUILD_DIR)
	@echo "$(GREEN)✓$(RESET) Build directory removed"

clean-all: clean
	@echo "$(YELLOW)⚠$(RESET) Removing all generated files including chapters..."
	@rm -rf $(CHAPTERS_DIR)
	@echo "$(GREEN)✓$(RESET) Clean complete"

################################################################################
# PHONY TARGETS (don't create files with these names)
################################################################################

.PHONY: help pdf clean clean-all chapters verify log open status install-deps