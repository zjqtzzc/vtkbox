import setuptools

setuptools.setup(
    name="vtktool",
    version="0.1.2",
    author="Zice",
    description="Zice's vtk tool",
    py_modules=['vtktool'],
    install_requires=['vtk'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
