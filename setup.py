from setuptools import setup, find_packages

setup(
    name="movrs-client",
    version="0.1.4",
    description="MOVRS Client GUI and CLI",
    author="Tariq Sarfaraz",
    packages=find_packages(),
    install_requires=[
        "PyQt6",
        "requests",
        "pyqt6_sip",
        "pyyaml",
        "requests"
    ],
    entry_points={
        "console_scripts": [
            "movrs-client=movrs_client.app:main"
        ]
    },
    include_package_data=True,
) 