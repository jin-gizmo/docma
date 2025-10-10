# Minimal makefile for Sphinx documentation

BASEDIR=$(shell cd ../.. && pwd)
dist=$(BASEDIR)/dist

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SOURCEDIR     = .
# BUILDDIR      = $(dist)/doc/api/_build
BUILDDIR      = $(dist)/doc/docma-user-guide.src/docs/api

DOCMA_VERSION=$(shell cat $(BASEDIR)/docma/VERSION)


# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile zip init

$(dist)/doc/docma-api-doc-$(DOCMA_VERSION).zip: init html
	@echo Generating $@
	@mkdir -p $(dist)/doc
	@(cd $(BUILDDIR)/html && zip -q -r - .) > $@

zip:	$(dist)/doc/docma-api-doc-$(DOCMA_VERSION).zip

# Create / update the *.rst files. We don't need --full, or modules.rst (hence the --no-toc)
# Also not trailing positional arguments are exclusions.
init:
	@echo Creating/updating API doc setup
	@sphinx-apidoc -q -o . --no-toc --separate --module-first --ext-autodoc --ext-viewcode \
		$(BASEDIR) \
		$(BASEDIR)/setup.py \
		$(BASEDIR)/docma/cli/ \
		$(BASEDIR)/docma/docma_core.py \
		$(BASEDIR)/docma/version.py \
		"$(BASEDIR)/docma/commands/*.py" \
		==SENTINEL==


clean:
	$(RM) $(dist)/doc/docma-api-doc-$(DOCMA_VERSION).zip
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)


build:	init
	@echo "Building Sphinx into MkDocs $(BUILDDIR)..."
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)"

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%:	Makefile 
	$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
