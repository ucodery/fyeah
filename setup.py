from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='f-yeah',
    version='0.1.0',
    author='Jeremiah Paige',
    author_email='ucodery@gmail.com',
    python_requires='>=3.6',
    packages=['fyeah'],
    url='https://github.com/ucodery/fyeah',
    license='BSD',
    description='Reusable f-strings',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
)
