# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

SPHINXAPIDOC  = sphinx-apidoc
SOURCEAPI     = source/api/
MOVIEBOT	  = ../moviebot
ALLAPIDOCOPTS = -e -M --tocfile moviebot --implicit-namespaces -o

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: rst
rst:
	$(SPHINXAPIDOC) $(ALLAPIDOCOPTS) $(SOURCEAPI) $(MOVIEBOT)
	@echo
	@echo "rst API documentation files generated. The .rst files are in $(SOURCEAPI)."

.PHONY: rstf
rstf:
	$(SPHINXAPIDOC) -f $(ALLAPIDOCOPTS) $(SOURCEAPI) $(MOVIEBOT)
	@echo
	@echo "rst API documentation files generated. The .rst files are in $(SOURCEAPI)."
