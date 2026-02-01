import os

# Compatibility shim: make `import tmt_os_labs.tools.*` resolve to the existing
# `tmt-os-labs/tools` directory (hyphens are not valid in module names).
# This keeps the repository layout intact while allowing tests to import
# using the underscore form (`tmt_os_labs`).

_this_dir = os.path.dirname(__file__)
_alt = os.path.abspath(os.path.join(_this_dir, '..', 'tmt-os-labs'))
if os.path.isdir(_alt):
    # Prepend to __path__ so Python will search the sibling folder for subpackages
    __path__.insert(0, _alt)

# Expose a simple version
__version__ = "0.1.0"
