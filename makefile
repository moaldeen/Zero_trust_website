.PHONY: all build backup_files update_files compile_book modify_html_files finalize

# Default values for year and archive
ARCHIVE := false

# If YEAR is not provided, use the current year
YEAR ?= $(shell date +%Y)

# If YEAR is provided on the command line, override ARCHIVE to true
ifneq ($(filter command line, $(origin YEAR)),)
    ARCHIVE := true
endif

# Main target
all: build

# Build target
build: backup_files update_files compile_book modify_html_files finalize

# Backup files
backup_files:
	@echo "Backing up original files"
	@cp -f _config.yml _config.yml.bak
	@cp -f logo.svg logo.svg.bak

# Update files
update_files:
ifeq ($(ARCHIVE), true)
	@echo "Replace ${YEAR} with the actual year value in config"
	@sed -i 's/\$${year}/$(YEAR)/g' "_config.yml"
	@echo "Replace ${YEAR} in logo.svg"
	@sed -i 's/\$${year}/$(YEAR)/g' logo.svg
	@echo "Uncommenting announcement in _config.yml for archive"
	@sed -i 's/# announcement:/announcement:/g' "_config.yml"
else
	@echo "Replace ${YEAR} with the actual year value in config"
	@sed -i 's/\$${year}/latest/g' "_config.yml"
	@echo "Replace ${YEAR} in logo.svg"
	@sed -i 's/\$${year}/latest/g' logo.svg
endif

# Compile Jupyter book
compile_book:
	@jupyter-book clean .
	@echo "Running copy_and_tweak_files and building jupyter-book..."
	@python -c 'import jupyter_book_compile; jupyter_book_compile.copy_and_tweak_files()'
	@jupyter-book build .
	@python -c 'import jupyter_book_compile; jupyter_book_compile.clean()'

# Modify HTML files based on archive flag
modify_html_files:
	@echo "Modifying HTML files..."
ifeq ($(ARCHIVE), true)
	@python -c 'import jupyter_book_compile; jupyter_book_compile.modify_html_files(modify_names=True, remove_buttons=True)'
else
	@python -c 'import jupyter_book_compile; jupyter_book_compile.modify_html_files(modify_names=True, remove_buttons=False)'
endif

# Finalize the build process
finalize:
	@echo "Performing final file operations..."
	@cp .htaccess _build/html/
ifeq ($(ARCHIVE), true)
	@rm -rf _build/html/_sources
	@mv -f _build/html _build/$(YEAR)
else
	@mv -f _build/html _build/latest
endif	
	@mv -f _config.yml.bak _config.yml
	@mv -f logo.svg.bak logo.svg

# To build a specific year
# Usage: make YEAR=2025 or make
