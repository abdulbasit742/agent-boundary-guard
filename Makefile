.PHONY: test scan-example

test:
	python -m unittest discover -s tests -v

scan-example:
	python -m agent_boundary_guard scan tests/fixtures/risky_repo
