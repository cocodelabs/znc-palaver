PALAVER_VERSION := $(shell git describe --tags --always --dirty 2> /dev/null || cat VERSION)
CXXFLAGS := -Wno-unknown-pragmas -DPALAVER_VERSION=\"$(PALAVER_VERSION)\"

palaver.so: test palaver.cpp
	@echo "Building palaver.so"
	@CXXFLAGS="$(CXXFLAGS)" znc-buildmod palaver.cpp

install: palaver.so
	@echo "Installing palaver.so to $(HOME)/.znc/modules/palaver.so"
	@mkdir -p $(HOME)/.znc/modules
	@cp palaver.so $(HOME)/.znc/modules/palaver.so

clean:
	-rm -f palaver.so

uninstall:
	@echo "Uninstall palaver from $(HOME)/.znc/modules"
	-rm -f $(HOME)/.znc/modules/palaver.so

test-regex: test-regex.cpp
	@c++ -std=c++11 test-regex.cpp -o test-regex

.PHONY: test
test: test-regex
	@./test-regex
