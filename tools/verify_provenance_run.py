from pathlib import Path
from metatron_nervous_system import MetatronNervousSystem


def main():
    registry = Path('cache/prov_test')
    m = MetatronNervousSystem(registry)
    tmp = Path('cache')
    tmp.mkdir(parents=True, exist_ok=True)
    testf = tmp / 'prov_test_file.txt'
    testf.write_text('probe')
    hmac_key = 'test-key-123'
    packet = m.create_packet(testf, client='unit-test', hmac_key=hmac_key)
    print('packet hmac:', packet.get('hmac_signature'))
    ok = m.verify_packet_signature(packet, hmac_key)
    print('verification OK:', ok)


if __name__ == '__main__':
    main()
