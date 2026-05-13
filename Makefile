test:
	pytest -v

# Build sdist + wheel locally for inspection.
# Publishing to PyPI happens via the `pythonpublish.yml` GitHub Actions
# workflow on a GitHub Release — do NOT `twine upload` from here.
dist: clean
	python setup.py sdist bdist_wheel

clean:
	rm -rf *.egg-info *.egg dist build .pytest_cache

.PHONY: test dist clean
