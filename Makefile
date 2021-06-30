DISTRO := $(shell lsb_release -si | tr A-Z a-z)
DISTRO_MAJOR_VERSION := $(shell lsb_release -sr | cut -d. -f1)
DISTRO_NAME := $(shell lsb_release -sc | tr A-Z a-z)
VERSION := $(shell head -n 1 debian-common/changelog | awk '{match( $$0, /\(.+?\)/); print substr( $$0, RSTART+1, RLENGTH-2 ) }' | cut -d- -f1 )

all:

install:
	mkdir -p $(DESTDIR)/usr/bin
	install -m755 cinp-autodoc $(DESTDIR)/usr/bin

version:
	echo $(VERSION)

clean:
	$(RM) -fr build
	$(RM) -f dpkg
	$(RM) -fr htmlcov
ifeq (ubuntu, $(DISTRO))
	dh_clean || true
endif

dist-clean: clean
	$(RM) -fr debian
	$(RM) -f dpkg-setup

.PHONY:: all install version clean dist-clean

test-distros:
	echo ubuntu-xenial

test-requires:
	echo flake8

lint:
	flake8 --ignore=E501,E201,E202,E111,E126,E114,E402 --statistics --exclude=migrations .

test:

.PHONY:: test-distroy lint-requires lint test-requires test

dpkg-distros:
	echo ubuntu-xenial ubuntu-bionic

dpkg-requires:
	echo dpkg-dev debhelper python3-dev python3-setuptools

dpkg-setup:
	./debian-setup
	touch dpkg-setup

dpkg:
	dpkg-buildpackage -b -us -uc
	touch dpkg

dpkg-file:
	echo $(shell ls ../*.deb)

.PHONY:: dpkg-distros dpkg-requires dpkg-setup dpkg-file
