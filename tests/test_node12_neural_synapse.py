import os
import numpy as np
from node12_neural_synapse import build_connectivity, _phi_correlation


def test_phi_correlation():
    a = 'ATCGATCG'
    b = 'ATCGATCG'
    c = 'GGGGGGGG'
    assert _phi_correlation(a, b) > 0.9
    assert _phi_correlation(a, c) < 0.2


def test_build_connectivity_strengthening():
    seqs = {'n0': 'ATCGATCG', 'n1': 'ATCGATCG', 'n2': 'GGGGGGGG'}
    mat, meta = build_connectivity(seqs, phi_threshold=0.9, strengthen=0.5)
    # n0-n1 should be stronger than n0-n2
    n0n1 = mat[0,1]
    n0n2 = mat[0,2]
    assert n0n1 > n0n2
    assert meta['shape'] == mat.shape
