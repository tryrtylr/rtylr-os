SHELL := /bin/bash
VERSION := $(strip $(shell cat VERSION))

.PHONY: check check-build test download verify iso validate-iso package-release print-version clean

check:
	./scripts/check-source.sh

check-build:
	./scripts/check-dependencies.sh

test:
	PYTHONPATH=src/rtylr-shell python3 -m unittest discover -s tests -v

download:
	./scripts/download-base.sh

verify:
	./scripts/verify-base.sh

iso: check check-build download verify
	./scripts/build.sh

validate-iso:
	./scripts/validate-iso.sh

package-release: validate-iso
	./scripts/package-release.sh

print-version:
	@printf '%s\n' '$(VERSION)'

clean:
	rm -rf build work tmp dist
