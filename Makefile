SHELL := /bin/bash

.PHONY: check lint download verify iso test-iso test-vm clean

check:
	./scripts/check-dependencies.sh

lint:
	shellcheck scripts/*.sh config/kiosk/session.sh
	yamllint -c .yamllint config/autoinstall.yaml

download:
	./scripts/download-base.sh

verify:
	./scripts/verify-base.sh

iso: check download verify
	./scripts/build.sh

# Builds a serial-console/poweroff test image and runs the QEMU smoke test.
# Needs RTYLR_INSTALL_PASSWORD_HASH in the environment.
test-iso: check download verify
	RTYLR_TEST_BUILD=1 ./scripts/build.sh

test-vm: test-iso
	./scripts/test-vm.sh

clean:
	rm -rf build work tmp dist
