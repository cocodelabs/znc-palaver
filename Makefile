build: test palaver.so

palaver.so: palaver.cpp
	@echo "Building palaver.so"
	@znc-buildmod palaver.cpp

install: palaver.so
	@echo "Installing palaver.so to $(HOME)/.znc/modules/palaver.so"
	@mkdir -p $(HOME)/.znc/modules
	@cp $^ $(HOME)/.znc/modules/palaver.so

clean:
	-rm -f palaver.so test-regex

uninstall:
	@echo "Uninstall palaver from $(HOME)/.znc/modules"
	-rm -f $(HOME)/.znc/modules/palaver.so

test-regex: test-regex.cpp
	@$(CXX) -std=c++11 $< -o $@

.PHONY: test
test: test-regex
	@./test-regex

test/fixtures/modules/palaver.so: palaver.so
	@mkdir -p test/fixtures/modules
	@cp $< $@

.PHONY: test-integration
test-integration: test/fixtures/modules/palaver.so
	@mkdir test-reports
	pytest --junitxml=test-reports/junit.xml
