import setuptools

from myeia.version import __version__

with open("README.md", "r") as ld:
    long_description = ld.read()

setuptools.setup(
    name="myeia",
    version=__version__,
    packages=["myeia"],
    include_package_data=True,
    install_requires=["backoff", "pandas", "requests", "python-dotenv"],
    url="https://github.com/philsv/myeia",
    license="MIT",
    author="philsv",
    author_email="frphsv@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["eia", "eia-api", "open-data", "python"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "License :: OSI Approved :: MIT License",
    ],
)
