"""회전 행렬, 재직교화, 축-각 및 쿼터니언 함수."""
from __future__ import annotations
import numpy as np
from .vectors import det, norm, normalize, skew

__all__ = ["rot_x", "rot_y", "rot_z", "rodrigues", "gram_schmidt", "orthogonality_error", "is_rotation", "axis_angle_from_matrix", "quaternion_from_axis_angle"]

def rot_x(theta):
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[1., 0., 0.], [0., c, -s], [0., s, c]])

def rot_y(theta):
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, 0., s], [0., 1., 0.], [-s, 0., c]])

def rot_z(theta):
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s, 0.], [s, c, 0.], [0., 0., 1.]])

def rodrigues(axis, theta):
    K = skew(normalize(axis))
    return np.eye(3) + np.sin(theta) * K + (1. - np.cos(theta)) * (K @ K)

def gram_schmidt(A):
    A = np.asarray(A, dtype=float)
    if A.ndim != 2 or A.shape[0] < A.shape[1]:
        raise ValueError("열 직교정규화가 가능한 2차원 행렬이 필요합니다.")
    Q = np.zeros_like(A)
    tol = max(A.shape) * np.finfo(float).eps * max(1., float(np.max(np.abs(A))) if A.size else 0.)
    for j in range(A.shape[1]):
        v = A[:, j].copy()
        for i in range(j):
            v -= np.sum(Q[:, i] * v) * Q[:, i]
        length = norm(v)
        if length <= tol:
            raise ValueError("선형종속인 열입니다.")
        Q[:, j] = v / length
    return Q

def orthogonality_error(R):
    R = np.asarray(R, dtype=float)
    if R.ndim != 2 or R.shape[0] != R.shape[1]:
        raise ValueError("정사각 행렬이 필요합니다.")
    E = R.T @ R - np.eye(R.shape[0])
    return float(np.sqrt(np.sum(E * E)))

def is_rotation(R, atol=1e-8):
    R = np.asarray(R, dtype=float)
    return R.shape == (3, 3) and orthogonality_error(R) <= atol and abs(det(R) - 1.) <= atol

def axis_angle_from_matrix(R, atol=1e-8):
    R = np.asarray(R, dtype=float)
    if not is_rotation(R, atol):
        raise ValueError("올바른 3x3 회전 행렬이 아닙니다.")
    theta = float(np.arccos(np.clip((np.trace(R) - 1.) / 2., -1., 1.)))
    if theta < atol:
        return np.array([1., 0., 0.]), 0.
    values, vectors = np.linalg.eig(R)
    axis = normalize(np.real(vectors[:, int(np.argmin(np.abs(values - 1.)))]))
    if abs(np.pi - theta) < atol:
        first = int(np.flatnonzero(np.abs(axis) > atol)[0])
        return (-axis if axis[first] < 0. else axis), theta
    antisymmetric = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]])
    if np.sum(axis * antisymmetric) < 0.:
        axis = -axis
    return axis, theta

def quaternion_from_axis_angle(axis, angle):
    axis = normalize(axis)
    return np.r_[axis * np.sin(angle / 2.), np.cos(angle / 2.)].astype(float)
