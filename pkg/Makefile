# Copyright (c) 2013-2015 Octopus
changelog = $(CURDIR)/debian/changelog

changelog:
	echo "octopus ($(PIPELINE_VERSION)-1) UNRELEASED; urgency=low" > $(changelog)
	echo "" >> $(changelog)
	echo "`git log --oneline $(PREV_PIPELINE_VERSION)..$(PIPELINE_VERSION) | sed -e 's/^/  * /'`" >> $(changelog)
	echo "" >> $(changelog)
	echo " -- Octopus Packaging <packaging@octopus.com>  `date +"%a, %d %b %Y %T %z"`" >> $(changelog)

deb: changelog
	dpkg-buildpackage -us -uc -b
	mv $(CURDIR)/../*.deb .
	rm $(CURDIR)/../*.changes

rpm:
	$(MAKE) -C $@
	mv $(CURDIR)/rpm/*.rpm .

osx:
	$(MAKE) -C $@

clean:
	$(MAKE) -f debian/rules clean
	$(MAKE) -C rpm clean
	$(MAKE) -C osx clean

.PHONY: deb rpm osx
