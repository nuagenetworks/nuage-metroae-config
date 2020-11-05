import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nuage-metroae-config",
    version="0.0.4",
    author="Nuage Devops",
    author_email="devops@nuagenetworks.net",
    description="Template-based configuration tool for Nuage Networks VSD",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nuagenetworks/nuage-metroae-config",
    packages=["nuage_metroae_config"],
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7,<3',
    install_requires=[
        "bambou",
        "Jinja2",
        "lark-parser",
        "PyYAML"
    ]
)
