# Contributing guidelines

### Pull Request Checklist

Before sending your pull requests, make sure you followed this list.

- Read [contributing guidelines](https://github.com/iai-group/moviebot/blob/master/CONTRIBUTING.md#contribution-guidelines).
- Check that changes are consistent with the [Coding Style](https://github.com/iai-group/moviebot/blob/master/CONTRIBUTING.md#python-coding-style).
- Run [Unit Tests](https://github.com/iai-group/moviebot/blob/master/CONTRIBUTING.md#running-unit-tests).



### Contribution guidelines

Before sending your pull request for
[review](https://github.com/iai-group/moviebot/pulls),
make sure your changes are consistent with the guidelines and follow the
[IAI group styles](https://github.com/iai-group/styleguide).

We usually recommend opening an issue before a pull request if there isn’t already an issue for the problem you’d like to solve. This helps facilitate a discussion before deciding on an implementation. Each pull request should then come from a new branch associated with a certain issue. This can be achieved as following.

```bash
git checkout master 
git pull
```

Git checkout -b branchtype(often feature)/#issue number_short_description. 

```bash
git checkout -b feature/#60_setup_guide
```

Do your changes with good commit messages, last commit should contain 'closing #issue_number'.
Then publish branch and create pull request on GitHub.


### Contributing code

#### Python coding style

Changes to IAI MovieBot should conform to
[IAI Python Style Guide](https://github.com/iai-group/styleguide/tree/master/python)

Use `pylint` to check your Python changes. You will also need `pylint-quotes` to check for single quote rule in the guidelines. To install `pylint` and check a file
with `pylint` against IAI MovieBot's custom style definition:

```bash
pip install pylint
pip install pylint-quotes
pylint --rcfile=.pylintrc myfile.py
```

#### Running unit tests

For any code you write, you should also write its unit tests. If you write a new file foo.py, you should place its unit tests in tests/unit/foo_test.py and submit it within the same change. 

```bash
pip install pytest
python -m pytest
```

Aim for >90% test coverage for all your code.
To get the coverage you can run pytest with parameter --cov=module.

```bash
pip install pytest-cov
pytest --cov=moviebot
```

Additionally, we can get the lines in the code that are not covered with the following command.

```bash
pytest --cov=moviebot --cov-report term-missing
```