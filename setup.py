from setuptools import setup, find_packages

setup(
    name="solar-feasibility-checker",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "python-dotenv",
        "pytest",
        "openai",
    ],
)
