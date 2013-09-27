CXXFLAGS := -Wno-unknown-pragmas
PALAVER_VERSION := $(shell git describe --tags --always --dirty 2> /dev/null)

ifneq "$(PALAVER_VERSION)" ""
	CXXFLAGS += -DPALAVER_VERSION=\"$(PALAVER_VERSION)\"
endif

palaver.so: palaver.cpp
	@CXXFLAGS="$(CXXFLAGS)" znc-buildmod palaver.cpp

install: palaver.so
	@echo "Installing palaver.so to $(HOME)/.znc/modules/palaver.so"
	@cp palaver.so $(HOME)/.znc/modules/palaver.so

clean:
	-rm -f palaver.so

uninstall:
	@echo "Uninstall palaver from $(HOME)/.znc/modules"
	-rm -f $(HOME)/.znc/modules/palaver.so

