"""Pokémon Scarlet & Violet's builds (tools/gen.py), apart from Arceus's (tools/pla_patches.py),
Z-A's (tools/za_patches.py) and Link's Awakening's (tools/patches.py)."""
import struct

# main's build ID (first 16 hex digits) -> version
SV_BUILDS = {
    '709bfd6611529864': '3.0.1',  # Pokémon Violet v786432 (3.0.1)
}


def sv_patches(build):
    if build.lower() in SV_BUILDS:
        return {}
    return {}
