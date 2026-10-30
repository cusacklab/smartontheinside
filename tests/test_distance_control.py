"""Distance controls: geometry, the distance-only model, and the regression."""

import numpy as np
import pandas as pd
import pytest

from sti.config import Config
from sti.datasets import Activation, Connectivity
from sti.distance_control import (distance_features_from_geometry,
                                  distance_only_results, geodesic_to_sources,
                                  mesh_graph, positional_share, regress_distance)


def lattice_mesh(nx=12, ny=12, z=0.0):
    """A flat triangulated lattice with unit spacing."""
    xs, ys = np.meshgrid(np.arange(nx), np.arange(ny))
    coords = np.column_stack([xs.ravel(), ys.ravel(), np.full(nx * ny, z)]).astype(float)
    tris = []
    for r in range(ny - 1):
        for c in range(nx - 1):
            v = r * nx + c
            tris += [(v, v + 1, v + nx), (v + 1, v + nx + 1, v + nx)]
    return coords, np.array(tris)


def test_mesh_graph_does_not_double_shared_edges():
    coords, tris = lattice_mesh(3, 3)
    g = mesh_graph(coords, tris)
    # the central horizontal edge (vertex 3 -> 4) is shared by two triangles
    # and must keep its unit length, not a summed one
    assert g[3, 4] == pytest.approx(1.0)
    assert g[4, 3] == pytest.approx(1.0)


def test_geodesic_matches_known_path_lengths():
    coords, tris = lattice_mesh(10, 2)  # a strip: geodesics are along the rows
    g = mesh_graph(coords, tris)
    d = geodesic_to_sources(g, np.array([0]))
    assert d[9] == pytest.approx(9.0)  # straight along the bottom row
    assert d[10] == pytest.approx(1.0)  # one step up


def test_distance_features_layout():
    coords, tris = lattice_mesh(12, 12)
    seeds = np.arange(5)
    ipsi = {10: np.array([100, 101]), 5: np.array([80])}       # labels 10, 5
    contra_coords = coords + np.array([50.0, 0.0, 0.0])
    contra = {200: np.array([0, 1]), 7: np.array([143])}       # 7 is "DLPFC"
    out = distance_features_from_geometry(
        seeds, coords, tris, ipsi, contra_coords, contra,
        n_parcels=360, exclude=(7,))
    assert out.shape == (5, 360)
    assert (out[:, 6] == 0).all()                  # excluded label 7 stays zero
    assert (out[:, 9] > 0).all() and (out[:, 4] > 0).all()
    # contralateral: pure Euclidean to the shifted lattice
    expect = np.linalg.norm(coords[seeds] - contra_coords[0], axis=1)
    alt = np.linalg.norm(coords[seeds] - contra_coords[1], axis=1)
    assert np.allclose(out[:, 199], np.minimum(expect, alt))
    untouched = np.ones(360, bool)
    untouched[[9, 4, 199]] = False
    assert (out[:, untouched] == 0).all()


def test_disconnected_mesh_is_an_error():
    coords, tris = lattice_mesh(4, 2)
    # three extra vertices with no triangles: a seed there is unreachable
    coords2 = np.vstack([coords, coords[:3] + 100.0])
    with pytest.raises(ValueError, match="disconnected"):
        distance_features_from_geometry(
            np.array([0, len(coords)]), coords2, tris, {1: np.array([0])},
            coords2, {}, n_parcels=4, exclude=())


# --------------------------------------------------------------------------- #


def _activation(target, n_sub, rng, task="tfMRI_SYNTH"):
    maps = target[None] + 0.3 * target.std() * rng.normal(size=(n_sub, target.size))
    return Activation(data={"L": maps}, task=task, cohort="synthetic")


def test_distance_only_model_recovers_a_positional_map():
    """A map that IS a function of distance should be predicted almost perfectly."""
    rng = np.random.default_rng(0)
    n_vert = 150
    d = np.abs(rng.normal(size=(n_vert, 20))) + 1.0
    dists = {"L": np.pad(d, ((0, 0), (0, 340)))}  # mirror the zero padding
    target = d @ rng.normal(size=20)
    acts = {"tfMRI_SYNTH": _activation(target, 8, rng)}
    res = distance_only_results(dists, acts, config=Config(alpha=0.0),
                                hemispheres=("L",))
    r = res[(res.task == "tfMRI_SYNTH") & (res.comparison_task == "tfMRI_SYNTH")]
    assert r.pearson.iloc[0] > 0.95
    assert (res.protocol == "distance_only").all()
    assert (res.subject == "geometry").all()


def test_positional_share_table():
    rng = np.random.default_rng(1)
    dist_res = pd.DataFrame([{"task": "tfMRI_SYNTH", "hemi": "L",
                              "comparison_task": "tfMRI_SYNTH", "pearson": 0.2}])
    obs = pd.DataFrame([{"task": "tfMRI_SYNTH", "hemi": "L",
                         "comparison_task": "tfMRI_SYNTH", "pearson": 0.4}])
    share = positional_share(dist_res, obs)
    assert share.excess_r.iloc[0] == pytest.approx(0.2)
    assert share.pct_positional.iloc[0] == pytest.approx(50.0)


def test_regress_distance_removes_decay_and_keeps_structure():
    rng = np.random.default_rng(2)
    n_sub, n_vert, n_feat = 4, 120, 30
    d = np.abs(rng.normal(size=(n_vert, n_feat))).astype(np.float32) * 10 + 1
    structure = rng.normal(size=(n_vert, n_feat)).astype(np.float32)
    # counts: exponential decay with distance, modulated by real structure
    lam = 5.0
    c = np.exp(-d / lam) * 2000 * np.exp(0.5 * structure)
    X = np.stack([c * np.exp(0.05 * rng.normal(size=c.shape)) for _ in range(n_sub)])
    conn = Connectivity(data={"L": X}, cohort="synthetic")

    res = regress_distance(conn, {"L": d})
    assert res.cohort.endswith("distance_regressed")
    for s in range(n_sub):
        assert res["L"][s].std() == pytest.approx(1.0, rel=1e-3)  # unit scale
        raw_r = np.corrcoef(np.log1p(X[s]).ravel(), d.ravel())[0, 1]
        res_r = np.corrcoef(res["L"][s].ravel(), d.ravel())[0, 1]
        assert abs(res_r) < 0.05 < abs(raw_r)
        kept = np.corrcoef(res["L"][s].ravel(), structure.ravel())[0, 1]
        assert kept > 0.5

    # zero-padded columns stay zero
    Xp = np.concatenate([X, np.zeros((n_sub, n_vert, 2), np.float32)], axis=2)
    dp = np.concatenate([d, np.zeros((n_vert, 2), np.float32)], axis=1)
    resp = regress_distance(Connectivity(data={"L": Xp}, cohort="s"), {"L": dp})
    assert (resp["L"][:, :, -2:] == 0).all()
