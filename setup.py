import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

version = '0.2.1'
setuptools.setup(
    name='blink-cameras',
    version=version,
    author='Derek Anderson',
    author_email='public@kered.org',
    description='Python API for the Blink Home Security Camera System',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    install_requires=[
        'python-dateutil',
        'pyyaml',
        'requests'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: LGPL License',
        'Operating System :: OS Independent'])
