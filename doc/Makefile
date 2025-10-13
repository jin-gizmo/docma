# Makefile to build doco.

dist=../dist

export PYTHONPATH=..

USER_GUIDE=docma-user-guide

FORMATS=md site

MARKDOWN_SRC=$(shell find user-guide -name '*.md')
IMAGES=$(sort $(wildcard img/*.png) $(wildcard img/*.jpg) $(wildcard img/*.svg))

DOCS=$(patsubst %,$(dist)/doc/$(USER_GUIDE).%,$(FORMATS))
CUSTOM_DICT=$(CURDIR)/.aspell-dict

DOCMA_VERSION=$(shell cat ../docma/VERSION)

# This gets picked up in the custom mkdocs footer template
export md_footer_rhs:=v$(DOCMA_VERSION)

all:	doc

doc:	user-guide

user-guide: DOC_TITLE=Docma User Guide
user-guide: $(DOCS)


clean:
	$(RM) -r $(dist)/doc

# Markdown as a single file.
$(dist)/doc/$(USER_GUIDE).md: $(MARKDOWN_SRC) $(IMAGES)
	@echo Generating $@
	@mkdir -p $(dist)/doc
	@find user-guide -name '*.md' -print0 | sort -z | xargs -0 -n1 sed -e '1s/^/\n/' > $@
	@cp -r img $(dist)/doc

# Generate prepared source area for published docs
%.site: %.md $(shell find mkdocs)
	@echo Generating $@
	@( \
		$(RM) -r "$@" ; \
		cp -RL mkdocs "$@" ; \
		../etc/jinja -p version="$(DOCMA_VERSION)" mkdocs/docs/index.md > "$@/docs/index.md" ; \
		../etc/md-split --config "$@/mkdocs.yml" --dir "$@/docs" $< ; \
	)

# Serve the user guide on port 8000 for local review
serve:	$(dist)/doc/$(USER_GUIDE).site
	mkdocs serve -f $</mkdocs.yml --open

# Spell check the user guide
spell:
	@for i in $$(find user-guide -name '*.md') ; \
	do \
		echo $$i ; \
		aspell -p $(CUSTOM_DICT) check $$i ; \
	done
