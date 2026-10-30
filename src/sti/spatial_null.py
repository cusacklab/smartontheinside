"""Spatial null models for prediction accuracy (manuscript Fig. S8).

The question is whether a model's prediction correlates with the observed
activation map only because both are spatially smooth. The null must therefore
preserve the spatial autocorrelation of the observed map while destroying its
correspondence with the prediction.

Why not a spin test
-------------------
The classic spin test (Alexander-Bloch et al., 2018) rotates a map on the
spherical surface. Here the data live on a DLPFC patch of ~2200 vertices, not the
whole cortex, so most rotations send vertices outside the mask and there is no
value to put in their place -- the boundary problem the manuscript flags as
outstanding. Instead this module uses variogram-matched surrogate maps
(Burt et al., 2020, "BrainSMASH"), which are generated *within* the mask and so
need no rotation at all. Every surrogate has, by construction, the same spatial
autocorrelation structure as the observed map.

The model is not refitted: the prediction is held fixed and only the target map is
resampled, so a null of 1,000 surrogates costs a few seconds rather than 1,000
refits.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
from scipy.stats import binned_statistic, pearsonr

log = logging.getLogger(__name__)


def empirical_variogram(
    x: np.ndarray, dist: np.ndarray, *, n_bins: int = 25, max_distance: float | None = None
) -> tuple[np.ndarray, np.ndarray]:
    """Empirical semivariogram of ``x`` over the pairwise distances ``dist``.

    Returns ``(bin_centres, gamma)`` where
    ``gamma(h) = 0.5 * mean((x_i - x_j)^2)`` over vertex pairs separated by ``h``.
    """
    x = np.asarray(x, dtype=float).reshape(-1)
    iu = np.triu_indices(dist.shape[0], k=1)
    d = dist[iu]
    if max_distance is None:
        max_distance = np.percentile(d, 75)
    keep = d <= max_distance
    d = d[keep]
    sq = 0.5 * (x[iu[0]][keep] - x[iu[1]][keep]) ** 2
    gamma, edges, _ = binned_statistic(d, sq, statistic="mean", bins=n_bins)
    centres = 0.5 * (edges[:-1] + edges[1:])
    ok = np.isfinite(gamma)
    return centres[ok], gamma[ok]


@dataclass
class SurrogateMaps:
    """Generator of variogram-matched surrogate maps for one hemisphere.

    Two things make a large null affordable. Smoothing kernels are precomputed
    once and reused across every surrogate; and the variogram used for fitting is
    estimated from a fixed random subsample of vertex pairs (``n_pairs``) with
    precomputed bin assignments, so each evaluation is a ``bincount`` rather than
    a pass over all ~2.4 million pairs.
    """

    dist: np.ndarray
    n_widths: int = 6
    n_bins: int = 25
    knn: int | None = 1000
    n_pairs: int = 200_000
    max_distance_pct: float = 50.0
    seed: int = 0

    def __post_init__(self) -> None:
        d = np.asarray(self.dist, dtype=np.float32)
        n = d.shape[0]
        if d.shape != (n, n):
            raise ValueError(f"dist must be square, got {d.shape}")
        self._n = n
        self._rng = np.random.default_rng(self.seed)

        # --- fixed subsample of vertex pairs, binned once ---
        rng = np.random.default_rng(self.seed + 1)
        i = rng.integers(0, n, size=self.n_pairs)
        j = rng.integers(0, n, size=self.n_pairs)
        keep = i != j
        i, j = i[keep], j[keep]
        dp = d[i, j]
        self._max_distance = float(np.percentile(dp, self.max_distance_pct))
        keep = dp <= self._max_distance
        self._pi, self._pj, dp = i[keep], j[keep], dp[keep]

        edges = np.linspace(0.0, self._max_distance, self.n_bins + 1)
        self._bin = np.clip(np.digitize(dp, edges) - 1, 0, self.n_bins - 1)
        counts = np.bincount(self._bin, minlength=self.n_bins)
        self._valid = counts > 0
        self._counts = counts[self._valid]
        self._centres = (0.5 * (edges[:-1] + edges[1:]))[self._valid]

        # --- row-normalised exponential smoothing kernels, one per width ---
        finite = dp
        widths = np.linspace(np.percentile(finite, 5), np.percentile(finite, 70), self.n_widths)
        self._kernels = []
        for w in widths:
            k = np.exp(-d / np.float32(w))
            if self.knn is not None and self.knn < n:
                # keep only the knn nearest neighbours per row; the far tail
                # costs the most and contributes almost nothing
                cutoff = np.partition(d, self.knn, axis=1)[:, self.knn][:, None]
                k = np.where(d <= cutoff, k, np.float32(0.0))
            k /= k.sum(axis=1, keepdims=True)
            self._kernels.append(k)
        self._widths = widths

    @property
    def bin_centres(self) -> np.ndarray:
        """Distance bin centres used for variogram fitting."""
        return self._centres

    def fast_variogram(self, x: np.ndarray) -> np.ndarray:
        """Semivariogram of ``x`` over the precomputed pair subsample."""
        x = np.asarray(x, dtype=float).reshape(-1)
        diff = 0.5 * (x[self._pi] - x[self._pj]) ** 2
        total = np.bincount(self._bin, weights=diff, minlength=self.n_bins)
        return total[self._valid] / self._counts

    def _fit_one(self, x: np.ndarray, target_gamma: np.ndarray) -> np.ndarray:
        """Generate one surrogate matched to the variogram of ``x``."""
        perm = self._rng.permutation(x)
        best = None
        for kernel in self._kernels:
            smooth = kernel @ perm
            gamma = self.fast_variogram(smooth)
            # target_gamma ~= beta * gamma + alpha   (alpha is the nugget)
            A = np.column_stack([gamma, np.ones_like(gamma)])
            coef, *_ = np.linalg.lstsq(A, target_gamma, rcond=None)
            resid = float(np.sum((A @ coef - target_gamma) ** 2))
            if best is None or resid < best[0]:
                best = (resid, smooth, max(float(coef[0]), 0.0), max(float(coef[1]), 0.0))

        _, smooth, beta, alpha = best
        return np.sqrt(beta) * smooth + np.sqrt(alpha) * self._rng.normal(size=self._n)

    def generate(self, x: np.ndarray, n: int, *, resample: bool = True) -> np.ndarray:
        """Return ``(n, n_vertices)`` surrogate maps matched to ``x``.

        With ``resample=True`` the surrogate values are rank-matched back onto the
        observed values, so each surrogate is an exact permutation of ``x`` and
        has an identical marginal distribution -- only the spatial arrangement
        differs.
        """
        x = np.asarray(x, dtype=float).reshape(-1)
        if x.size != self._n:
            raise ValueError(f"x has {x.size} vertices, distance matrix has {self._n}")
        target_gamma = self.fast_variogram(x)
        sorted_x = np.sort(x)

        out = np.empty((n, self._n))
        for i in range(n):
            s = self._fit_one(x, target_gamma)
            if resample:
                s = sorted_x[np.argsort(np.argsort(s))]
            out[i] = s
        return out


def null_correlations(
    prediction: np.ndarray, observed: np.ndarray, surrogates: np.ndarray
) -> np.ndarray:
    """Correlation of a fixed prediction against each surrogate of the observed map."""
    prediction = np.asarray(prediction).reshape(-1)
    return np.array([pearsonr(prediction, s)[0] for s in surrogates])


def p_spin(observed_r: float, null_r: np.ndarray, *, tail: str = "greater") -> float:
    """p-value of an observed correlation against a spatial null.

    Uses the ``(k + 1) / (n + 1)`` estimator, which never returns exactly zero --
    a null of 1,000 surrogates cannot support a claim stronger than p < 0.001.
    """
    null_r = np.asarray(null_r)
    n = null_r.size
    if tail == "greater":
        k = int(np.sum(null_r >= observed_r))
    elif tail == "less":
        k = int(np.sum(null_r <= observed_r))
    elif tail == "two-sided":
        k = int(np.sum(np.abs(null_r) >= abs(observed_r)))
    else:
        raise ValueError(f"unknown tail {tail!r}")
    return (k + 1) / (n + 1)


def correlation_matrix(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Pearson correlation between every row of ``A`` and every row of ``B``.

    Returns ``(len(A), len(B))``. Vectorised because the null needs
    ``n_neonates x n_surrogates`` correlations per task and hemisphere -- 325,000
    for a 1,000-surrogate null, which is impractical one ``pearsonr`` at a time.
    """
    def _z(M):
        M = np.asarray(M, dtype=np.float64)
        M = M - M.mean(axis=1, keepdims=True)
        norms = np.linalg.norm(M, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return M / norms

    return _z(A) @ _z(B).T


def group_null_distribution(
    predictions: np.ndarray, surrogates: np.ndarray
) -> np.ndarray:
    """Null distribution of the *group-mean* prediction accuracy.

    ``predictions`` is ``(n_subjects, n_vertices)`` -- each subject's predicted
    map, held fixed. For each surrogate of the observed target map, every
    subject's prediction is correlated against it and the correlations averaged,
    giving one null value per surrogate. This matches the observed statistic,
    which is the mean within-task correlation across subjects.
    """
    return correlation_matrix(predictions, surrogates).mean(axis=0)
