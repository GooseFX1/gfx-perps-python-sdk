from setuptools import setup, find_packages

setup(
    name='Gfx_perps_sdk',
    version='0.0.1',
    url='https://github.com/GooseFX1/gfx-perp-python-sdk',
    author='Shashank Shekhar',
    author_email='shashank@goosefx.io',
    description='Perp python sdk',
    packages=['Gfx_perps_sdk'],    
    install_requires=[
        'pytest'
    ],
)