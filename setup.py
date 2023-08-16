from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='gfx_perp_sdk',
    version='0.0.2',
    url='https://github.com/GooseFX1/gfx-perps-python-sdk',
    author='Shashank Shekhar',
    author_email='shashank@goosefx.io',
    description='Perp python sdk',
    packages=['gfx_perp_sdk'],    
    install_requires=[
        'pytest'
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
)
