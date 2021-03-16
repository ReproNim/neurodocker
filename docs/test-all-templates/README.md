# Test all Neurodocker templates

pytest --report-log report.json

1. In the project's root directory, run

```
pytest --report-log docs/test-all-templates/build_results.json docs/test-all-templates/test_all_templates.py
```

This can take hours. Optionally run in parallel with `-n` flag.

2. Again in the project's root directory, run `

```
python docs/test-all-templates/create_docs_build_results.py
```
This updates the `build_results.rst` file `docs/build_results.rst`.
