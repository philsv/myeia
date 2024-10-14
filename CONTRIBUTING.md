# Contributing to myeia
We love your input! We want to make contributing to this project as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features

## Report bugs using Github's [issues](https://github.com/philsv/myeia/issues/)
We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/philsv/myeia/issues/new); it's that easy!

Write bug reports with detail, background, and sample code if possible. **Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can.
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## Github Actions
We use Github Actions to automate the testing and deployment of the package. The workflow is defined in the `.github/workflows` directory.
To get your code merged into the main branch, you need to pass the tests. Feel free to extend the tests to cover your code.
For a successful test run it's necessary to [set the EIA_TOKEN as secret](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository) in your Fork.

## License
By contributing, you agree that your contributions will be licensed under its [MIT License](LICENSE).