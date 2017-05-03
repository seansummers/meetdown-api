from setuptools import setup

setup(
    name='meetdown',
    packages=['meetdown'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask_graphql',
        'graphene',
    ],
)
