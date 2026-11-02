# Shortcuts for Linux/macOS. On Windows: python scripts/tasks.py <task>
.PHONY: setup test catchup evals reset
setup:   ; python scripts/tasks.py setup
test:    ; python scripts/tasks.py test $(LAB)
lab%:    ; python scripts/tasks.py test $*
catchup: ; python scripts/tasks.py catchup $(LAB)
evals:   ; python scripts/tasks.py evals $(ARGS)
reset:   ; python scripts/tasks.py reset
