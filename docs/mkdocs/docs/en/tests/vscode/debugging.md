---
title: Debugging
---
# Debugging

**Run and Debug** has these launch configurations:

| Configuration | What it debugs |
| --- | --- |
| `pytest: current file` | the tests of the open file, in Python |
| `pytest: unit tests` | all the unit tests |
| `pytest: integration tests (docker)` | all the integration tests, after building the module and starting the network |
| `C++: pytest current file (gdb)` | the tests of the open file, with gdb on the C++ of the module: the breakpoints of `src/cpp` stop |
| `C++: attach to a python process (gdb)` | gdb on a Python that already runs |
| `python: current file` | the open file, as a script |

The pytest configurations build the module first, and run without reruns, timeout and coverage.

## Into the C++

`C++: pytest current file (gdb)` starts Python under gdb with the module of `build-debug/`, which the task
`build: monero-python module (debug)` builds before it: a breakpoint in a file of `src/cpp` stops when a test calls it. It needs gdb
(`sudo apt install gdb`). For the code of monero-cpp, build it with `build: monero-cpp with debug info` first.

To be in Python and in C++ in the same run: start the test with `pytest: current file`, stop it at a breakpoint of Python, then attach
`C++: attach to a python process (gdb)` to the process of the test. Attaching to a process that gdb did not start needs
`kernel.yama.ptrace_scope=0`, or gdb as root.
