# PokeV-Recomp: Developer & Architecture Guide (Antigravity / Gemini)

Port nativo e recompilador estático para PC de **Pokémon Scarlet & Violet (3.0.1)**, adaptado e otimizado a partir do projeto PokeL-ARecomp / PokeZ-ARecomp / LAS Recomp por **@fabioschmidt01** em colaboração com o assistente de IA **Antigravity (Google DeepMind / Gemini)**.

O código ARM64 do Nintendo Switch é traduzido antecipadamente (AOT) para C puro e compilado para x86-64 nativo; o runtime recria o microkernel Horizon do Switch e o subsistema gráfico NVN diretamente sobre a API **Vulkan**.

---

## 1. Identificação do Jogo Suportado

| Atributo | Valor Oficial |
|---|---|
| **Título** | Pokémon Scarlet & Violet (SV) |
| **Title ID Base Violet** | `01008F6008C5E000` |
| **Title ID Update Violet** | `01008F6008C5E800` |
| **Title ID Base Scarlet** | `0100A3D008C5C000` |
| **Title ID Update Scarlet** | `0100A3D008C5C800` |
| **Versão Homologada** | **3.0.1** (Update v786432) |
| **Build ID (`main`)** | `709BFD6611529864` |
| **Módulos Convidados** | `main`, `sdk`, `subsdk0` |

---

## 2. Hardware-Alvo e Otimizações Específicas

O projeto conta com calibrações dedicadas para a estação de trabalho do desenvolvedor:

### A. Intel Xeon Multi-Threading (>= 24 threads lógicas)
- **Localização**: [`runtime/nvn/vulkan/textures.c`](file:///D:/Rons/nintendo%20Switch/pokemon%20violet/PokeV-Recomp-privado/runtime/nvn/vulkan/textures.c)
- **Otimização**: Detecção dinâmica de alta contagem de threads na CPU. Em processadores com 24 ou mais threads lógicas (como a linha Intel Xeon E5), o descompactador paralelo de texturas (`LARECOMP_TEX_UNPACK_THREADS`) é elevado para até 10 threads dedicadas, eliminando engasgos (stutter) durante streaming de áreas abertas de Paldea.

### B. Intel Arc B580 (Arquitetura Xe2 Battlemage, 12 GB GDDR6)
- **Localização**: [`runtime/nvn/vulkan/device.c`](file:///D:/Rons/nintendo%20Switch/pokemon%20violet/PokeV-Recomp-privado/runtime/nvn/vulkan/device.c)
- **Otimização**: Identificação de GPUs discretas Intel (`0x8086` + `VK_PHYSICAL_DEVICE_TYPE_DISCRETE_GPU`). Desbloqueio do pool de memória guest original do Switch, permitindo alocação ampla nos 12 GB de VRAM de alta velocidade.

### C. Intel XeSS (Xe Super Sampling) SDK 3.0.2
- **Localização**: [`runtime/nvn/vulkan/vk_xess.h`](file:///D:/Rons/nintendo%20Switch/pokemon%20violet/PokeV-Recomp-privado/runtime/nvn/vulkan/vk_xess.h), [`runtime/nvn/vulkan/xess.cpp`](file:///D:/Rons/nintendo%20Switch/pokemon%20violet/PokeV-Recomp-privado/runtime/nvn/vulkan/xess.cpp), [`third_party/xess/`](file:///D:/Rons/nintendo%20Switch/pokemon%20violet/PokeV-Recomp-privado/third_party/xess/)
- **Otimização**: Carregador dinâmico de `libxess.dll` via Vulkan. Quando uma GPU Intel Arc com aceleradores matriciais XMX é detectada, o upscale neural por IA é habilitado diretamente no pipeline gráfico (com fallback gracioso para DP4a em GPUs NVIDIA/AMD).

---

## 3. Filosofia de Desenvolvimento e CI na Nuvem

Para preservar o sistema operacional local limpo e sem necessidade de dezenas de gigabytes de compiladores globais:

- **Desenvolvimento Local Leve**: O computador local necessita apenas de [.NET SDK](https://dotnet.microsoft.com/) e [Python](https://www.python.org/) para manipulação de dados e extração do jogo.
- **Compilação 100% no GitHub Actions**: Toda compilação pesada (Clang, UCRT64, LLVM, FFmpeg, SDL3, Zig Slim e Docker Ubuntu para AppImage) roda automaticamente na infraestrutura do GitHub.
- **Ambiente de Testes e Versionamento**:
  - Versionamento granular por tags (`v0.0.1`, `v0.0.2`, `v0.0.3`...) até atingir a versão estável `0.1.0`.
  - Repositório privado oficial: [`fabioschmidt01/PokeV-Recomp-privado`](https://github.com/fabioschmidt01/PokeV-Recomp-privado).

---

## 4. Estrutura de Diretórios e Onde Fica Cada Coisa

```
PokeV-Recomp-privado/
├── .github/workflows/
│   └── build-all.yml         # CI/CD: Compila Windows (.zip) e Linux (.AppImage)
├── docs/                     # Documentação de arquitetura e notas de compilação
├── extracted/                # (Ignorado no git) Arquivos do jogo extraídos
│   ├── exefs/                # main, sdk, subsdk0, main.npdm
│   └── romfs.bin             # RomFS de ~9.92 GB gerada com patch 3.0.1
├── runtime/
│   ├── gamebuild.c           # Orquestrador de geração e compilação do jogo
│   ├── loader.c              # Carregador de NSO com suporte a subsdk0
│   ├── nvn/vulkan/           # Backend Vulkan, Intel Arc e XeSS 3.0.2
│   └── ui/                   # Interface gráfica (Launcher & Menu F1)
├── third_party/
│   └── xess/                 # Headers e bibliotecas de importação do Intel XeSS SDK
└── tools/
    ├── zaimport/             # Importador C# / .NET para extrair NSPs e montar RomFS
    ├── gen.py                # Tradutor estático ARM64 -> C nativo
    ├── sv_patches.py         # Patches específicos para Pokémon Scarlet & Violet
    └── za/dist.sh            # Empacotador do release final com Zig e dependências
```

---

## 5. Comandos Úteis

### Extrair a ROM do Jogo Localmente (via `zaimport`)
```powershell
dotnet run --project tools/zaimport -- `
  --title-keys "<caminho>/title.keys" `
  "<caminho>/prod.keys" `
  "extracted" `
  "<caminho>/Pokemon Violet [01008F6008C5E000][v0].nsp" `
  "<caminho>/Pokemon Violet [01008F6008C5E800][v786432].nsp"
```

### Acompanhar o Status da Compilação no GitHub Actions
```powershell
gh run list
gh run watch <run-id>
```

---

## 6. Atalhos e Teclas no Jogo

- **F1**: Abre o Menu de Configurações (Resolução, VSync, Filtros, Áudio, Controles).
- **F9**: Captura o dump de passes do próximo frame renderizado.
- **F10**: Salva captura de tela em alta qualidade na pasta `screenshots/`.
