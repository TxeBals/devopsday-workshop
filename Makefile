# Atajos para Linux/macOS. En Windows: python scripts/tasks.py <tarea>
.PHONY: setup test catchup evals reset
setup:   ; python scripts/tasks.py setup
test:    ; python scripts/tasks.py test $(LAB)
lab%:    ; python scripts/tasks.py test $*
catchup: ; python scripts/tasks.py catchup $(LAB)
evals:   ; python scripts/tasks.py evals $(ARGS)
reset:   ; python scripts/tasks.py reset
