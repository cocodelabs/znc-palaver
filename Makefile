palaver.so: test palaver.cpp
	@echo "Building palaver.so"
	@znc-buildmod palaver.cpp

install: palaver.so
	@echo "Installing palaver.so to $(HOME)/.znc/modules/palaver.so"
	@mkdir -p $(HOME)/.znc/modules
	@cp palaver.so $(HOME)/.znc/modules/palaver.so

clean:
	-rm -f palaver.so test-regex

uninstall:
	@echo "Uninstall palaver from $(HOME)/.znc/modules"
	-rm -f $(HOME)/.znc/modules/palaver.so

test-regex: test-regex.cpp
	@$(CXX) -std=c++11 test-regex.cpp -o test-regex

.PHONY: test
test: test-regex
	@./test-regex
