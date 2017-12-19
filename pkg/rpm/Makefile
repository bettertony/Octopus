PACKAGE = octopus
PREFIX = /usr/lib/$(PACKAGE)

TOP_BUILDDIR = ../../
BINDIR = $(PREFIX)/bin
LIBDIR = $(PREFIX)/lib
BUILDROOT = $(CURDIR)/build

all: spec conf octopus octopus_kafka octopus-debug clean-libs set-perms
	mkdir $(CURDIR)/build
	cp -p -r --parents $(PREFIX) $(BUILDROOT)
	rpmbuild -bb -vv \
		--define "_topdir $(CURDIR)/rpmbuild" \
		--define "_tmppath $(CURDIR)/tmp" \
		 --buildroot $(BUILDROOT) octopus.spec
	mv $(CURDIR)/rpmbuild/RPMS/x86_64/*.rpm .

spec:
	sed -e 's/__VERSION__/$(PIPELINE_VERSION)/g' \
		-e 's:__PREFIX__:$(PREFIX):g' $(CURDIR)/octopus.spec.in > octopus.spec

set-perms:
	find $(PREFIX) -type d -exec chmod 755 {} +

conf:
	(cd $(TOP_BUILDDIR) && ./configure)

octopus:
	(cd $(TOP_BUILDDIR) && ./configure PIPELINE_VERSION=$(PIPELINE_VERSION) PIPELINE_REVISION=$(PIPELINE_REVISION) --prefix=$(PREFIX) --with-system-tzdata=/usr/share/zoneinfo CFLAGS="$(PIPELINE_CFLAGS)" --disable-rpath $(PIPELINE_WITH_OPTIONS))
	(cd $(TOP_BUILDDIR) && $(MAKE))
	(cd $(TOP_BUILDDIR) && $(MAKE) install)

octopus_kafka:
	git clone https://github.com/octopus/octopus_kafka.git
	(cd octopus_kafka && ./configure && make PG_CONFIG=$(BINDIR)/pg_config install)
	rm -rf octopus_kafka

octopus-debug:
	(cd $(TOP_BUILDDIR) && make clean)
	(cd $(TOP_BUILDDIR) && ./configure CFLAGS="-g -O0 -DDUMP_CORE" PIPELINE_VERSION=$(PIPELINE_VERSION) PIPELINE_REVISION=$(PIPELINE_REVISION) --prefix=$(PREFIX) --with-system-tzdata=/usr/share/zoneinfo --enable-cassert --disable-rpath $(PIPELINE_WITH_OPTIONS))
	(cd $(TOP_BUILDDIR) && $(MAKE) PIPELINE_SERVER_BINARY=octopus-debug)
	(cd $(TOP_BUILDDIR)/src/backend && $(MAKE) PIPELINE_SERVER_BINARY=octopus-debug install-server-bin )

clean-libs:
	find $(LIBDIR) -name "*.la" -exec rm {} \;

clean:
	rm -rf $(GEOS)* $(GDAL)* $(PROJ)* rpmbuild tmp octopus.spec
