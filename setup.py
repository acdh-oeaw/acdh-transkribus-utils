from setuptools import setup

with open("README.md") as readme_file:
    readme = readme_file.read()


setup(
    name="acdh-transkribus-utils",
    version="2.2",
    description="""some utility function to interact with the Transkribus-API""",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Peter Andorfer",
    author_email="peter.andorfer@oeaw.ac.at",
    url="https://github.com/acdh-oeaw/acdh-transkribus-utils",
    packages=[
        "transkribus_utils",
    ],
    entry_points={
        "console_scripts": [
            "import-goobi-mets-to-transkribus=transkribus_utils.cli:import_goobi_mets_to_transkribus",
        ]
    },
    include_package_data=True,
    install_requires=["requests", "lxml", "click"],
    license="MIT",
    zip_safe=False,
    keywords="acdh-transkribus-utils",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Django :: 2.0",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
)
