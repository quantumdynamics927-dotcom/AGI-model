#!/usr/bin/env python
"""Sign promoter FASTA files and generate certificates.
Generates a one-time HMAC key, signs all .fa files in e:/AGI model/data/promoters,
creates .sha256 and .nft.json via stamper.stamp_file and renders certificates via certificate.generate_certificate.
The key is saved to e:/AGI model/data/promoters/hmac_key.txt - store it securely.
"""
import os
import binascii
from pathlib import Path
import importlib.util

# Generate key
key = binascii.hexlify(os.urandom(32)).decode()
print('GENERATED_HMAC_KEY:', key)

# Write key to file (user must store securely)
out_dir = Path(r'e:/AGI model/data/promoters')
out_dir.mkdir(parents=True, exist_ok=True)
key_file = out_dir / 'hmac_key.txt'
key_file.write_text(key)

# Import stamper
spec = importlib.util.spec_from_file_location('stamper','e:/AGI model/tmt-os-labs/tools/stamper.py')
stamper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stamper)

# Import certificate
spec2 = importlib.util.spec_from_file_location('certificate','e:/AGI model/tmt-os-labs/tools/certificate.py')
certificate = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(certificate)

results = []
for p in sorted(out_dir.glob('*.fa')):
    try:
        metrics = {'phi_score': 1.0, 'size': p.stat().st_size}
        meta = stamper.stamp_file(p, out_dir=out_dir, client_name='PromoterDelivery', physics_metrics=metrics, hmac_key=key)
        nft_path = Path(str(p) + '.nft.json')
        cert_path = certificate.generate_certificate(nft_path)
        results.append({'file': str(p), 'nft': str(nft_path), 'cert': str(cert_path)})
        print('[OK]', p.name, '->', nft_path.name, cert_path.name)
    except Exception as e:
        print('[ERR]', p.name, e)

print('\nSUMMARY:')
for r in results:
    print(r)

print('\nHMAC key saved to:', key_file)
print('Store this key securely to verify signatures later.')
