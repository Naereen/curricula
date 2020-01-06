from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="curricula",
    version="0.0.3",
    description="A content manager and grading toolkit for evaluating student code",
    url="https://github.com/csci104/curricula",
    author="Noah Kim",
    author_email="noahbkim@gmail.com",

    # Extra
    long_description=long_description,
    long_description_content_type="text/markdown",

    # Python
    python_requires=">=3.7",

    # Packaging
    packages=find_packages(),
    zip_safe=False,
    install_requires=["jinja2", "jsonschema"])
