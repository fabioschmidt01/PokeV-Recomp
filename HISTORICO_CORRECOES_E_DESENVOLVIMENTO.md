# Histórico Completo de Desenvolvimento, Adaptações e Correções
## Projeto: PokeV-Recomp (Port Nativo / Recompilador Estático para Pokémon Scarlet & Violet)

---

## 1. Visão Geral do Projeto

O **PokeV-Recomp** é uma adaptação do recompilador estático ARM64 para x86-64 nativo via Vulkan, baseado na linhagem arquitetural do **PokeL-ARecomp** / **PokeZ-ARecomp** / **LASRecomp**, customizado e mantido por **@fabioschmidt01** em colaboração com o assistente de IA **Antigravity (Google DeepMind / Gemini)**.

O objetivo central é executar **Pokémon Scarlet & Pokémon Violet** de forma nativa no PC sem sobrecarga de emulação de CPU, aproveitando a aceleração gráfica por hardware (Vulkan, otimizações para GPUs Intel Arc Xe2 e CPUs multi-core Intel Xeon).

---

## 2. Identificação Técnica do Jogo Alvo

| Atributo | Detalhes Técnicos |
|---|---|
| **Jogo Suportado** | Pokémon Violet & Pokémon Scarlet |
| **Title ID Base (Violet)** | `01008F6008C5E000` |
| **Title ID Base (Scarlet)** | `0100A3D008C5C000` |
| **Title ID Update (Violet)** | `01008F6008C5E800` |
| **Title ID Update (Scarlet)** | `0100A3D008C5E800` |
| **Versão Alvo Homologada** | **v786432** (Versão 3.0.1 + DLC The Teal Mask & The Indigo Disk) |
| **Build ID do Executável (`main`)** | `709BFD6611529864` |
| **Módulos Convidados Extraídos** | `main` (34 MB ELF), `sdk` (5.9 MB ELF), `subsdk0` (3.3 MB ELF) |
| **Tamanho da RomFS Unificada** | **9,92 GB** (descompactada e unificada com o patch v3.0.1 em `romfs.bin`) |

---

## 3. Etapas de Criação e Configuração Inicial

### A. Criação do Repositório Privado no GitHub
- Criação do repositório remoto: [`fabioschmidt01/PokeV-Recomp-privado`](https://github.com/fabioschmidt01/PokeV-Recomp-privado) via GitHub CLI (`gh repo create`).
- Clonagem / Inicialização do workspace local em:
  `D:\Rons\nintendo Switch\pokemon violet\PokeV-Recomp-privado`
- Configuração de autor Git local:
  - `user.name`: `fabioschmidt01`
  - `user.email`: `fabioschmidt01@users.noreply.github.com`
- Criação e envio da branch principal `main`.

### B. Adaptação da Ferramenta de Extração (`tools/zaimport`)
- O utilitário original em C#/.NET `zaimport` reconhecia apenas os Title IDs de Link's Awakening e Pokémon Legends Arceus.
- **Alteração efetuada**:
  Adicionados os Title IDs de Pokémon Violet e Scarlet no array de jogos suportados em [`tools/zaimport/Program.cs`](file:///D:/Rons/nintendo%20Switch/pokemon%20violet/PokeV-Recomp-privado/tools/zaimport/Program.cs), permitindo o reconhecimento automático das NSPs, descriptografia via `prod.keys` e `title.keys`, e montagem direta da `romfs.bin`.

### C. Extração e Unificação dos Dados do Jogo
- Comando de extração executado com sucesso:
  ```powershell
  dotnet run --project tools/zaimport -- `
    --title-keys "D:/Rons/nintendo Switch/pokemon violet/Jogo/title.keys" `
    "D:/Rons/nintendo Switch/pokemon violet/Jogo/prod.keys" `
    "D:/Rons/nintendo Switch/pokemon violet/PokeV-Recomp-windows-x64/extracted" `
    "D:/Rons/nintendo Switch/pokemon violet/Jogo/Pokemon Violet[01008F6008C5E000][US][v0].nsp" `
    "D:/Rons/nintendo Switch/pokemon violet/Jogo/Pokemon Violet [01008F6008C5E800][v786432].nsp"
  ```
- Criação de **Junction de Sistema de Arquivos** no Windows vinculando `PokeV-Recomp-privado\extracted` diretamente à pasta de execução `PokeV-Recomp-windows-x64\extracted`, permitindo reutilização imediata dos arquivos sem duplicação de quase 10 GB em disco.

### D. Pipeline de Compilação CI/CD no GitHub Actions
- Configuração do workflow `.github/workflows/build-all.yml`:
  - Compilação cruzada completa com Clang, UCRT64, LLVM, FFmpeg (LGPL), SDL3, Zig Slim e empacotamento Windows x64 (.zip).
  - Primeira release oficial gerada: **`v0.0.1`**.
  - O pacote binário resultante foi baixado e descompactado em `D:\Rons\nintendo Switch\pokemon violet\PokeV-Recomp-windows-x64`.

---

## 4. Primeira Compilação dos 1.730 Objetos do Jogo

Ao iniciar o launcher pela primeira vez:
- O tradutor AOT estático e o compilador Zig CC compilaram todos os módulos do jogo:
  - `main`: 180.337 funções traduzidas.
  - `sdk`: 39.287 funções traduzidas.
  - `subsdk0`: 13.662 funções traduzidas.
- **Total compilado**: **1.730 objetos** gerados em **1.628 segundos** (~27 minutos).
- **Biblioteca final gerada**: `extracted/lasgame.dll` com **382.829.568 bytes (~382 MB)** e hash `eac99c0f80004dc4-709BFD6611529864`.

---

## 5. O Erro e Diagnóstico de Baixo Nível (ARM64 / Horizon OS)

### Sintoma
Ao clicar em **"JOGAR"**, a janela de jogo abriu brevemente e travou com a caixa de diálogo:
```
The game crashed
This is a bug in PokeL-ARecomp, not a problem with your game files or PC.
Log file: D:\Rons\nintendo Switch\pokemon violet\PokeV-Recomp-windows-x64\lasrecomp-backup-01dd70b73839f5a2-19652.log
```

### Análise do Log de Crash
No arquivo [`lasrecomp-backup-01dd70b73839f5a2-19652.log`](file:///D:/Rons/nintendo%20Switch/pokemon%20violet/PokeV-Recomp-windows-x64/lasrecomp-backup-01dd70b73839f5a2-19652.log):
```
init sdk (DT_INIT 7008000030, 112 init_array entries)

*** exception c0000005 accessing 0x30
    host pc 7ffc9552eaca (f_7002b7d830+7a)
    host lr 7008da4ae0 (?)
guest: sp=723ffffd10 lr=700858fb20
  x0  0000000000000030  x1  00000070085403b4  x2  0000000000000000
  x10 0000000000000000  x16 0000007008cd6bc0  x17 0000007002b7d830
```

### Engenharia Reversa e Desmontagem ARM64
Desmontando a função convidada `f_7002b7d830` no executável `main` (descompactado do NSO via LZ4):
```arm64
7002b7d830:  sub   sp, sp, #0x30
7002b7d834:  stp   x29, x30, [sp, #0x10]
7002b7d838:  add   x29, sp, #0x10
7002b7d83c:  str   x19, [sp, #0x20]
7002b7d840:  mov   x8, x0
7002b7d844:  movz  x0, #0, lsl #16
7002b7d848:  movk  x0, #0x30
7002b7d84c:  nop   
7002b7d850:  nop   
7002b7d854:  mrs   x10, tpidr_el0         ; <--- Lê registrador de Thread Pointer (TLS)
7002b7d858:  ldr   x9, [x10, x0]          ; <--- Falha: acessa [x10 + 0x30]
7002b7d85c:  cbz   x9, #0x7002b7d884
```

### Causa Raiz Descoberta
1. **O que é a função `0x7002b7d830`**: É o alocador `malloc` do Pokémon Violet. A sequência de instruções acima é a implementação padrão da ABI ARM64 ELF de Local-Exec Thread-Local Storage (TLS) para cache rápido de arena por thread.
2. **O problema no runtime**:
   - No Nintendo Switch Horizon OS, existem dois registradores de thread:
     - `TPIDRRO_EL0`: Read-Only para userland, aponta para a TLR (Thread Local Region) de 512 bytes (IPC + slots de TLS do SDK).
     - `TPIDR_EL0`: Read/Write para userland, aponta para a estrutura do Thread Pointer / TLS da biblioteca C/C++.
   - No código original do runtime ([`runtime/kernel.c`](file:///D:/Rons/nintendo%20Switch/pokemon%20violet/PokeV-Recomp-privado/runtime/kernel.c)), a função `thread_new()` configurava apenas:
     ```c
     t->tlr = tls_next;
     tls_next += 0x200;
     t->cpu.tpidrro = t->tlr;
     // t->cpu.tpidr permanecia NULO (0x0000000000000000)!
     ```
   - No Pokémon Violet, o executável `main` possui **5.424 ocorrências** de leitura de `mrs tpidr_el0`.
   - Como `tpidr_el0` era 0, a instrução `ldr x9, [x10, x0]` tentava ler `[0x0 + 0x30]`, gerando imediatamente o crash do Windows **`c0000005 (EXCEPTION_ACCESS_VIOLATION)`** no endereço `0x30`.
3. **Descoberta adicional no `sdk`**:
   No módulo `sdk`, encontramos as rotinas que manipulam `tpidr_el0`:
   ```arm64
   700840e204: mrs  x9, tpidrro_el0
   700840e20c: str  x8, [x9, #0x1f0]        ; Guarda ThreadPointer no offset 0x1f0 da TLR
   700840e210: msr  tpidr_el0, x8          ; Atualiza TPIDR_EL0
   ```
   Isso confirmou que no padrão oficial da Nintendo, o offset `0x1f0` da Thread Local Region é reservado para guardar o ponteiro de `tpidr_el0`!

---

## 6. Correções Implementadas

### A. Inicialização de TLS e Thread Pointer em `runtime/kernel.c`
Modificado o método [`thread_new`](file:///D:/Rons/nintendo%20Switch/pokemon%20violet/PokeV-Recomp-privado/runtime/kernel.c#L294):
- Cada thread agora recebe um bloco ampliado de `0x1000` (4.096 bytes), totalmente zerado via `memset`.
- Os primeiros `0x200` bytes permanecem dedicados à Thread Local Region oficial (buffer de mensagens IPC e controle de sincronização).
- `t->cpu.tpidr` agora é inicializado em `t->tlr + 0x200` (espaço exclusivo para variáveis de thread locais, imune a sobrescritas por IPC).
- O slot oficial da Nintendo em `[tpidrro_el0 + 0x1f0]` é preenchido com `t->cpu.tpidr`.

```c
// runtime/kernel.c (thread_new)
pthread_mutex_lock(&g_klock);
t->id = next_thread_id++;
t->tlr = tls_next;
tls_next += 0x1000;
memset((void *)(uintptr_t)t->tlr, 0, 0x1000);
t->cpu.tpidrro = t->tlr;
t->cpu.tpidr = t->tlr + 0x200;
*(uint64_t *)(uintptr_t)(t->tlr + 0x1f0) = t->cpu.tpidr;
t->anext = g_threads;
g_threads = t;
pthread_mutex_unlock(&g_klock);
```

### B. Expansão do Pool Global de TLS em `runtime/rt.h`
Modificado [`runtime/rt.h`](file:///D:/Rons/nintendo%20Switch/pokemon%20violet/PokeV-Recomp-privado/runtime/rt.h#L43):
- Aumentado o espaço virtual de TLS de 1 MB para 4 MB:
  ```c
  #define TLS_BASE     0x7090000000ull
  #define TLS_SIZE     0x0000400000ull   // 4 MB (suporta até 1024 threads simultâneas a 4KB cada)
  ```
- O layout de memória possui mais de 28 MB de folga antes do início do `HLE_HEAP` (`0x7092000000ull`), sendo 100% seguro contra sobreposição.

---

## 7. Garantia de Preservação do Código Compilado (`lasgame.dll`)

Uma regra crucial do projeto:
- A variável `GAMELIB_ID` no `Makefile` calcula o hash SHA-256 apenas dos arquivos geradores e headers do guest:
  `tools/gen.py`, `tools/lifter.py`, `runtime/cpu.h`, `runtime/simd.h`, `runtime/gamelib.h`.
- Nem [`runtime/kernel.c`](file:///D:/Rons/nintendo%20Switch/pokemon%20violet/PokeV-Recomp-privado/runtime/kernel.c) nem [`runtime/rt.h`](file:///D:/Rons/nintendo%20Switch/pokemon%20violet/PokeV-Recomp-privado/runtime/rt.h) fazem parte desse hash.
- Por consequência:
  **A compilação de 27 minutos realizada pelo usuário (`extracted/lasgame.dll` de 382 MB) permanece 100% válida e íntegra, dispensando qualquer recompilação dos 1.730 arquivos.**

---

## 8. Crash #2: Exceção c0000005 accessing 0 em f_7002b7d830+14a (malloc durante init sdk)

### A. Diagnóstico e Causa Raiz
Ao tentar iniciar o jogo na versão `v0.0.2`, o Launcher travou com o log:
```
init sdk (DT_INIT 7008000030, 112 init_array entries)
*** exception c0000005 accessing 0
    host pc 7ffc9552eb9a (f_7002b7d830+14a)
    host lr 7008da4ae0 (?)
```

**Análise de Engenharia Reversa:**
1. A função de inicialização do executável guest `nn::init::Start` (`0x70082dc200`) segue estritamente esta ordem de execução:
   - Passo 1: `rtld_init_sdk` (chama o `DT_INIT` do módulo `sdk` em `0x7008000030`).
   - Passo 2: `_init_libc1`
   - Passo 3: `nninitInitializeSdkModule`
   - Passo 4: `nninitStartup` (endereço `0x7002b7da90` no módulo `main` - **é esta rotina que inicializa o ponteiro do heap do jogo em `0x7004759418`!**)
   - Passo 5: `_init_libc2`
   - Passo 6: `rtld_init_main`
   - Passo 7: `nnMain`
2. No passo 1, o construtor global do `sdk` executa uma chamada para `malloc(0x38)` através da entrada GOT `0x7008cd6bc0`.
3. Como o `runtime/loader.c` resolvia símbolos não interceptados por HLE buscando nos outros módulos carregados, o símbolo `malloc` foi resolvido para a implementação interna do `main` (`f_7002b7d830`).
4. Porém, dentro de `f_7002b7d830`, o código lê `[0x7004759418]`, que é a estrutura do alocador principal do jogo.
5. Como `nninitStartup` ainda **não havia rodado**, `0x7004759418` continha `0x0000000000000000`.
6. Ao tentar desreferenciar `[0x0] + offset`, ocorreu uma violação de acesso imediata `c0000005 accessing 0`.

### B. Solução Implementada: Alocador HLE Antecipado em `runtime/hle/libc.c`
Interceptamos todas as importações de alocação de memória C padrão (`malloc`, `calloc`, `realloc`, `free`, `memalign`, `aligned_alloc`, `posix_memalign`) via HLE.
O `loader.c` da arquitetura do recompilador prioriza `hle_lookup_impl(name)` sobre os símbolos dos módulos convidados. Com isso:
- O `sdk` e o `subsdk0` recebem memória segura, alinhada e zerada do pool reservado de 224 MB (`HLE_HEAP` em `0x7092000000ull`) via `hle_alloc()`.
- O `main` não sofre tentativa de uso de memória antes da chamada de `nninitStartup`.

---

## 9. Sincronização Completa de Melhorias de Estabilidade (Arceus ➔ Violet)

Foram portadas e sincronizadas as seguintes melhorias críticas originárias do PokeZ-ARecomp (Legends Arceus):

| Componente | Arquivo Modificado | Melhoria Aplicada |
|---|---|---|
| **Build Cache & Trava** | `runtime/build_cache.cpp` | Geração automática do arquivo de estado persistente `recomp_state.ini` ao finalizar o build. |
| **Bypass de Recompilação** | `runtime/gamelib.c` | Verificação de `state_matches(game_dir, want)`. Se `lasgame.dll.id` e `recomp_state.ini` coincidirem com a CPU, o launcher entra direto no menu com botão **JOGAR** ativo, sem reconstruir arquivos. |
| **Tabela de Desvios (Setjmp)** | `runtime/dispatch.c` | Expansão de slots `NJMP` de 32 para 256, mecanismo de poda de pilha para frames mortos (`sp < c->sp`) e fallback por PC de retorno em `dispatch_slow`. |
| **Shaders Atômicos 64-bit** | `runtime/nvn/maxwell/translate.c` | Suporte completo para `atom size 2` (64-bit atomics) no compilador Maxwell -> GLSL/Vulkan, manipulando metades baixa e alta (`old` e `old_hi`). |
| **Threading para Xeon** | `runtime/nvn/vulkan/textures.c` | Calibração do pool de descompactação paralela de texturas para CPUs multi-core (até 10 threads para Xeon 24+ threads) com log informativo. |
| **Identidade Visual & Janela** | `runtime/crash_explain.c`<br>`runtime/platform/windows.c` | Correção dos textos residuais do Arceus, padronizando os alertas e diálogos para **PokeV-Recomp**. |

---

## 10. Versionamento dos Commits

| Commit | Tag | Mensagem | Escopo |
|---|---|---|---|
| `14ff341` | `v0.0.1` | `feat(pokev): initial commit for PokeV-Recomp (Pokémon Scarlet & Violet)` | Criação do recompiler, zaimport com Title IDs de SV, CI/CD Windows e Linux. |
| `cfbbeab` | - | `fix(kernel): initialize tpidr with thread local region to prevent TLS crash in malloc` | Correção do crash `c0000005 accessing 0x30`. Inicialização correta de `tpidr_el0` e expansão do pool TLS para 4 MB. |
| `fe0cd1a` | `v0.0.2` | `docs: add comprehensive development and bugfix history document` | Documentação inicial e release v0.0.2. |
| `c612890` | `v0.0.3` | `fix(hle): add HLE malloc/free allocator and sync stability features from Arceus` | Correção do crash `c0000005 accessing 0` via alocador HLE em `libc.c` e sincronização total de melhorias de estabilidade do Arceus. |

---

*Documento gerado automaticamente pelo assistente de IA Antigravity (Google DeepMind) para documentação contínua do projeto PokeV-Recomp.*
