"""Package setup for envoy-local."""

from setuptools import setup, find_packages

setup(
    name="envoy-local",
    version="0.1.0",
    description="Helper tool to spin up local Envoy proxy configs for service mesh testing.",
    author="envoy-local contributors",
    python_requires=">=3.8",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov",
        ]
    },
    entry_points={
        "console_scripts": [
            "envoy-local=envoy_local.cli:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Testing",
        "Topic :: Internet :: Proxy Servers",
    ],
)
