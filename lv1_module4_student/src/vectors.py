"""벡터 연산과 가우스 소거 기반 선형대수 함수."""
from __future__ import annotations
import numpy as np

__all__ = ["as_vector", "dot", "norm", "angle_between", "normalize", "project", "reject", "skew", "cross", "plane_normal", "row_echelon", "rank", "det", "gauss_eliminate", "inverse_gauss_jordan"]

def as_vector(v):
    arr = np.asarray(v, dtype=float)
    if arr.ndim != 1:
        raise ValueError(f"1차원 벡터가 필요합니다. 받은 shape={arr.shape}")
    return arr

def dot(a, b):
    a, b = as_vector(a), as_vector(b)
    if a.shape != b.shape:
        raise ValueError("두 벡터의 차원이 다릅니다.")
    return float(np.sum(a * b))

def norm(v):
    return float(np.sqrt(max(0.0, dot(v, v))))

def angle_between(a, b, degrees=True):
    a, b = as_vector(a), as_vector(b)
    denominator = norm(a) * norm(b)
    if denominator <= 1e-12:
        raise ValueError("영벡터와의 사이각은 정의되지 않습니다.")
    angle = float(np.arccos(np.clip(dot(a, b) / denominator, -1.0, 1.0)))
    return float(np.rad2deg(angle)) if degrees else angle

def normalize(v, eps=1e-12):
    arr = as_vector(v)
    length = norm(arr)
    if length < eps:
        raise ValueError("영벡터는 정규화할 수 없습니다.")
    return arr / length

def project(a, b):
    a, b = as_vector(a), as_vector(b)
    if a.shape != b.shape:
        raise ValueError("두 벡터의 차원이 다릅니다.")
    denominator = dot(b, b)
    if denominator <= 1e-24:
        raise ValueError("영벡터 방향으로 정사영할 수 없습니다.")
    return (dot(a, b) / denominator) * b

def reject(a, b):
    a, b = as_vector(a), as_vector(b)
    return a - project(a, b)

def skew(a):
    a = as_vector(a)
    if a.shape != (3,):
        raise ValueError("3차원 벡터가 필요합니다.")
    x, y, z = a
    return np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])

def cross(a, b):
    b = as_vector(b)
    if b.shape != (3,):
        raise ValueError("3차원 벡터가 필요합니다.")
    return skew(a) @ b

def plane_normal(P1, P2, P3):
    p1, p2, p3 = as_vector(P1), as_vector(P2), as_vector(P3)
    if p1.shape != (3,) or p2.shape != (3,) or p3.shape != (3,):
        raise ValueError("세 점은 모두 3차원이어야 합니다.")
    return normalize(cross(p2 - p1, p3 - p1))

def _matrix(A):
    arr = np.asarray(A, dtype=float)
    if arr.ndim != 2:
        raise ValueError("2차원 행렬이 필요합니다.")
    return arr

def row_echelon(A, pivoting=True):
    U = _matrix(A).copy()
    m, n = U.shape
    scale = max(1.0, float(np.max(np.abs(U))) if U.size else 0.0)
    tol = max(m, n) * np.finfo(float).eps * scale
    pivot_cols, swaps, row = [], 0, 0
    for col in range(n):
        if row == m:
            break
        pivot_row = row + int(np.argmax(np.abs(U[row:, col]))) if pivoting else row
        if abs(U[pivot_row, col]) <= tol:
            continue
        if pivot_row != row:
            U[[row, pivot_row]] = U[[pivot_row, row]]
            swaps += 1
        pivot_cols.append(col)
        for lower in range(row + 1, m):
            factor = U[lower, col] / U[row, col]
            U[lower, col:] -= factor * U[row, col:]
            U[lower, col] = 0.0
        row += 1
    return U, pivot_cols, swaps

def rank(A):
    return len(row_echelon(A)[1])

def det(A):
    arr = _matrix(A)
    if arr.shape[0] != arr.shape[1]:
        raise ValueError("정사각 행렬이 필요합니다.")
    U, pivots, swaps = row_echelon(arr)
    if len(pivots) < arr.shape[0]:
        return 0.0
    value = float(np.prod(np.diag(U)))
    return -value if swaps % 2 else value

def gauss_eliminate(A, b, pivoting=True, verbose=False):
    A, b = _matrix(A), as_vector(b)
    m, n = A.shape
    if m != n or b.shape != (m,):
        raise ValueError("A는 정사각 행렬이고 b의 길이는 행 수와 같아야 합니다.")
    Ab = np.column_stack((A, b)).astype(float)
    steps = [Ab.copy()]
    tol = n * np.finfo(float).eps * max(1.0, float(np.max(np.abs(A))))
    for col in range(n):
        pivot_row = col + int(np.argmax(np.abs(Ab[col:, col]))) if pivoting else col
        zero_pivot = abs(Ab[pivot_row, col]) <= tol if pivoting else Ab[pivot_row, col] == 0.0
        if zero_pivot:
            raise ZeroDivisionError("피벗이 0이므로 유일한 해가 없습니다.")
        if pivot_row != col:
            Ab[[col, pivot_row]] = Ab[[pivot_row, col]]
        for row in range(col + 1, n):
            factor = Ab[row, col] / Ab[col, col]
            Ab[row, col:] -= factor * Ab[col, col:]
            Ab[row, col] = 0.0
        steps.append(Ab.copy())
        if verbose:
            print(f"[Step {col + 1}]")
            print(Ab)
    x = np.zeros(n)
    for row in range(n - 1, -1, -1):
        x[row] = (Ab[row, -1] - np.sum(Ab[row, row + 1:n] * x[row + 1:n])) / Ab[row, row]
    return x, steps

def inverse_gauss_jordan(A):
    A = _matrix(A)
    m, n = A.shape
    if m != n:
        raise ValueError("정사각 행렬이 필요합니다.")
    AI = np.hstack((A.copy(), np.eye(n)))
    tol = n * np.finfo(float).eps * max(1.0, float(np.max(np.abs(A))))
    for col in range(n):
        pivot_row = col + int(np.argmax(np.abs(AI[col:, col])))
        if abs(AI[pivot_row, col]) <= tol:
            raise np.linalg.LinAlgError("특이행렬은 역행렬이 없습니다.")
        if pivot_row != col:
            AI[[col, pivot_row]] = AI[[pivot_row, col]]
        AI[col] /= AI[col, col]
        for row in range(n):
            if row != col:
                AI[row] -= AI[row, col] * AI[col]
    return AI[:, n:]
