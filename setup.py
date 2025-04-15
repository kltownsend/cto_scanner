from setuptools import setup, find_packages

setup(
    name="cto_signal_scanner",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "feedparser==6.0.11",
        "python-dotenv==1.0.1",
        "openai==1.12.0",
    ],
) 