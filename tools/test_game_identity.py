"""Game identity (runtime/game_identity.h): only Pokémon Violet 3.0.1 is accepted for setup and compilation; Legends:
Arceus, Z-A and Link's Awakening files are refused by name (issue #1). Also checks the start screen and main.c take
their answer from that header, not a table of their own. Fake NSO headers in a scratch folder; no game files used."""
import os
from pathlib import Path
import re
import shlex
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
with tempfile.TemporaryDirectory() as directory:
    directory = Path(directory)
    exe = directory / ('game-identity-test.exe' if os.name == 'nt' else 'game-identity-test')
    for cc, std in ((os.environ.get('CC', 'clang'), '-std=gnu11'), (os.environ.get('CXX', 'clang++'), '-std=gnu++17')):
        src = ['tools/test_game_identity.c'] if std.endswith('11') else ['-x', 'c++', 'tools/test_game_identity.c']
        subprocess.run(shlex.split(cc) + [std, '-Wall', '-Werror', '-Iruntime'] + src + ['-o', str(exe)],
                       cwd=ROOT, check=True)
        scratch = directory / 'scratch'
        scratch.mkdir(exist_ok=True)
        run = subprocess.run([str(exe), str(scratch)], capture_output=True, text=True)
        print(run.stderr + run.stdout, end='')
        assert run.returncode == 0 and 'all checks passed' in run.stdout, f'game identity test failed ({std})'

# The SV build id must agree with the generator's (tools/sv_patches.py SV_BUILDS: what gen.py patches as Violet)
sv = (ROOT / 'tools/sv_patches.py').read_text()
header = (ROOT / 'runtime/game_identity.h').read_text()
m = re.search(r'\{\{([^}]*)\}, "Pok\\xc3\\xa9mon Violet", "3\.0\.1", true\}', header)
assert m, 'Violet 3.0.1 entry not found in game_identity.h'
violet = ''.join(b.strip()[2:] for b in m.group(1).split(','))
assert f"'{violet}': '3.0.1'" in sv, f'{violet} is not tools/sv_patches.py SV_BUILDS\'s Violet 3.0.1'

# The start screen and main.c take the answer from the header: no build table of their own that could let another
# game's files through again (v0.0.24's launcher accepted Arceus 1.1.1, Z-A and Link's Awakening)
launcher = (ROOT / 'runtime/ui/launcher.mm').read_text()
main = (ROOT / 'runtime/main.c').read_text()
assert 'return game_identity_supported(id);' in launcher
for src, name in ((launcher, 'launcher.mm'), (main, 'main.c')):
    for other in ('0xae, 0xe8, 0xf1, 0x50', '0x72, 0x22, 0xe1, 0x3e', '0xae, 0x16, 0xf7, 0x1e'):
        assert other not in src, f'{name} still lists another game\'s build id ({other})'
# every compile goes through build_game_code, which checks the identity before gamebuild_run
assert launcher.count('gamebuild_run(') == 1
body = launcher[launcher.index('static bool build_game_code(void)'):]
assert body.index('build_id_ok(g_root + "/exefs/main")') < body.index('gamebuild_run(')
print('only Pokémon Violet 3.0.1 is set up and compiled; Arceus / Z-A / Link\'s Awakening files are refused by name')
