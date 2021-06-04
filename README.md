# vtkTool
方便测试时快速构建vtk对象并显示

---
### 主要函数
* vtk_show(*args, color: Union[bool, Iterable] = False, interactor=None, style=None)  
    - args： 输入数据，可以是vtkProp3D格式（如vtkActor、vtkAssembly）,或者numpy、list格式（按点云处理） 
    - color: 输入True-随机染色， 输入可迭代对象按rgb染色
    - 例子: vtk_show(a, b, c, color=True) 显示abc三个点云随机染色