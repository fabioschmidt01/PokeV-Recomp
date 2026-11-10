"""Pokémon Scarlet & Violet's builds (tools/gen.py), apart from Arceus's (tools/pla_patches.py),
Z-A's (tools/za_patches.py) and Link's Awakening's (tools/patches.py)."""
import struct

# main's build ID (first 16 hex digits) -> version
SV_BUILDS = {
    '709bfd6611529864': '3.0.1',  # Pokémon Violet v786432 (3.0.1)
}


def _sv_frame_pace(gen, a):
    # 0x7002b7a858: ldrsb w20, [x10, #0x20]
    # In Pokémon Scarlet & Violet 3.0.1, [x10 + 0x20] is the game's target frame mode (1 for 30 FPS, 0 for 60 FPS).
    # Setting w20 = 0 when 60fps is enabled causes:
    # 1. Present interval at 0x7002b7a874 (w20 + 1) to become 1 (60 FPS vsync presentation).
    # 2. Clock slots 0..3 to be set to mode 0 (16.666667 ms = 1/60s), eliminating 2x fast-forward speed-up!
    # We also keep entry 1 in the duration table (0x7003c2fbb0) synced to 16.67ms at 60fps.
    w = struct.unpack_from('<I', gen.nso.image, a - gen.base)[0]
    assert w == 0x39c08154, hex(w)  # ldrsb w20, [x10, #0x20]
    return ('{ extern _Bool rt_pla_is_60fps(void); '
            '_Bool fps60 = rt_pla_is_60fps(); '
            'int8_t orig_mode = c->x[10] ? *(int8_t *)(c->x[10] + 0x20) : 1; '
            'c->x[20] = fps60 ? 0 : orig_mode; '
            '*(uint64_t *)0x7003c2fbb0ull = fps60 ? 0x00fe502bull : 0x01fca056ull; }'
            f'  /* {a:#x}: SV 3.0.1 60fps frame mode and delta-time */')


def sv_patches(build):
    if build.lower() in SV_BUILDS:
        return {
            0x7002b7a858: _sv_frame_pace,
        }
    return {}

