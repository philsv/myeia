import setuptools

with open("README.md", "r") as ld:
    long_description = ld.read()

setuptools.setup(
    name="myeia",
    version="0.1.2",
    url="https://github.com/philsv/myeia",
    license="MIT",
    author="philsv",
    author_email="frphsv@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        "pandas",
    ],
    keywords=[
        "eia",
        "eia-api",
        "open-data",
        "python",
    ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "License :: OSI Approved :: MIT License",
    ],
)
