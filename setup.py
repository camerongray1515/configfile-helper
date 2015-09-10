from setuptools import setup

setup(  name="ConfigFileHelper",
        version="1.0.0",
        packages=["cfh"],
        entry_points={
            "console_scripts": [
                "cfh = cfh.configfilehelper:main"
            ]
        })
