"""Data folder isolation (runtime/paths.c, Linux): PokeV-Recomp's data root is $XDG_DATA_HOME/pokev-recomp
(~/.local/share/pokev-recomp), never another recomp's - v0.0.24 used PokeL-ARecomp's plarecomp/ and took Arceus's
extracted/ there for its own (issue #1). Builds tools/test_data_dir.c with the real paths.c and runs it under scratch
HOME / XDG_DATA_HOME values next to fake plarecomp/, zarecomp/ and lasrecomp/ folders, which must stay byte for byte
as they were. Scratch folders only: the player's own data is never read."""
import hashlib
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
if not sys.platform.startswith('linux'):
    print('data dir test: Linux only (Windows keeps its data next to the .exe)')
    sys.exit(0)
flags = []
deps = os.environ.get('DEPS')  # (a prefix with SDL3, as for make DEPS=)
if deps:
    flags = [f'-I{deps}/include', f'-L{deps}/lib', f'-Wl,-rpath,{deps}/lib', '-lSDL3']
elif shutil.which('pkg-config') and subprocess.run(['pkg-config', '--exists', 'sdl3']).returncode == 0:
    flags = shlex.split(subprocess.run(['pkg-config', '--cflags', '--libs', 'sdl3'], capture_output=True, text=True,
                                       check=True).stdout)


def snapshot(top):
    """Every path under top: files with their size, mtime and contents' hash; folders by mode only (rt_paths_init's
    write check creates and removes a .write_test file in the data root, which moves a folder's mtime)."""
    out = {}
    for p in sorted(top.rglob('*')):
        st = p.lstat()
        if p.is_dir() and not p.is_symlink():
            out[str(p.relative_to(top))] = (st.st_mode,)
            continue
        h = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() and not p.is_symlink() else ''
        out[str(p.relative_to(top))] = (st.st_mode, st.st_size, st.st_mtime_ns, h)
    return out


ARCEUS_MAIN = b'NSO0' + bytes(0x3c) + bytes.fromhex('aee8f150dda1b5a8') + bytes(0x38)
with tempfile.TemporaryDirectory() as directory:
    directory = Path(directory).resolve()
    exe = directory / 'data-dir-test'
    subprocess.run(shlex.split(os.environ.get('CC', 'clang')) +
                   ['-std=gnu11', '-Iruntime', 'runtime/paths.c', 'runtime/platform/linux.c', 'tools/test_data_dir.c',
                    '-o', str(exe)] + flags + ['-pthread', '-ldl'], cwd=ROOT, check=True)

    home = directory / 'home'
    share = home / '.local/share'
    # the other recomps' data folders, as a player with all of them installed has them
    for name in ('plarecomp', 'zarecomp', 'lasrecomp'):
        d = share / name
        (d / 'extracted/exefs').mkdir(parents=True)
        (d / 'extracted/exefs/main').write_bytes(ARCEUS_MAIN)
        (d / 'extracted/romfs.bin').write_bytes(b'romfs')
        (d / 'extracted/.gamebuild').mkdir()
        (d / 'save/save_0').mkdir(parents=True)
        (d / 'save/save_0/main').write_bytes(b'save of ' + name.encode())
        (d / 'larecomp.ini').write_text('fps60 = 1\n')
        (d / 'data_root.txt').write_text(str(d) + '\n')
    before = snapshot(share)
    start = directory / 'start'  # (where the AppImage is started from: no extracted/ there, so not dev mode)
    start.mkdir()

    def run(mode, **env):
        e = {k: v for k, v in os.environ.items()
             if k not in ('XDG_DATA_HOME', 'LARECOMP_DATA_ROOT', 'LARECOMP_DATA_HOME', 'LARECOMP_SETTINGS')}
        e.update(HOME=str(home), SDL_VIDEO_DRIVER='dummy', **env)
        r = subprocess.run([str(exe), mode], cwd=start, env=e, capture_output=True, text=True)
        assert r.returncode == 0, f'{mode}: exit {r.returncode}\n{r.stderr}'
        return r.stdout.split('\n')

    want = share / 'pokev-recomp'
    assert run('early')[0] == str(want), run('early')
    # XDG_DATA_HOME, when absolute, is the parent; a relative one is ignored (the XDG spec)
    xdg = directory / 'xdg'
    assert run('early', XDG_DATA_HOME=str(xdg))[0] == str(xdg / 'pokev-recomp')
    assert run('early', XDG_DATA_HOME='relative/dir')[0] == str(want)

    root, cwd = run('init')[:2]
    assert root == str(want) and cwd == str(want), (root, cwd)
    assert want.is_dir() and not (want / 'extracted').exists(), 'a fresh data folder has no game files'
    assert not (want / 'larecomp.ini').exists() or 'fps60 = 1' not in (want / 'larecomp.ini').read_text()
    for name in ('plarecomp', 'zarecomp', 'lasrecomp'):
        assert root != str(share / name)
    # a second start uses the same folder
    assert run('init')[0] == str(want)
    after = snapshot(share)
    after = {k: v for k, v in after.items() if k != 'pokev-recomp' and not k.startswith('pokev-recomp/')}
    assert after == before, 'another recomp\'s data folder changed'

    # Another app's game files are never deleted, whatever made them PokeV-Recomp's data root. Dev mode: started from
    # inside plarecomp/ (it has extracted/), the data root is that folder - setting up would have wiped Arceus's files
    plarecomp = share / 'plarecomp'
    e = {k: v for k, v in os.environ.items() if k not in ('XDG_DATA_HOME', 'LARECOMP_DATA_ROOT', 'LARECOMP_DATA_HOME')}
    r = subprocess.run([str(exe), 'remove'], cwd=plarecomp, env=dict(e, HOME=str(home), SDL_VIDEO_DRIVER='dummy'),
                       capture_output=True, text=True)
    out = r.stdout.split('\n')
    assert r.returncode == 0 and out[0] == str(plarecomp), r.stdout + r.stderr
    assert out[1] == 'foreign=1 Pok\u00e9mon Legends: Arceus 1.1.1' and out[2] == 'removed=0', out
    pla_now = {k: v for k, v in snapshot(share).items() if k.startswith('plarecomp')}
    assert pla_now == {k: v for k, v in before.items() if k.startswith('plarecomp')}, 'plarecomp changed (dev mode)'

    # In PokeV-Recomp's own data root: another app's files refused; Violet's own and unknown builds removed as before
    VIOLET_MAIN = b'NSO0' + bytes(0x3c) + bytes.fromhex('709bfd6611529864') + bytes(0x38)
    UNKNOWN_MAIN = b'NSO0' + bytes(0x3c) + bytes.fromhex('0123456789abcdef') + bytes(0x38)
    for main, foreign in ((ARCEUS_MAIN, True), (VIOLET_MAIN, False), (UNKNOWN_MAIN, False)):
        game = want / 'extracted'
        (game / 'exefs').mkdir(parents=True, exist_ok=True)
        (game / 'exefs/main').write_bytes(main)
        (game / 'romfs.bin').write_bytes(b'romfs')
        out = run('remove')
        assert out[1].startswith(f'foreign={int(foreign)}') and out[2] == f'removed={int(not foreign)}', (main[0x40:0x48].hex(), out)
        assert (game / 'exefs/main').exists() == foreign and (game / 'romfs.bin').exists() == foreign
        if foreign:
            shutil.rmtree(game)  # (the test's own copy)
    print('linux: data in ~/.local/share/pokev-recomp; plarecomp/, zarecomp/, lasrecomp/ untouched; another app\'s '
          'game files never deleted (dev mode or own data root)')
