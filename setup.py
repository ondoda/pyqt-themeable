from setuptools import setup, find_packages

setup(
    name="ondoda.pyqtthemeable",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'pyside6 => 6.7.2',
    ],
    author="joet-dev",
    author_email="joet-dev@ondoda.com",
    description="This package is used to simplify the process of theming PyQt applications.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/joet-dev/your_package_name",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)