"""Pokémon Scarlet & Violet's builds (tools/gen.py), apart from Arceus's (tools/pla_patches.py),
Z-A's (tools/za_patches.py) and Link's Awakening's (tools/patches.py)."""
import struct

# main's build ID (first 16 hex digits) -> version
SV_BUILDS = {
    '709bfd6611529864': '3.0.1',  # Pokémon Violet v786432 (3.0.1)
}


def _sv_frame_clock(gen, a):
    # 0x7002b7a784: ldr d0, [x0, #8]
    # Master frame clock in f_7002b79f68: loads nanosecond duration of slot 0.
    # The value is converted to double (scvtf d0, d0), divided by 1e9 (fdiv d0, d0, d1) and float s0
    # is passed to f_7000c9cdfc to advance the game simulation.
    # Returning real wall-clock delta-time (16.67ms at 60 FPS) eliminates 2x speed-up and prevents slow-motion!
    #
    # The rest of the game steps by the clock manager's slots, not by this value: each frame (0x7002b7a8f4..) the
    # manager's SetSlotMode(slot, mode) (0x7002b7b308) copies the mode's duration from the table at 0x7003c2fba8
    # (16.67 / 33.3 / 50 / 66.7 / 83.3 ms) into slot i (manager + 8 + 16 i, duration at +8: GetSlot 0x7002b7b2fc), and
    # systems read slot 1 directly or as a speed factor, slot 1 / (table[mode] - 1) (0x7000b83d1c, 0x7000d96428). With
    # the 60 fps mode forced, the slots held 16.67 ms however long the frame took: below 60 fps the world, animations
    # and the character's walk moved in slow motion (~38 fps looked like 15-20; 30 fps ran smooth). x0 here is slot 0
    # (GetSlot(0)), and the simulation step (bl 0x7000c9cdfc) comes before SetSlotMode, so the real frame time written
    # into slots 0 and 1 now is what this frame's update reads; the table keeps its nominal 16.67 ms, so the factor
    # readers get real / nominal. Both slot classes seen have 2+ slots (GetSlotCount: 2, 7). rt_sv_slot_dt(): off with
    # LARECOMP_SV_SLOT_DT=0.
    w = struct.unpack_from('<I', gen.nso.image, a - gen.base)[0]
    assert w == 0xfd400400, hex(w)  # ldr d0, [x0, #8]
    return ('{ extern uint64_t rt_pla_frame_dt_ns(uint32_t slot, uint64_t default_ns); extern _Bool rt_sv_slot_dt(void); '
            'uint64_t orig_ns = c->x[0] ? LD64(c->x[0] + 8) : 0x01fca056ull; '
            'uint64_t dt_ns = rt_pla_frame_dt_ns(0, orig_ns); '
            'if (c->x[0] && dt_ns != orig_ns && rt_sv_slot_dt()) { ST64(c->x[0] + 8, dt_ns); ST64(c->x[0] + 0x18, dt_ns); } '
            'c->v[0] = dt_ns; }'
            f'  /* {a:#x}: SV 3.0.1 dynamic frame clock delta-time (ns), into clock slots 0 and 1 */')


def _sv_slot_mode(gen, a):
    # SetSlotMode(slot, mode)'s table load, ldr x2, [x8, w2, sxtw #3] (x8: the duration table at 0x7003c2fba8): the
    # duration it hands SetSlotDuration for the slot. As Arceus's _pla_frame_dt_step (pla_patches.py, 0x7002783050 -
    # the same instruction; Arceus plays smooth at 45-50 fps): the 60 fps mode's 16.67 ms becomes the real frame time,
    # for every slot of every clock manager. Unlike Arceus it doesn't measure (the frame clock patch above already does,
    # once a frame: a second measuring call would see a few microseconds and drag the average down) - it takes the
    # frame time measured this frame (rt_sv_slot_duration). Three implementations call it: 0x7002b7b308 and
    # 0x7002b7b334 (two slots) and 0x700092dd20 (seven).
    w = struct.unpack_from('<I', gen.nso.image, a - gen.base)[0]
    assert w == 0xf862d902, hex(w)  # ldr x2, [x8, w2, sxtw #3]
    return ('{ extern uint64_t rt_sv_slot_duration(uint64_t table_ns); '
            'c->x[2] = rt_sv_slot_duration(LD64(c->x[8] + ((int64_t)(int32_t)c->x[2] << 3))); }'
            f'  /* {a:#x}: SV 3.0.1 clock slot duration: the real frame time in the 60 fps mode */')


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
            0x7002b7a784: _sv_frame_clock,
            0x7002b7a858: _sv_frame_pace,
            0x7002b7b310: _sv_slot_mode,
            0x7002b7b33c: _sv_slot_mode,
            0x700092dd28: _sv_slot_mode,
        }
    return {}
