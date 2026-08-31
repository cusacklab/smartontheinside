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
