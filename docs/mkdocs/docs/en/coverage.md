---
title: Coverage
---
# Coverage

The reports of the last CI run on `main`, made by the unit and the integration tests together{% if commit %}, on commit
[`{{ commit[:7] }}`]({{ config.repo_url }}/tree/{{ commit }}){ target="_blank" rel="noopener" }{% endif %}. Each one shows, in its title, the commit that it was made on.

| Report | What it measures |
| --- | --- |
| <a href="tests/" target="_blank" rel="noopener">Tests</a> | the Python code of the tests (`tests/`), with coverage.py |
| <a href="bindings/" target="_blank" rel="noopener">Bindings</a> | the C++ code of the Python bindings (`src/cpp`), with gcov and lcov |
| <a href="monero-cpp/" target="_blank" rel="noopener">monero-cpp</a> | the C++ library that the bindings wrap (`external/monero-cpp/src`), with gcov and lcov |
