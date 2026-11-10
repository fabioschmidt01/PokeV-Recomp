// The SDK's C library routines (memcpy, memset, memcmp, strlen, ...) on the host's: the recompiled versions are the
// SDK's byte loops lifted to C, and they were ~3% of the game's CPU time (memcmp alone ~1.5% of the presenting
// thread in a busy overworld scene). tools/gen.py replaces each function listed in hle_symbols.txt with a call to
// hle_<name>. Guest pointers are host addresses. The comparisons return the difference of the first unequal bytes,
// as the SDK's do (not just the sign).
#include <stdint.h>
#include <string.h>

#include "../hle.h"

#define P(r) ((void *)(uintptr_t)c->x[r])
#define CP(r) ((const uint8_t *)(uintptr_t)c->x[r])

static int64_t byte_diff(const uint8_t *a, const uint8_t *b) {  // (a and b differ somewhere ahead)
    while (*a == *b) a++, b++;
    return (int64_t)*a - (int64_t)*b;
}

void hle_memcpy(Cpu *c) { memmove(P(0), P(1), c->x[2]); }  // (memmove: an overlapping copy behaves as the SDK's)
void hle_memmove(Cpu *c) { memmove(P(0), P(1), c->x[2]); }
void hle_memset(Cpu *c) { memset(P(0), (int)(uint8_t)c->x[1], c->x[2]); }
void hle_memcmp(Cpu *c) { c->x[0] = (uint64_t)(memcmp(P(0), P(1), c->x[2]) ? byte_diff(CP(0), CP(1)) : 0); }
void hle_bcmp(Cpu *c) { c->x[0] = memcmp(P(0), P(1), c->x[2]) != 0; }
void hle_strlen(Cpu *c) { c->x[0] = strlen((const char *)P(0)); }
void hle_strcmp(Cpu *c) {
    const uint8_t *a = CP(0), *b = CP(1);
    while (*a && *a == *b) a++, b++;
    c->x[0] = (uint64_t)((int64_t)*a - (int64_t)*b);
}
void hle_strncmp(Cpu *c) {
    const uint8_t *a = CP(0), *b = CP(1);
    uint64_t n = c->x[2];
    if (!n) { c->x[0] = 0; return; }
    while (--n && *a && *a == *b) a++, b++;
    c->x[0] = (uint64_t)((int64_t)*a - (int64_t)*b);
}
void hle_memchr(Cpu *c) { c->x[0] = (uint64_t)(uintptr_t)memchr(P(0), (int)(uint8_t)c->x[1], c->x[2]); }

// ------------------------------------------------------------------ HLE Allocator
// The SDK and musl call malloc/calloc during DT_INIT before nninitStartup has initialized
// the main game heap (0x7004759418). Intercepting these symbols with HLE ensures early
// allocations are satisfied safely from the guest-visible HLE_HEAP pool.

static void *hle_malloc_internal(size_t size) {
    if (!size) size = 1;
    size_t total = (size + 15 + 16) & ~15ull;
    uint8_t *p = (uint8_t *)hle_alloc(total);
    if (!p) return NULL;
    *(uint64_t *)p = size;
    return p + 16;
}

HLE_FUNC("malloc", hle_malloc) {
    uint64_t size = c->x[0];
    c->x[0] = (uint64_t)(uintptr_t)hle_malloc_internal(size);
}

HLE_FUNC("calloc", hle_calloc) {
    uint64_t n = c->x[0], sz = c->x[1];
    c->x[0] = (uint64_t)(uintptr_t)hle_malloc_internal(n * sz);
}

HLE_FUNC("realloc", hle_realloc) {
    uint64_t ptr = c->x[0], size = c->x[1];
    if (!ptr) {
        c->x[0] = (uint64_t)(uintptr_t)hle_malloc_internal(size);
        return;
    }
    void *np = hle_malloc_internal(size);
    if (np && size) {
        size_t old_size = size;
        if (ptr >= HLE_HEAP && ptr < HLE_HEAP + HLE_HEAP_SIZE) {
            old_size = *(uint64_t *)((uint8_t *)(uintptr_t)ptr - 16);
            if (old_size > size) old_size = size;
        }
        memcpy(np, (void *)(uintptr_t)ptr, old_size);
    }
    c->x[0] = (uint64_t)(uintptr_t)np;
}

HLE_FUNC("free", hle_free) {
    (void)c;
}

HLE_FUNC("memalign", hle_memalign) {
    uint64_t align = c->x[0], size = c->x[1];
    (void)align;
    c->x[0] = (uint64_t)(uintptr_t)hle_malloc_internal(size);
}

HLE_FUNC("aligned_alloc", hle_aligned_alloc) {
    uint64_t align = c->x[0], size = c->x[1];
    (void)align;
    c->x[0] = (uint64_t)(uintptr_t)hle_malloc_internal(size);
}

HLE_FUNC("posix_memalign", hle_posix_memalign) {
    uint64_t out_ptr = c->x[0], align = c->x[1], size = c->x[2];
    (void)align;
    void *p = hle_malloc_internal(size);
    if (out_ptr) *(uint64_t *)(uintptr_t)out_ptr = (uint64_t)(uintptr_t)p;
    c->x[0] = p ? 0 : 12;
}
