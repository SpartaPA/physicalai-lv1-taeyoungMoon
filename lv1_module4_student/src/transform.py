"""문제 5 — 4x4 동차변환 모듈. (학생 작성용 템플릿)

동차변환 생성/역변환, 점과 방향의 구분, 벡터화된 점군 변환,
정규방정식 기반 최소자승법을 직접 구현한다.
"""

from __future__ import annotations

import numpy as np

from .vectors import inverse_gauss_jordan

__all__ = [
    "make_T",
    "inv_T",
    "inv_T_batch",
    "to_homogeneous",
    "transform_point",
    "transform_direction",
    "transform_points",
    "least_squares_normal_equation",
    "rmse",
]


def make_T(R, t) -> np.ndarray:
    """회전 R(3x3)과 병진 t(3,)로 4x4 동차변환을 만든다.

        T = [[R, t],
             [0, 1]]

    R 이 3x3 이 아니면 ValueError.
    """
    # TODO: 문제 5-1
    R_arr = np.asarray(R, dtype=float)
    if R_arr.shape != (3,3):
        raise ValueError ("R은 3x3 행렬이어야 합니다.")
    t_arr = np.asarray(t, dtype=float)
    if t_arr.shape != (3,):
        raise ValueError("t는 (3,) 벡터여야 합니다.")
    T = np.eye(4, dtype=float)
    T[:3,:3] = R_arr
    T[0:3,3] = t_arr

    return T


def inv_T(T) -> np.ndarray:
    """동차변환의 역변환. **일반 역행렬 함수를 쓰지 않고** 공식으로 구한다.

        T^-1 = [[R^T, -R^T t],
                [  0,      1]]

    유도: T^-1 을 [[S, u], [0, 1]] 로 두고 T T^-1 = I 를 풀면
          R S = I -> S = R^T (R 이 직교),  R u + t = 0 -> u = -R^T t.

    4x4 가 아니면 ValueError.
    """
    # TODO: 문제 5-1
    T_arr = np.asarray(T, dtype=float)

    if T_arr.shape != (4,4):
        raise ValueError ("T는 4x4 행렬이어야 합니다.")

    R = T_arr[:3, :3]
    t = T_arr[:3, 3]

    R_inv = R.T
    t_inv = -R_inv @ t

    return make_T(R_inv, t_inv)


def inv_T_batch(Ts) -> np.ndarray:
    """(N, 4, 4) 동차변환 묶음을 **반복문 없이** 한 번에 역변환한다.

    `inv_T` 와 같은 공식을 배치 축으로 확장한 것이다.
    문제 5-4 의 속도 비교에서 쓴다 — 단건 호출은 파이썬/NumPy 호출 오버헤드가
    지배해서 연산량 차이가 드러나지 않기 때문이다.

    힌트: 전치는 `np.swapaxes(..., 1, 2)`, 배치 행렬-벡터 곱은
          `np.einsum("nij,nj->ni", ...)` 로 쓸 수 있다.
    """
    # TODO: 문제 5-4
    Ts_arr = np.asarray(Ts, dtype=float)
    if Ts_arr.ndim != 3 or Ts_arr.shape[1:] != (4, 4):
        raise ValueError("Ts는 (N, 4, 4) 차원의 배열이어야 합니다.")
    N = Ts_arr.shape[0]

    # 2. 배치 슬라이싱 추출
    R = Ts_arr[:, :3, :3]  # (N, 3, 3)
    t = Ts_arr[:, :3, 3]   # (N, 3)

    # 3. 배치 단위 역회전 및 역병진 계산
    R_inv = np.swapaxes(R, 1, 2)                   # (N, 3, 3)
    t_inv = np.einsum("nij,nj->ni", -R_inv, t)     # (N, 3)

    # 4. 결과 배치 동차변환 행렬 할당 및 반환
    inv_Ts = np.zeros((N, 4, 4), dtype=float)
    inv_Ts[:, :3, :3] = R_inv
    inv_Ts[:, :3, 3] = t_inv
    inv_Ts[:, 3, 3] = 1.0

    return inv_Ts

def to_homogeneous(P, w: float = 1.0) -> np.ndarray:
    """(3,) 또는 (N,3) 좌표에 마지막 성분 w 를 붙인다.

    w = 1 이면 점(위치), w = 0 이면 방향(벡터).
    """
    # TODO: 문제 5-2
    P_arr = np.asarray(P, dtype = float)

    if P_arr.ndim == 1 and P_arr.shape[0] == 3:
        return np.append(P_arr, w)
    elif P_arr.ndim == 2 and P_arr.shape[1] == 3:
        N = P_arr.shape[0] # 차원수
        w_col = np.full((N, 1), w, dtype=float)
        return np.hstack([P_arr, w_col])
    else:
        raise ValueError("P는 (3,) 또는 (N,3) 크기의 좌표여야 합니다.")


def transform_point(T, p) -> np.ndarray:
    """점 변환 (w = 1): 회전과 병진이 모두 적용된다. 반환은 (3,)."""
    # TODO: 문제 5-2
    T_arr = np.asarray(T, dtype=float)
    p_arr = np.asarray(p, dtype=float)

    if T_arr.shape != (4, 4):
        raise ValueError("T는 4x4 행렬이어야 합니다.")
    if p_arr.shape != (3,):
        raise ValueError("p는 (3,) 크기의 좌표여야 합니다.")
    
    p_hom = to_homogeneous(p, w=1.0)
    p_trans_hom = T_arr @ p_hom
    return p_trans_hom[:3]


def transform_direction(T, v) -> np.ndarray:
    """방향 변환 (w = 0): 회전만 적용되고 병진은 무시된다. 반환은 (3,)."""
    # TODO: 문제 5-2
    T_arr = np.asarray(T, dtype=float)
    v_arr = np.asarray(v, dtype=float)

    if T_arr.shape != (4, 4):
        raise ValueError("T는 4x4 행렬이어야 합니다.")
    if v_arr.shape != (3,):
        raise ValueError("v는 (3,) 크기의 방향 벡터여야 합니다.")

    # w = 0.0 전달
    v_hom = to_homogeneous(v_arr, w=0.0)
    v_trans_hom = T_arr @ v_hom

    return v_trans_hom[:3]


def transform_points(T, P, w: float = 1.0) -> np.ndarray:
    """(N,3) 점군을 **반복문 없이** 한 번에 변환한다. (3,) 입력도 받아야 한다.

    힌트: (T @ P_h.T).T 대신 P_h @ T.T 를 쓰면 전치가 한 번으로 끝나고
          메모리 접근도 행 방향이라 캐시에 유리하다.
    """
    # TODO: 문제 5-2 / 6-2
    T_arr = np.asarray(T, dtype=float)
    P_arr = np.asarray(P, dtype=float)

    # 1. T 형태 검사
    if T_arr.shape != (4, 4):
        raise ValueError("T는 4x4 행렬이어야 합니다.")

    # 2. 동차 좌표계 변환 (N, 4) 또는 (4,)
    P_h = to_homogeneous(P_arr, w=w)

    # 3. P_h @ T.T 연산
    P_trans_h = P_h @ T_arr.T

    # 4. (x, y, z) 성분만 슬라이싱하여 반환
    return P_trans_h[..., :3]


def least_squares_normal_equation(A, b):
    """정규방정식 (A^T A) x = A^T b 를 직접 세워 최소자승해를 구한다.

    - (A^T A) 의 역행렬은 문제 4 에서 만든 `inverse_gauss_jordan` 으로 구한다
      (`np.linalg.lstsq` 는 노트북에서 **비교 대상**으로만 쓴다).
    - 근거: 잔차 r = b - A x 가 최소일 때 r 은 A 의 열공간에 수직이므로 A^T r = 0.

    Returns
    -------
    x : 최소자승해
    residual : b - A x
    """
    # TODO: 문제 5-5
    A_arr = np.asarray(A, dtype=float)
    b_arr = np.asarray(b, dtype=float)
    if A_arr.ndim != 2 or b_arr.ndim not in (1, 2) or A_arr.shape[0] != b_arr.shape[0]:
        raise ValueError("A의 행 수와 b의 첫 번째 차원이 같아야 합니다.")

    # 1. A^T A 및 A^T b 연산
    ATA = A_arr.T @ A_arr
    ATb = A_arr.T @ b_arr

    # 2. 직점 구현했던 가우스-조던 역행렬 함수 사용
    ATA_inv = inverse_gauss_jordan(ATA)

    # 3. 해 x 및 잔차 residual 구하기
    x = ATA_inv @ ATb
    residual = b_arr - A_arr @ x

    return x, residual


def rmse(residual) -> float:
    """잔차의 RMSE = sqrt(mean(r^2))."""
    # TODO: 문제 5-5
    r = np.asarray(residual, dtype=float)
    return float(np.sqrt(np.mean(r ** 2)))
