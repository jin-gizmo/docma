# Makefile to build doco. You must have pandoc installed.

dist=../dist

USER_GUIDE=docma-user-guide

DOC_AUTHOR=Murray Andrews
DOC_PUBLISHER=Jin-Gizmo
TOC_DEPTH=2

# FORMATS=md docx epub html site
FORMATS=md site epub

MARKDOWN_SRC=$(shell find user-guide -name '*.md')
IMAGES=$(sort $(wildcard img/*.png) $(wildcard img/*.jpg) $(wildcard img/*.svg))

DOCS=$(patsubst %,$(dist)/doc/$(USER_GUIDE).%,$(FORMATS))
CUSTOM_DICT=$(CURDIR)/.aspell-dict

DOCMA_VERSION=$(shell cat ../docma/VERSION)

all:	doc

doc:	user-guide api-doc
# doc:	user-guide

user-guide: DOC_TITLE=Docma User Guide
user-guide: $(DOCS)

api-doc:
	$(MAKE) -C api build dist=$(abspath $(dist))

clean:
	$(RM) -r $(DOCS) 
	$(RM) -r $(dist)/img
	$(MAKE) -C api $(MAKECMDGOALS)

# Markdown
$(dist)/doc/$(USER_GUIDE).md: $(MARKDOWN_SRC) $(IMAGES)
	@echo Generating $@
	@mkdir -p $(dist)/doc
	@find user-guide -name '*.md' -print0 | sort -z | xargs -0 -n1 sed -e '1s/^/\n/' > $@
	@cp -r img $(dist)/doc

%.docx:	%.md
	@echo Generating $@
	@sed -e 's/\.svg)/.eps)/g' < $< | pandoc --from markdown --to docx \
		--reference-doc style.docx \
		--toc --toc-depth=$(TOC_DEPTH) \
		--standalone \
		--metadata "title=$(DOC_TITLE)" \
		--metadata "subtitle=Version $(DOCMA_VERSION)" \
		--metadata "pagetitle=$(DOC_TITLE)" \
		--metadata "author=$(DOC_AUTHOR)" \
		--metadata "publisher=$(DOC_PUBLISHER)" \
		> $@ || $(RM) $@

%.epub:	%.md
	@echo Generating $@
	@pandoc --from markdown --to epub \
		--css=epub.css \
		--number-sections \
		--standalone \
		--metadata "title=$(DOC_TITLE)" \
		--metadata "subtitle=Version $(DOCMA_VERSION)" \
		--metadata "pagetitle=$(DOC_TITLE)" \
		--metadata "author=$(DOC_AUTHOR)" \
		--metadata "publisher=$(DOC_PUBLISHER)" \
		< $< > $@ || $(RM) $@

%.html:	%.md
	@echo Generating $@
	@pandoc --from markdown --to html \
		--include-in-header=style.html \
		--toc --toc-depth=$(TOC_DEPTH) \
		--number-sections \
		--standalone \
		--metadata "title=$(DOC_TITLE)" \
		--metadata "subtitle=Version $(DOCMA_VERSION)" \
		--metadata "pagetitle=$(DOC_TITLE)" \
		--metadata "author=$(DOC_AUTHOR)" \
		--metadata "publisher=$(DOC_PUBLISHER)" \
		< $< > $@ || $(RM) $@

# Generate prepared source area for published docs
%.src: %.md $(shell find mkdocs)
	@echo Generating $@
	@( \
		$(RM) -r "$@" ; \
		cp -RL mkdocs "$@" ; \
		../etc/jinja -p version="$(DOCMA_VERSION)" mkdocs/docs/index.md > "$@/docs/index.md" ; \
		../etc/md-split --config "$@/mkdocs.yml" --dir "$@/docs" $< ; \
	)

# Generate a standalone HTML site using mkdocs
%.site: %.src $(shell find mkdocs)
	@echo Generating $@
	mkdocs build --clean -f $</mkdocs.yml --site-dir $(abspath $@)

# Serve the user guide on port 8000 for local review
serve:	$(dist)/doc/$(USER_GUIDE).src
	mkdocs serve -f $</mkdocs.yml --open

# Spell check the user guide
spell:
	@for i in $$(find user-guide -name '*.md') ; \
	do \
		echo $$i ; \
		aspell -p $(CUSTOM_DICT) check $$i ; \
	done
