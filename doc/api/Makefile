# Minimal makefile for Sphinx documentation

BASEDIR=$(shell cd ../.. && pwd)
dist=$(BASEDIR)/dist

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SOURCEDIR     = .
BUILDDIR      = $(dist)/doc/api/_build

DOCMA_VERSION=$(shell cat $(BASEDIR)/docma/VERSION)


# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile zip init

zip:	$(dist)/doc/docma-api-doc-$(DOCMA_VERSION).zip

# Create / update the *.rst files. We don't need --full, or modules.rst (hence the --no-toc)
init:
	@echo Creating/updating API doc setup
	@sphinx-apidoc -q -o . --no-toc --separate --module-first --ext-autodoc --ext-viewcode \
		$(BASEDIR) \
		$(BASEDIR)/setup.py

$(dist)/doc/docma-api-doc-$(DOCMA_VERSION).zip: init html
	@echo Generating $@
	@mkdir -p $(dist)/doc
	@(cd $(BUILDDIR)/html && zip -q -r - .) > $@

clean:
	$(RM) $(dist)/doc/docma-api-doc-$(DOCMA_VERSION).zip
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%:	Makefile 
	$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
