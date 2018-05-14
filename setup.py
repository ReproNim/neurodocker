import os
import re
from setuptools import find_packages
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def main():
    """Main setup function."""

    with open(os.path.join(here, 'README.md'), encoding='utf-8') as fp:
        long_description = fp.read()

    with open(os.path.join(here, 'requirements.txt')) as fp:
        requirements = [r.strip() for r in fp.readlines()]

    with open(os.path.join(here, 'requirements-dev.txt')) as fp:
        requirements_dev = [r.strip() for r in fp.readlines()]

    setup(
        name="neurodocker",
        version=find_version("neurodocker", "version.py"),
        license="Apache License, 2.0",
        description="Create custom containers for neuroimaging",
        long_description=long_description,
        long_description_content_type='text/markdown',
        url="https://github.com/kaczmarj/neurodocker",
        author="Jakub Kaczmarzyk",
        author_email="jakubk@mit.edu",
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
        ],
        keywords='containers neuroimaging reproducibility research',
        packages=find_packages(),
        package_data={
            'neurodocker': [
                'templates/*.yaml',
                'reprozip/utils/reprozip_trace_runner.sh']
        },
        install_requires=requirements,
        entry_points={
            "console_scripts": [
                "neurodocker=neurodocker.neurodocker:main"
            ],
        },
        python_requires='>=3.5',
        extras_require={
            'dev': requirements_dev,
        },
    )


if __name__ == '__main__':
    main()
