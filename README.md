<div align="center">

<img src="docs/icon/icon_1024.png" alt="PokeV-Recomp icon" width="140">

# PokeV-Recomp (SV Recomp)

**A native PC port of *Pokémon Violet*, built by static recompilation. Work in progress.**

**English** · [Português (Brasil)](README.pt-BR.md)

[Report an issue](../../issues) ·
[Releases](../../releases)

</div>

---

> [!WARNING]
> **Work in progress: expect bugs and crashes.**
> PokeV-Recomp is still at an early stage. Even in my own testing and my friends', there are graphical glitches,
> performance drops and crashes, and you will probably run into others. Please be patient, and help us by
> [reporting bugs and crashes](../../issues) (with your `logs/play.log` file when you can): every report helps
> improve the project.
>
> **Development will be slower for a while**, as my main focus right now is
> [PokeL-ARecomp](https://github.com/fabioschmidt01/PokeL-ARecomp).

**PokeV-Recomp** (SV Recomp) turns the Nintendo Switch code of *Pokémon Violet* into a native 64-bit program for
Windows (and Linux, untested so far).
The game's ARM64 machine code is translated ahead of time into C and compiled for x86-64 on your own PC. The Switch's
operating system services, file system, audio and NVN graphics are re-implemented on top of Vulkan.

**No emulator runs while you play.** The game's code executes natively on your CPU and GPU.

> [!IMPORTANT]
> **You need your own copy of the game.** PokeV-Recomp does not include any game code, ROM, asset, texture, font or
> encryption key, and never will. You provide the files from the game you own; the recompilation happens locally on
> your machine.

---

## Current status

This is an early, in-development port. The game boots, loads a save and is playable in the open world, but it is not
finished and has only been tested on one machine (Intel Arc B580, Xeon E5-2650 v4, Windows 10).

**Known issues**

- Small white specks along triangle edges on terrain and grass.
- Character hair can render bright cyan.
- The frame rate is unsteady in the open world (around 40 fps on the test machine, with drops), and there are hitches
  the first time each shader is compiled.
- Only *Pokémon Violet* 3.0.1 is recognised. *Pokémon Scarlet* is not supported yet.
- **Linux is untested.** Releases include an AppImage built automatically from the same code, but nobody has run it on
  real hardware yet. Reports are welcome ([docs/linux.md](docs/linux.md) lists what to include).

Every fix and its validation state is logged in
[HISTORICO_CORRECOES_E_DESENVOLVIMENTO.md](HISTORICO_CORRECOES_E_DESENVOLVIMENTO.md) (in Portuguese).

---

## Features

Most of these come from the runtime this project is built on (see [Credits](#credits--acknowledgements)). They are
available in the F1 menu; not all of them have been validated with *Pokémon Violet* yet.

### Performance
- **30 or 60 fps target** (option). See the known issues above for where it stands today.
- **Internal resolution scale**, with optional dynamic resolution.
- **Multi-threaded texture unpacking**, scaled to the number of CPU threads.

### Graphics
- **Upscalers**: bilinear, AMD FSR 1, Intel XeSS; AMD FSR 2 (temporal) and SMAA anti-aliasing.
- **Lighting options**: ambient occlusion (XeGTAO), indirect light, water reflections, shadow resolution and sharpness.
- **HDR output** (option).
- **HD texture packs**: an *Original / HD* switch in the menu loads replacement textures from `textures/hd/`.
- **Mods**: `mods/<name>/romfs` layers over the game's files, each switched on or off in the start screen's Mods tab.
  A Brazilian Portuguese translation by [PKG Traduções](https://pkgtraducoes.com.br/) installs this way (not included:
  get it from them). The Mods tab links their download and credits them.
- **Save backups**: each save is also copied to `save/backups/` (the 10 newest, at most one every 5 minutes).

### Controls
- Gamepads through SDL3 (Xbox, DualShock 4, DualSense, Switch Pro Controller, Steam Deck).
- Keyboard and mouse, with a mouse-driven camera and rebindable keys.

---

## Supported version

| Game | Title ID | Version | `main` build ID | Status |
|---|---|---|---|---|
| **Pokémon Violet** | `01008F6008C5E000` | **3.0.1** (update v786432) | `709BFD6611529864` | Supported |
| **Pokémon Scarlet** | `0100A3D008C5C000` | 3.0.1 | - | Not supported yet |

---

## Requirements

| Component | Expected minimum (not tested) | Tested |
|---|---|---|
| **Operating system** | Windows 10/11 64-bit, or Linux x86-64 with glibc 2.35+ | Windows 10 |
| **Processor** | x86-64 with AVX2, 4 cores | Intel Xeon E5-2650 v4 (12 cores / 24 threads) |
| **Graphics card** | Vulkan 1.3, 4 GB of video memory | Intel Arc B580 (12 GB) |
| **Memory** | 8 GB | 16 GB |
| **Storage** | ~15 GB free | SSD |

---

## Quick start

1. Download `PokeV-Recomp-windows-x64.zip` from the [Releases](../../releases) page (Linux:
   `PokeV-Recomp-linux-x86_64.AppImage`, untested - make it executable and run it; the steps below are the same).
2. Extract it into a folder you can write to (for example `C:\Games\PokeV-Recomp`).
3. Have your own copy of the game ready, in one of these forms:
   - the game extracted (`exefs` and `romfs` folders) at version **3.0.1** - no keys needed; or
   - your dump: the base game (`.xci` or `.nsp`), the **3.0.1 update** (`.nsp`) and the `prod.keys` from your own
     console.
4. Run `PokeV-Recomp.exe`.
5. On the start screen, choose the folder with your game files and click **Set up the game**.
   The game's version is checked first: only Pokémon Violet 3.0.1 is set up (Scarlet, other versions and other
   games' files are refused, with the reason on screen). On Linux, the game files, saves and settings live in
   `~/.local/share/pokev-recomp` (see [docs/linux.md](docs/linux.md)); `prod.keys` is also found in `~/.switch`.
6. The first setup recompiles the game's code on your PC. It takes 10 to 30 minutes depending on the CPU and happens
   once (again only when an update changes how the code is generated).
7. Click **Play**.

---

## Controls

Keyboard movement is on **W / A / S / D** and the camera follows the mouse. Every key and button can be seen and
changed in the F1 menu.

| Key | Action |
|---|---|
| F1 | Settings menu |
| F9 | Dump the next frame's render passes into `build/` (diagnostics) |
| F10 | Performance overlay |
| F11 | Toggle fullscreen |
| F12 | Save a screenshot to `screenshots/` |

---

## Credits & acknowledgements

- **Peiikai**: creator of [LAS Recomp](https://github.com/peiikai/LASRecomp) - the static recompiler, the runtime
  architecture and the Maxwell shader translator this project is built on.
- **Hexveil404**: creator of [PokeZ-ARecomp](https://github.com/Hexveil404/PokeZ-ARecomp), which brought the Switch OS
  services and the Pokémon engine support.
- **fabioschmidt01 & Antigravity**: architecture, Intel Xeon multi-threading, Intel Arc B580 tuning, Intel XeSS
  integration, and the Pokémon Violet & Arceus ports.
- **Ryujinx project**: behavioural reference for the Switch kernel and the NVN GPU.
- **[PKG Traduções](https://pkgtraducoes.com.br/)**: the Brazilian Portuguese translation mod (distributed by them).
- **Open-source libraries**: SDL3, FFmpeg, Dear ImGui, Vulkan Memory Allocator, Shaderc, XeGTAO, LibHac, Intel XeSS SDK.

PokeV-Recomp's own code is under the [MIT license](LICENSE); the components in `third_party/` keep their own licenses.

---

## Legal notice

*PokeV-Recomp* is a fan-made research and preservation project. It is **not** endorsed by, affiliated with or sponsored
by Nintendo, Game Freak, Creatures Inc. or The Pokémon Company. *Pokémon*, *Pokémon Scarlet* and *Pokémon Violet* are
trademarks of their respective owners. No Nintendo code, game binary, texture, model or font is distributed in this
repository or in its releases.
