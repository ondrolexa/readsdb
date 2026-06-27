# Packaging and deployment

## Packaging

This plugin is using the [qgis-plugin-ci](https://qgis.github.io/qgis-plugin-ci/) tool to perform packaging operations.  
Under the hood, the package command is performing a `git archive` run based on `CHANGELOG.md`.

Install additional dependencies:

```bash
python -m pip install -U -r requirements/packaging.txt
```

Then use it:

```bash
# package a specific version
qgis-plugin-ci package 1.3.1
# package latest version
qgis-plugin-ci package latest
```

## Release a version

Everything is done through the continuous deployment, sticking to a classic git workflow: 1 released version = 1 git tag.

Here comes the process for a tag `X.y.z` (which has to be SemVer compliant):

1. Add the new version to the `CHANGELOG.md`.You can write it manually or use the auto-generated release notes by Github:
    1. Go to your [project's releases](https://github.com/ondrolexa/readsdbreleases) and click on `Draft a new release`
    1. In `Choose a tag`, enter the new tag
    1. Click on `Generate release notes`
    1. Copy/paste the generated text from `## What's changed` until the line before `**Full changelog**:...` in the CHANGELOG.md replacing `What's changed` with the tag and the publication date.
1. Optionally change the version number in `metadata.txt`. It's recommended to use the next version number with `-DEV` suffix (e.g. `1.4.0-DEV` when `X.y.z` is `1.3.0` ) to avoid confusion during the development phase.
1. Apply a git tag with the relevant version: `git tag -a X.y.z {git commit hash} -m "This version rocks!"`
1. Push tag to main branch: `git push origin X.y.z` or `git push --tags` if you want to push all tags at once.
1. The CI/CD pipeline will be triggered and will create a new release on your Git repository and publish it to the [official QGIS plugins repository](https://plugins.qgis.org/) (if you picked up the option).

If things go wrong (failed CI/CD pipeline, missed step...), here comes the fix process:

```sh
git tag -d old
git push origin :refs/tags/old
git push --tags
```

And try again!
