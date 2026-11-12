// Which game a set of game files is, from its exefs/main build ID (the NSO header's first 8 bytes at 0x40), and
// whether PokeV-Recomp runs it. Header-only (C and C++: runtime/ui/launcher.mm, runtime/main.c, tools/test_game_identity.c).
//
// Only Pokémon Violet 3.0.1 is accepted (tools/sv_patches.py SV_BUILDS). The other builds below are the ones this
// runtime's ancestors (LAS Recomp, ZA Recomp, PokeL-ARecomp) set up: they are *recognised*, never accepted, so the
// start screen can say "these are Pokémon Legends: Arceus's files" instead of offering to compile them. Before
// v0.0.25 the start screen accepted all of them, and on Linux its data folder was PokeL-ARecomp's
// (~/.local/share/plarecomp): Arceus's extracted/ there passed as "set up, needs a rebuild" (issue #1).
#pragma once
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

typedef struct {
    uint8_t id[8];
    const char *game;     // for messages: "Pokémon Legends: Arceus"
    const char *version;  // "1.1.1"
    bool supported;       // PokeV-Recomp sets it up and compiles it
} GameIdentity;

static const GameIdentity GAME_IDENTITIES[] = {
    // Pokémon Violet 3.0.1 (update v786432; title 01008F6008C5E000): the one game PokeV-Recomp runs
    {{0x70, 0x9b, 0xfd, 0x66, 0x11, 0x52, 0x98, 0x64}, "Pok\xc3\xa9mon Violet", "3.0.1", true},
    // recognised only (refused, with their name)
    {{0xae, 0xe8, 0xf1, 0x50, 0xdd, 0xa1, 0xb5, 0xa8}, "Pok\xc3\xa9mon Legends: Arceus", "1.1.1", false},
    {{0x72, 0x22, 0xe1, 0x3e, 0xcf, 0x6a, 0xdb, 0x32}, "Pok\xc3\xa9mon Legends: Z-A", "1.0.0", false},
    {{0x8a, 0x1c, 0x86, 0xc4, 0x37, 0x39, 0x4b, 0x69}, "Pok\xc3\xa9mon Legends: Z-A", "2.0.0", false},
    {{0xb1, 0xf1, 0x2f, 0xd9, 0x19, 0xea, 0xe8, 0x6a}, "Pok\xc3\xa9mon Legends: Z-A", "2.0.2", false},
    {{0xae, 0x16, 0xf7, 0x1e, 0x00, 0x2a, 0xf8, 0xcb}, "The Legend of Zelda: Link's Awakening", "1.0.0", false},
};

// The known build an ID is (supported or not); NULL = unknown
static inline const GameIdentity *game_identity_find(const uint8_t id[8]) {
    for (size_t i = 0; i < sizeof GAME_IDENTITIES / sizeof *GAME_IDENTITIES; i++)
        if (!memcmp(id, GAME_IDENTITIES[i].id, 8)) return &GAME_IDENTITIES[i];
    return NULL;
}

// The version string of a build PokeV-Recomp runs; NULL = anything else (another game, another version, unknown)
static inline const char *game_identity_supported(const uint8_t id[8]) {
    const GameIdentity *g = game_identity_find(id);
    return g && g->supported ? g->version : NULL;
}

// The build ID of a main module (false: no such file, or too short to be one)
static inline bool game_identity_read(const char *main_path, uint8_t id[8]) {
    FILE *f = fopen(main_path, "rb");
    if (!f) return false;
    memset(id, 0, 8);
    bool ok = fseek(f, 0x40, SEEK_SET) == 0 && fread(id, 1, 8, f) == 8;
    fclose(f);
    return ok;
}

// What a refused build is, for the start screen: "Pokémon Legends: Arceus 1.1.1" or "an unknown build (aee8f150...)"
static inline void game_identity_describe(const uint8_t id[8], char *out, size_t n) {
    const GameIdentity *g = game_identity_find(id);
    if (g) snprintf(out, n, "%s %s", g->game, g->version);
    else snprintf(out, n, "an unknown build (%02x%02x%02x%02x%02x%02x%02x%02x)", id[0], id[1], id[2], id[3], id[4],
                  id[5], id[6], id[7]);
}
