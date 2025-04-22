from setuptools import setup, find_packages

setup(
    name="ownmine",
    version="2.0.0",
    description="Self-hosted Minecraft Server Manager",
    author="Igor Nunes",
    author_email="",
    packages=find_packages(),
    python_requires=">=3.11",
    entry_points={
        'console_scripts': [
            'ownmine=ownmine.cli:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: MIT License",
        "Topic :: System :: Systems Administration",
        "Topic :: Games/Entertainment :: Simulation",
    ],
)
