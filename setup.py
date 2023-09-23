import setuptools

setuptools.setup(
    name="zzctool",
    version="0.1.4",
    author="zjqtzzc",
    author_email="zjqtzzc1995@gmail.com",
    url='https://github.com/zjqtzzc/vtkTool',
    description="Zice's vtk tool",
    # py_modules=['vtktool'],
    packages=setuptools.find_packages(),
    install_requires=['vtk'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
