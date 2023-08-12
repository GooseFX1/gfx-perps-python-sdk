from setuptools import setup, find_packages

setup(
    name='gfx_perps_sdk',
    version='0.0.9',
    url='https://github.com/GooseFX1/gfx-perp-python-sdk',
    author='Shashank Shekhar',
    author_email='shashank@goosefx.io',
    description='Perp python sdk',
    packages=['gfx_perp_python_sdk'],    
    install_requires=[
        'pytest'
    ],
)