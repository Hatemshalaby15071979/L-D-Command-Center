"""Desktop shell package."""

# Single source of truth for the product version. The git tag `v1.0.0` and the
# top CHANGELOG entry must agree with this. Release tags in CI are date-stamped
# (v2026MMDD-HHMMSS) per the desktop-app cadence; this constant is the semver
# anchor consumers should read.
__version__ = "1.0.0"
