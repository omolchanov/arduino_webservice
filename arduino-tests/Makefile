tests:
	set -e; \
	for i in test_*/Makefile; do \
		$(MAKE) -s -C $$(dirname $$i); \
	done

runtests: tests
	set -e; \
	for i in test_*/Makefile; do \
		echo '==== $$(basename $$(dirname $$i))'; \
		$(MAKE) -s -C $$(dirname $$i) run; \
	done

clean:
	set -e; \
	for i in test_*/Makefile; do \
		$(MAKE) -s -C $$(dirname $$i) clean; \
	done
