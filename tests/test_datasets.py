import numpy as np
import pytest

from sti.datasets import (Activation, Connectivity, MissingDataError, adult_activation_key,
                          adult_connectivity_key, load_connectivity, neonatal_connectivity_key)
from sti.config import N_SEED_VERTICES


def test_s3_key_conventions():
    assert adult_connectivity_key(155) == "Results/conn_for_classifier_N-155.npy"
    assert neonatal_connectivity_key(183) == \
        "infant_classifier/conn_for_classifier_N-183_infants.npy"
    assert adult_activation_key("tfMRI_WM", 155) == \
        "Results/act_for_classifier_tfMRI_WM_N-155.npy"


def test_connectivity_validation_catches_wrong_vertex_count():
    bad = Connectivity({"L": np.zeros((3, 999, 334))}, "bad")
    with pytest.raises(ValueError, match="seed vertices"):
        bad.validate()


def test_connectivity_validation_catches_wrong_dimensionality():
    with pytest.raises(ValueError, match="3D"):
        Connectivity({"L": np.zeros((3, 334))}, "bad").validate()


def test_activation_zscore_is_per_subject_across_vertices():
    rng = np.random.default_rng(0)
    a = Activation({"L": rng.normal(5, 3, (4, N_SEED_VERTICES["L"]))}, "t", "c")
    z = a.zscored()["L"]
    assert np.allclose(z.mean(axis=1), 0, atol=1e-10)
    assert np.allclose(z.std(axis=1), 1, atol=1e-10)


def test_missing_local_data_without_download_is_explicit(tmp_path, monkeypatch):
    monkeypatch.setenv("STI_DATA_DIR", str(tmp_path))
    with pytest.raises(MissingDataError, match="downloads are disabled"):
        load_connectivity(155, allow_download=False)


def test_tractography_key_conventions():
    from sti.datasets import adult_tractography_key, neonatal_tractography_key

    assert neonatal_tractography_key("CC00060XX03", "L") == \
        "Results/sub-CC00060XX03_infants_tractography_results_VOXEL_L.npy"
    # a bare or prefixed ID must give the same key
    assert neonatal_tractography_key("sub-CC00060XX03", "R") == \
        neonatal_tractography_key("CC00060XX03", "R")
    assert adult_tractography_key("103818", "L") == \
        "Results/103818_tractography_results_VOXEL_L.npy"


def test_build_connectivity_rejects_wrong_vertex_count(tmp_path, monkeypatch):
    """A per-subject file with the wrong seed count must not be silently accepted."""
    from sti import datasets

    bad = tmp_path / "bad.npy"
    np.save(bad, np.zeros((361, 99)))
    monkeypatch.setattr(datasets.s3io, "fetch", lambda *a, **k: bad)
    with pytest.raises(ValueError, match="seed vertices"):
        datasets.build_connectivity(["CC1"], "L", keep_cache=True, progress=False)


def test_build_connectivity_rejects_too_few_parcel_rows(tmp_path, monkeypatch):
    from sti import datasets
    from sti.config import N_SEED_VERTICES

    bad = tmp_path / "short.npy"
    np.save(bad, np.zeros((100, N_SEED_VERTICES["L"])))
    monkeypatch.setattr(datasets.s3io, "fetch", lambda *a, **k: bad)
    with pytest.raises(ValueError, match="rows"):
        datasets.build_connectivity(["CC1"], "L", keep_cache=True, progress=False)


def test_build_connectivity_transposes_parcels_to_the_last_axis(tmp_path, monkeypatch):
    """Rows 1..360 of the stored file become the target axis; row 0 is dropped."""
    from sti import datasets
    from sti.config import N_PARCELS, N_SEED_VERTICES

    nv = N_SEED_VERTICES["L"]
    arr = np.zeros((N_PARCELS + 1, nv))
    arr[0] = 999.0                      # unused row, must not appear in the output
    arr[7] = 5.0                        # parcel 7 -> column 6
    f = tmp_path / "one.npy"
    np.save(f, arr)
    monkeypatch.setattr(datasets.s3io, "fetch", lambda *a, **k: f)
    X = datasets.build_connectivity(["CC1"], "L", keep_cache=True, progress=False)
    assert X.shape == (1, nv, N_PARCELS)
    assert np.allclose(X[0, :, 6], 5.0)
    assert 999.0 not in X


def _write_conn(path, n, nv_l=None, nv_r=None):
    from sti.config import N_PARCELS, N_SEED_VERTICES
    d = {"L": np.zeros((n, nv_l or N_SEED_VERTICES["L"], N_PARCELS), np.float32),
         "R": np.zeros((n, nv_r or N_SEED_VERTICES["R"], N_PARCELS), np.float32)}
    np.save(path, d, allow_pickle=True)


def test_load_connectivity_file_reads_the_subject_sidecar(tmp_path):
    from sti.datasets import load_connectivity_file

    p = tmp_path / "conn.npy"
    _write_conn(p, 3)
    p.with_suffix(".subjects.txt").write_text("CC1\nCC2\nCC3\n")
    conn, subs = load_connectivity_file(p)
    assert conn.n_subjects == 3 and subs == ["CC1", "CC2", "CC3"]


def test_sidecar_disagreeing_with_the_array_is_an_error(tmp_path):
    """A 326-subject cohort against a 325-row array would mislabel every row."""
    from sti.datasets import load_connectivity_file

    p = tmp_path / "conn.npy"
    _write_conn(p, 3)
    p.with_suffix(".subjects.txt").write_text("CC1\nCC2\n")
    with pytest.raises(ValueError, match="lists 2 subjects but"):
        load_connectivity_file(p)


def test_load_connectivity_file_without_sidecar_returns_none(tmp_path):
    from sti.datasets import load_connectivity_file

    p = tmp_path / "conn.npy"
    _write_conn(p, 2)
    conn, subs = load_connectivity_file(p)
    assert conn.n_subjects == 2 and subs is None


def test_missing_connectivity_file_is_explicit(tmp_path):
    from sti.datasets import load_connectivity_file

    with pytest.raises(MissingDataError, match="not found"):
        load_connectivity_file(tmp_path / "nope.npy")
