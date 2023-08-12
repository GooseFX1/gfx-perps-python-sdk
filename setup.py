from setuptools import setup, find_packages

setup(
    name='gfx_perp_sdk',
    version='0.0.1',
    url='https://github.com/GooseFX1/gfx-perps-python-sdk',
    author='Shashank Shekhar',
    author_email='shashank@goosefx.io',
    description='Perp python sdk',
    packages=['gfx_perp_sdk'],    
    install_requires=[
        'pytest'
    ],
)