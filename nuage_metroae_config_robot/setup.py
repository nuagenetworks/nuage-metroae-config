import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nuage-metroae-config-robot",
    version="0.0.2",
    author="Nuage Devops",
    author_email="devops@nuagenetworks.net",
    description="Library for Nuage MetroAE Config in Robot Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nuagenetworks/nuage-metroae-config",
    package_dir={'': 'src'},
    packages=['NuageMetroaeConfig'],
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
    install_requires=[
        "robotframework",
        "nuage-metroae-config"
    ]
)
