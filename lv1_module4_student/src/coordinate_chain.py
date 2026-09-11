"""base-link-camera 좌표 변환 체인."""
from __future__ import annotations
import numpy as np
from .rotation import axis_angle_from_matrix, rot_x, rot_y, rot_z
from .transform import inv_T, make_T, transform_points

__all__ = ["CoordinateChain", "default_chain", "camera_point_to_base", "base_point_to_camera"]

class CoordinateChain:
    def __init__(self, root="base"):
        self.root = root
        self._parent = {}
        self._T = {}

    def add(self, parent, child, T):
        T = np.asarray(T, dtype=float)
        if T.shape != (4, 4):
            raise ValueError("4x4 동차변환이 필요합니다.")
        if child == self.root or child in self._parent:
            raise ValueError(f"프레임 {child!r}의 부모가 이미 정해졌습니다.")
        if parent == child:
            raise ValueError("부모와 자식 프레임은 달라야 합니다.")
        self._parent[child] = parent
        self._T[(parent, child)] = T.copy()
        try:
            self._path_to_root(child)
        except (KeyError, ValueError):
            del self._parent[child]
            del self._T[(parent, child)]
            raise
        return self

    def get(self, parent, child):
        return self._T[(parent, child)].copy()

    def frames(self):
        return [self.root] + list(self._parent.keys())

    def _path_to_root(self, frame):
        if frame == self.root:
            return [self.root]
        path, seen, current = [frame], set(), frame
        while current != self.root:
            if current in seen:
                raise ValueError("좌표계 체인에 순환이 있습니다.")
            seen.add(current)
            if current not in self._parent:
                raise KeyError(f"프레임 {frame!r}은 root에 연결되지 않았습니다.")
            current = self._parent[current]
            path.append(current)
        return path

    def T_from_root(self, frame):
        path = self._path_to_root(frame)
        result = np.eye(4)
        for index in range(len(path) - 1, 0, -1):
            parent, child = path[index], path[index - 1]
            result = result @ self._T[(parent, child)]
        return result

    def T(self, target, source):
        return inv_T(self.T_from_root(target)) @ self.T_from_root(source)

    def transform(self, target, source, P, w=1.0):
        return transform_points(self.T(target, source), P, w=w)

    def axis_angle(self, target, source):
        return axis_angle_from_matrix(self.T(target, source)[:3, :3])

def default_chain():
    T_base_link = make_T(rot_z(np.deg2rad(22.5)), [0.35, 0.05, 0.45])
    T_link_camera = make_T(rot_y(np.deg2rad(-22.5)) @ rot_x(np.deg2rad(67.5)), [0.12, 0.04, 0.18])
    return CoordinateChain("base").add("base", "link", T_base_link).add("link", "camera", T_link_camera)

def camera_point_to_base(p_cam, chain=None):
    chain = default_chain() if chain is None else chain
    return chain.transform("base", "camera", p_cam)

def base_point_to_camera(p_base, chain=None):
    chain = default_chain() if chain is None else chain
    return chain.transform("camera", "base", p_base)
