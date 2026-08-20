SHELL := /bin/bash

.PHONY: check download verify iso clean

check:
	./scripts/check-dependencies.sh

download:
	./scripts/download-base.sh

verify:
	./scripts/verify-base.sh

iso: check download verify
	./scripts/build.sh

clean:
	rm -rf build work tmp dist
