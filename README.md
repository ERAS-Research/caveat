# CAVEAT
Context-Aware Verification, Emulation, and Training

## Scope

Verification using vendor-specific as well as independent simulators and frameworks is a fundamental
and well established step to successful digital design. Similarly, software-defined configuration and
operation of hardware has significantly improved accessibility of technology. In fact, modern software-defined
experiment design allows scientists and cross-disciplinary users to propose novel modes of
operation within hours or even minutes.

This vendor-agnostic framework decouples application development, design verification, and training from the immediate availability of sensitive, unwieldy, and costly hardware installations.
Moreover, it facilitates feasibility studies prior to investments as well as reproducibility of research results.

The framework is designed with three distinct needs of academic and development laboratories in mind:
1. streamlining context-aware verification for supervised operation,
2. hardware emulation for ease of application software development, and
3. an environment for experiential training of prospective users.

It distinguishes two distinct aspects of verification:
1. static (topologic), and
2. dynamic (algorithmic).

We will provide example's on how to do this...

### Dependencies
(see requirements.txt)


### Installation (inside virtual environment)
``` Bash
sudo apt install python-venv
```
**activate virtual env**
```Bash
python3 -m venv caveatenv
source caveatenv/bin/activate
```

Then ensure `build` is installed

```Bash
python3 -m pip install build
```

**Install locally**

In the caveat top level directory where `pyproject.toml` lives, run:
```Bash
pip install -e .
```

To test the installed code, navigate to `example/` and run:
```Bash
./run_tests.py
```
The test *test_loopback_throughput* will execute, and the results are placed in the subdirectory `build/results/`.


### Recommended Tools (optional)
- python 3.11+
- pip
- venv
- **pytest-reporter-html-dots** for advanced html reporting
- **pytest-xdist** for test parallelization (or pytest-parallel)


### Repository Structure

#### Issues

#### Pull Requests
