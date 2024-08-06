## Vinyl Development Wiki

# Running static type checking

Useful for catching bugs and other problems
`python -m mypy vinyl/cli/main.py`

Run Ruff (a fast linter with an autofixer)
`ruff .` (or with fixing) `ruff . --fix`

How to run pytest with a watcher
`watchmedo shell-command --patterns="*.py" --recursive --command="pytest"`

# Third Party Services

You'll want an .env file at the root of the project with the following keys.

```
AWS_ACCESS_KEY_ID='xxx'
AWS_SECRET_ACCESS_KEY='xxx'
```

## Generating references
When you've changed parts of Vinyl and want to update the reference:
- Make sure you are in a poetry shell (otherwise you risk oulling the live version of vinyl instead of the development version)
- `poetry shell`
- then run `python scripts/genereate_reference.py` to generate both table and column references


# How to publish to pypi

On main, make sure your latest commit has both passing tests and build. Make sure to update the version in `pyproject.toml` to the next desired version using `poetry version <version>` and commit those changes.

Once that is in a good state, tag the release like this:

- git tag -a <tagname> -m "your message here"

Example: git tag -a v0.0.1 -m "Initial release"

Then:

- git push origin <tagname>

Example: git push origin --tags

This will kick off a build and pypi deploy.

## Pytest

Make sure to run test name instead of absolute file paths (can be test file name or test name). Otherwise, you may run into flakey test behavior and import issues.

## Running the HTTP Server

For testing the http server locally for development, you can run the following command:
`uvicorn main:app --reload`

## Testing PyPi

Coming soon https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/#separate-workflow-for-publishing-to-testpypi
