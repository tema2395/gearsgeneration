import math
import numpy as np
from shapely.geometry import Polygon, MultiPolygon

def polar_ellipse_radius(a,b,theta):
    """
    Полярное задание эллипса:
      R = (a*b) / sqrt((b*cos(theta))^2 + (a*sin(theta))^2).
    """
    denom = (b*math.cos(theta))**2 + (a*math.sin(theta))**2
    if denom<=0:
        return 0
    return (a*b)/math.sqrt(denom)

def involute_profile(base_radius, start_r, end_r, n_points=20):
    """
    Генерация точек инволюты от start_r до end_r 
    (где start_r >= base_radius, end_r >= start_r).
    t = sqrt((r/base_r)^2 - 1).
    Возвращает список (x,y). (Локальная инволюта, ось X "радиальная").
    """
    import math

    def t_of_r(r):
        if r<base_radius:
            return 0
        return math.sqrt((r/base_radius)**2 - 1)

    t1 = t_of_r(start_r)
    t2 = t_of_r(end_r)
    points = []
    for i in range(n_points):
        t = t1 + (t2 - t1)*(i/(n_points-1) if n_points>1 else 0)
        x = base_radius*(math.cos(t) + t*math.sin(t))
        y = base_radius*(math.sin(t) - t*math.cos(t))
        points.append((x,y))
    return points

def unify_segments(geometry):
    """
    Превращает Polygon / MultiPolygon (shapely) в список отрезков [( (x1,y1),(x2,y2) ), ...]
    Берём только exterior-координаты.
    """
    lines = []
    if geometry.is_empty:
        return lines

    geom_type = geometry.geom_type
    if geom_type == 'Polygon':
        lines += polygon_to_lines(geometry)
    elif geom_type == 'MultiPolygon':
        for g in geometry.geoms:
            lines += polygon_to_lines(g)
    else:
        # Возможно GeometryCollection, обойдём все geoms
        if hasattr(geometry, 'geoms'):
            for gg in geometry.geoms:
                lines += unify_segments(gg)
    return lines

def polygon_to_lines(poly: Polygon):
    """
    Берём exterior полигона -> список отрезков.
    """
    coords = list(poly.exterior.coords)
    segments = []
    for i in range(len(coords)-1):
        p1 = coords[i]
        p2 = coords[i+1]
        segments.append(((p1[0],p1[1]), (p2[0],p2[1])))
    return segments
