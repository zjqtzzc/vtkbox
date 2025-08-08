import setuptools

setuptools.setup(
    name="vtkbox",
    version="0.2.0",
    author="zjqtzzc",
    author_email="zjqtzzc1995@gmail.com",
    url='https://github.com/zjqtzzc/vtkbox',
    description="一些个人常用的VTK函数",
    # py_modules=['vtktool'],
    packages=setuptools.find_packages(),
    install_requires=['vtk'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)
