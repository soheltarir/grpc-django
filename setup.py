import codecs
import pathlib

try:
    codecs.lookup('mbcs')
except LookupError:
    ascii = codecs.lookup('ascii')
    func = lambda name, enc=ascii: {True: enc}.get(name == 'mbcs')
    codecs.register(func)

from setuptools import find_packages, setup

version = "1.0.0"

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="grpc-django",
    version=version,
    packages=find_packages(exclude=["tests*", "manage.py", "docs"]),
    include_package_data=True,
    python_requires='>3.5.0',
    install_requires=[
        "Django >= 1.9",
        "grpcio",
        "grpcio-tools",
        "google",
        "six",
        "djangorestframework"
    ],
    author="Sohel Tarir",
    author_email="sohel.tarir@gmail.com",
    description="gRPC Integration with Django Framework",
    long_description=README,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/soheltarir/grpc-django",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
