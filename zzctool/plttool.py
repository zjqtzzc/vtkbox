from matplotlib import pyplot


def show_3d_points(points):
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    pyplot.plot(x, y)
    pyplot.axis('equal')
    pyplot.show()


def show_3d_points2(points):
    x = [p[1] for p in points]
    y = [p[2] for p in points]
    pyplot.plot(x, y)
    pyplot.axis('equal')
    pyplot.show()


def trans(points):
    x = [p[0] for p in points]
    y = [p[1] for p in points]
    return x, y
