import itertools
import numpy as np

PAULIS = {
    'I': np.array([[1, 0], [0, 1]], dtype=complex),
    'X': np.array([[0, 1], [1, 0]], dtype=complex),
    'Y': np.array([[0, -1j], [1j, 0]], dtype=complex),
    'Z': np.array([[1, 0], [0, -1]], dtype=complex),
}


def kron3(a, b, c):
    return np.kron(np.kron(a, b), c)


def hamiltonian_to_pauli_decomposition(H, tol=1e-12):
    """Decompose a 8x8 Hamiltonian matrix into Pauli basis.

    Returns list of (pauli_string, coeff) where pauli_string is e.g. 'XZI'.
    Coeffs are computed as (1/2^n) * Tr(P H) with n=3.
    """
    H = np.asarray(H, dtype=complex)
    if H.shape != (8, 8):
        raise ValueError('Expected 8x8 Hamiltonian')
    terms = []
    n = 3
    scale = 1.0 / (2 ** n)
    for ops in itertools.product('IXYZ', repeat=3):
        pstr = ''.join(ops)
        P = kron3(PAULIS[ops[0]], PAULIS[ops[1]], PAULIS[ops[2]])
        coeff = scale * np.trace(P.dot(H))
        coeff = complex(coeff)
        if abs(coeff.real) > tol or abs(coeff.imag) > tol:
            # drop near-zero imaginary part if negligible
            if abs(coeff.imag) < tol:
                coeff = float(coeff.real)
            else:
                coeff = complex(coeff)
            terms.append((pstr, coeff))
    # sort by magnitude descending for readability
    terms.sort(key=lambda t: abs(t[1]), reverse=True)
    return terms


if __name__ == '__main__':
    # tiny self-test
    I = PAULIS['I']
    Z = PAULIS['Z']
    H = kron3(Z, Z, I) + 0.2 * (kron3(PAULIS['X'], I, I) + kron3(I, PAULIS['X'], I) + kron3(I, I, PAULIS['X']))
    terms = hamiltonian_to_pauli_decomposition(H)
    for p, c in terms[:10]:
        print(p, c)
