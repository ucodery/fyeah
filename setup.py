from pathlib import Path
from setuptools import Extension, setup

with open("README.md", "r") as f:
    long_description = f.read()

moddir = Path(__file__).parent.resolve()

cmodule = Extension(
    "fyeah._cfyeah",
    sources=[str(moddir / "fyeah" / "_cfyeah.c")],
    include_dirs=[str(moddir / "build" / "cpython" / "Python")],
    extra_compile_args=["-std=c99"],  # necessary to package manylinux
    optional=True,
)

setup(
    name="f-yeah",
    version="0.3.0",
    author="Jeremiah Paige",
    author_email="ucodery@gmail.com",
    packages=["fyeah"],
    ext_modules=[cmodule],
    extras_require={
        "dev": [
            "tox",
        ]
    },
    url="https://github.com/ucodery/fyeah",
    license="BSD",
    description="Reusable f-strings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
)
