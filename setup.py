from setuptools import setup, find_packages

setup(
    name="abake-use-engine",
    version="1.0.0",
    description="ABAKE USE Engine — Dynamic Pacing & Possession Scaling Basketball Analytics",
    author="ABAKE USE",
    packages=find_packages(),
    install_requires=[
        "flask>=3.0",
        "pandas>=2.0",
        "numpy>=1.24",
        "requests>=2.28",
        "beautifulsoup4>=4.12",
        "lxml>=4.9",
    ],
    python_requires=">=3.10",
)
