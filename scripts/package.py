"""Build a reproducible ZIP from an explicit runtime-file allowlist."""
import hashlib
import zipfile
from validate import ROOT, FILES, validate

def build(root=ROOT):
    validate(root)
    out = root / 'dist'
    out.mkdir(exist_ok=True)
    target = out / 'billr.zip'
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(FILES):
            entry = zipfile.ZipInfo(name, (2026, 1, 1, 0, 0, 0))
            entry.external_attr = 0o100644 << 16
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, (root / name).read_bytes())
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        assert sorted(archive.namelist()) == sorted(FILES)
    return target

if __name__ == '__main__':
    target = build()
    print(f'{target.name} SHA256 {hashlib.sha256(target.read_bytes()).hexdigest()}')
