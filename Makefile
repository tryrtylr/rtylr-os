SHELL := /bin/bash
VERSION := $(strip $(shell cat VERSION))

.PHONY: check lint check-build test download verify iso validate-iso test-iso test-vm package-release print-version clean

check:
	./scripts/check-source.sh

lint:
	shellcheck scripts/*.sh config/kiosk/session.sh
	yamllint -c .yamllint config/autoinstall.yaml

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

# Builds a serial-console/poweroff test image and runs the QEMU smoke test.
# Needs the build dependencies; RTYLR_INSTALL_PASSWORD_HASH is optional.
test-iso: check-build download verify
	RTYLR_TEST_BUILD=1 ./scripts/build.sh

test-vm: test-iso
	./scripts/test-vm.sh

package-release: validate-iso
	./scripts/package-release.sh

print-version:
	@printf '%s\n' '$(VERSION)'

clean:
	rm -rf build work tmp dist
