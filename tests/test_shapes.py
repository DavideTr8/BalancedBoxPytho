import pytest

from shapes.rectangle import Rectangle
from shapes.shapee import Shape
from shapes.triangle import Triangle

import math

p1, p2 = (4, 3), (6, 0)


def test_rectangle_area():
    rect = Rectangle(p1, p2)
    assert rect.area == 6


def test_infinite_rectangle_area():
    rect = Rectangle()
    assert rect.area == math.inf


def test_triangle_area():
    tria = Triangle(p1, p2)
    assert tria.area == 3


def test_infinite_triangle_area():
    tria = Triangle((-math.inf, math.inf), (math.inf, -math.inf))
    with pytest.raises(ValueError):
        tria.area


def test_midpoints():
    shap = Shape(p1, p2)
    assert shap.vertical_midpoint == 1.5
    assert shap.horizontal_midpoint == 5
