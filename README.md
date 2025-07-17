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

### Repository Structure

#### Issues

#### Pull Requests


### Developer Notes

#### Installation

**Dependencies**

- python 3.11+
- pip
- venv
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

In the caveat top level directory where `pyproject.toml` lives and in your virtual environment:
```Bash
pip install -e .
```

this will install `caveat` locally, to test:
navigate to `example/` and in your virtual environment run:
```Bash
./run_tests.py
```
test_loopback_throughput will execute, and the results may be viewed in the `build/results/` folder .

#### Testing Environment

To run unit tests, go to the example directory of *caveat* repo and type `pytest`, or `./run_tests.py`. for now, only test_loopback_throughput exists, but more tests will be added over time.


### Recommended Tools (optional)
- **pytest-reporter-html-dots** for advanced html reporting
- **pytest-xdist** for test parallelization (or pytest-parallel)
