# Minimal makefile for Sphinx landing page documentation

SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
OUTPUTDIR     = ../../docs
DOCTREEDIR    = .doctrees

.PHONY: html clean help

help:
	@echo "Please use 'make <target>' where <target> is one of:"
	@echo "  html     to make standalone HTML files"

html:
	@$(SPHINXBUILD) -b html -d $(DOCTREEDIR) $(SPHINXOPTS) $(SOURCEDIR) $(OUTPUTDIR)
	@echo "Build finished. The HTML pages are in $(OUTPUTDIR)."

clean:
	rm -rf $(DOCTREEDIR)
