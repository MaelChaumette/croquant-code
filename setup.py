from setuptools import setup, find_packages


setup(
    name="complex-quantization",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "shapely",
        "matplotlib",
        "lazylinop",
        "seaborn",
        "pandas",
        "scipy",
        "tqdm"
    ]
)
