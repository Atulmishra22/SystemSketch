"""
Shape Pydantic Schemas with Discriminated Unions
https://docs.pydantic.dev/2.6/concepts/unions/#discriminated-unions
"""
from pydantic import BaseModel, Field
from typing import Literal, Union


class BaseShape(BaseModel):
    """Base shape with common properties"""
    id: str = Field(..., description="Unique shape identifier")
    color: str = Field(default="#2D5BFF", description="Shape color (hex)")
    userId: str = Field(default="anonymous", description="User who created the shape")


class Rectangle(BaseShape):
    """Rectangle shape"""
    type: Literal["rectangle"] = "rectangle"
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    width: float = Field(..., gt=0, description="Rectangle width")
    height: float = Field(..., gt=0, description="Rectangle height")


class Circle(BaseShape):
    """Circle shape"""
    type: Literal["circle"] = "circle"
    x: float = Field(..., description="Center X coordinate")
    y: float = Field(..., description="Center Y coordinate")
    radius: float = Field(..., gt=0, description="Circle radius")


class Arrow(BaseShape):
    """Arrow shape (line with arrowhead)"""
    type: Literal["arrow"] = "arrow"
    x1: float = Field(..., description="Start X coordinate")
    y1: float = Field(..., description="Start Y coordinate")
    x2: float = Field(..., description="End X coordinate")
    y2: float = Field(..., description="End Y coordinate")


class Text(BaseShape):
    """Text label"""
    type: Literal["text"] = "text"
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    content: str = Field(..., max_length=500, description="Text content")
    fontSize: int = Field(default=16, ge=8, le=72, description="Font size in pixels")


# Discriminated union of all shape types
Shape = Union[Rectangle, Circle, Arrow, Text]


class ShapesArray(BaseModel):
    """Container for array of shapes"""
    shapes: list[Shape] = Field(default_factory=list)
