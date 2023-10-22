[![CI](https://github.com/lpenz/ptfuzzmenu/actions/workflows/ci.yml/badge.svg)](https://github.com/lpenz/ptfuzzmenu/actions/workflows/ci.yml)
[![coveralls](https://coveralls.io/repos/github/lpenz/ptfuzzmenu/badge.svg?branch=main)](https://coveralls.io/github/lpenz/ptfuzzmenu?branch=main)
[![PyPI](https://img.shields.io/pypi/v/ptfuzzmenu)](https://pypi.org/project/ptfuzzmenu/)

# ptfuzzmenu

A fuzzy-filtering menu widget for prompt-toolkit


## Installation


### Releases

ptfuzzmenu can be installed via [pypi]:

```
pip install ptfuzzmenu
```


### Repository

We can also clone the github repository and install ptfuzzmenu from it with:

```
pip install .
```

We can also install it for the current user only by running instead:

```
pip install --user .
```


## Development

ptfuzzmenu uses the standard python3 infra. To develop and test the module:
- Clone the repository and go into the directory:
  ```
  git clone git@github.com:lpenz/ptfuzzmenu.git
  cd ptfuzzmenu
  ```
- Use [`venv`] to create a local virtual environment with
  ```
  python -m venv venv
  ```
- Activate the environment by running the shell-specific `activate`
  script in `./venv/bin/`. For [fish], for instance, run:
  ```
  source ./venv/bin/activate.fish
  ```
- Install ptfuzzmenu in "editable mode":
  ```
  pip install -e '.[test]'
  ```
- To run the tests:
  ```
  pytest
  ```
  Or, to run the tests with coverage:
  ```
  pytest --cov
  ```
- Finally, to exit the environment and clean it up:
  ```
  deactivate
  rm -rf venv
  ```


[pypi]: https://pypi.org/project/ptfuzzmenu/
[`venv`]: https://docs.python.org/3/library/venv.html
