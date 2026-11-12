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
| `a0e5146` | `v0.0.4` | `fix(hle): route post-startup malloc/free to CentralHeap and stub assertion breaks` | Resolução do trap em `nnmem_nlib_debug_break` (`NotNMallocPtrError`): roteamento dinâmico pós-startup para o alocador nativo do jogo via `game_heap_ready()`. |

---

## 11. Crash #3: FATAL undefined instruction / trap em 7008318020 (NotNMallocPtrError)

### A. Diagnóstico e Causa Raiz
Na versão `v0.0.3`, o jogo passou com sucesso por toda a inicialização de módulos (`init sdk`, `init subsdk0`, chamadas IPC de todos os serviços de sistema e 2.133 construtores globais de `init main`). Logo em seguida, ocorreu o erro fatal:
```
FATAL: undefined instruction / trap at 7008318020
host pc ... (rt_udf)
guest: sp=723ffffb20 lr=7008323ee4
x0  0000007092000a50  x1  0000007092000a50
```

**Análise de Engenharia Reversa:**
1. O endereço `0x7008318020` no módulo `sdk` é a função `nnmem_nlib_debug_break`, cujo código assembly ARM64 consiste em:
   ```arm64
   0x7008318020: udf #0xdefe
   0x7008318024: ret
   ```
   O recompilador traduziu a instrução `udf #0xdefe` para `rt_udf(c, 0x7008318020)`, interrompendo a execução.
2. A rotina chamadora em `lr = 0x7008323ee4` é `nn::nlibsdk::heap::CentralHeap::GetAllocSize(void const*)`.
3. Ao inspecionar `CentralHeap::GetAllocSize`, a rotina calcula se o ponteiro recebido em `x1` (`0x7092000a50`) pertence ao intervalo de páginas do `CentralHeap` gerenciado pelo jogo:
   ```arm64
   sub  x9, x1, x8
   cmp  x9, x10
   b.hs NotNMallocPtrError
   ```
4. Como `0x7092000a50` pertencia ao `HLE_HEAP` (alocado pelo nosso `hle_malloc`), ele falhou no teste de pertencimento ao `CentralHeap`, chamando `NotNMallocPtrError(ptr)`, que disparou o trap.

### B. Solução Implementada: Roteamento de Duas Fases em `runtime/hle/libc.c`
Implementamos a verificação atômica `game_heap_ready()` baseada no ponteiro global do alocador do jogo em `0x7004759418`:
- **Fase de Bootstrap (pré-startup, `*0x7004759418 == 0`)**: As alocações do construtor do SDK são atendidas com segurança no `HLE_HEAP`, impedindo a desreferência de ponteiro nulo (`c0000005`).
- **Fase de Execução Normal (pós-startup, `*0x7004759418 != 0`)**: Chamadas a `malloc`, `calloc`, `realloc`, `free`, `memalign`, `aligned_alloc` e `posix_memalign` são encaminhadas diretamente para as rotinas nativas do executável do jogo (`f_7002b7d830`), garantindo que todos os ponteiros pertençam legitimamente ao `CentralHeap`.
- **Proteção em `free` / `realloc`**: Ponteiros gerados durante a fase de bootstrap no `HLE_HEAP` são ignorados no `free` e realocados transparentemente para o `CentralHeap` no `realloc`.
- **Stubs de Proteção HLE**: Registrados stubs não-fatais para `nnmem_nlib_debug_break` e `NotNMallocPtrError`, garantindo que eventuais asserções do SDK não encerrem o processo abruptamente.

---
---

## 12. Crash #4: Abort on result 0x0 (2000-0) em InitializeBtmUserInterface (btm:u)

### A. Diagnóstico e Causa Raiz
Na versão `v0.0.4`, o Roteamento de Heap de Duas Fases foi 100% bem-sucedido:
- Todos os 2.133 construtores de `init main` executaram sem travar em `NotNMallocPtrError`.
- O jogo adentrou com sucesso em `nnMain`!
- O sistema de arquivos montou a partição de save (`save/save_0`) 18 vezes com sucesso.

Logo após a inicialização dos subsistemas de áudio e entrada, ocorreu a chamada:
```
[sm] GetService btm:u
[ipc] no HLE implementation for service 'btm:u', using logging stub
[ipc] STUB btm:u cmd 0 (in 0 bytes, x0 a0 b0 c0) -> ok
[am] IApplicationFunctions cmd 22 (unhandled, ok)
[kernel] abort on result 0x0 (2000-0)
  guest #0 700816b8e8
  guest #1 700816ba48
  guest #2 70080b8eb4
```

**Análise de Engenharia Reversa:**
1. O endereço `0x70080b8eb4` pertence à função `InitializeBtmUserInterface` (`0x70080b8d10`) no módulo `sdk`.
2. Essa rotina inicializa a interface de Bluetooth para comunicação com acessórios sem fio (como o Pokémon GO Plus+ no Pokémon Scarlet & Violet).
3. A rotina envia o comando IPC `cmd 0` (`GetCore`) para o serviço `btm:u`, esperando receber um sub-objeto `IBtmUserCore` (`resp->objects[resp->nobjects++] = sub_service`).
4. Como `btm:u` era apenas um stub de log genérico (`logging stub`), ele retornava 0 objetos. O SDK leu o endereço do ponteiro do objeto retornado na pilha (`[sp]`), encontrou `NULL` (0x0) e chamou `nn::diag::detail::AbortImpl`, resultando no `svcBreak` / encerramento do processo.

### B. Solução Implementada em `runtime/services/misc.c`
1. **Implementação HLE de `btm:u`, `btm:m`, `btm:s`, `btm`, `bt`**:
   - Criada a interface de sub-objeto `IBtmUserCore` retornada pelo comando 0 (`GetCore`).
   - Fornecidos manipuladores de evento não-sinalizados para comandos de BLE (`AcquireBleScanEvent`, `AcquireBleConnectionEvent`).
2. **Implementação HLE de `bcat:u`, `bcat:s`, `bcat:a`, `bcat:m`**:
   - Implementada a interface `IServiceForGeneral` para distribuição de eventos in-game (Mystery Gift, Tera Raids).
3. **Implementação HLE de `ectx:aw`, `ectx:r`**:
   - Implementada a interface `IErrorContext` para captura de relatórios de erro do Switch.

---
---

## 13. Diagnóstico do Log 25676.log: Conflito de Instância Dupla (lasrecomp.exe vs PokeV-Recomp.exe)

### A. Diagnóstico e Causa Raiz
No log `lasrecomp-backup-01dd70d7f7ce5d3d-25676.log`, ocorreu uma violação de acesso imediata logo no primeiro salto dinâmico do jogo (`f_70082dc200` / `nn::init::Start`):
```
*** exception c0000005 accessing 0x2d8627bd798
    host pc 7ff7ee3232d6 (lasrecomp.exe+32d6)
    host lr 7ffc87879967 (f_70082dc200)
host backtrace:
  #0  00007ff6543c07b8 lasrecomp+b07b8
  #1  00007ff654312a21 lasrecomp+2a21
  #2  00007ff654313bc8 lasrecomp+3bc8
  ...
  #10 00007ff7ee3232d6 lasrecomp.exe+32d6
```

**Análise Forense de Engenharia Reversa:**
1. Note que o backtrace continha **duas instâncias diferentes** do binário do recompilador carregadas na memória do mesmo processo:
   - Módulo `#0` (base `0x7ff654310000`): O processo principal lançado pelo usuário (`PokeV-Recomp.exe`).
   - Módulo `#10` (base `0x7ff7ee320000`): Carregado secundariamente pelo Windows (`lasrecomp.exe`).
2. **A Origem do Conflito**:
   - A biblioteca de jogo compilada (`extracted/lasgame.dll`) foi gerada com a tabela de importação PE apontando expressamente para `lasrecomp.exe` (definido em `lasrecomp.def` / `lasrecomp.dll.a`).
   - Ao executar o executável renomeado `PokeV-Recomp.exe`, o carregador de PE do Windows inspeciona as dependências de `lasgame.dll`. Como o processo em execução se chamava `PokeV-Recomp.exe` e não `lasrecomp.exe`, o Windows procurou no disco e encontrou o `lasrecomp.exe`, carregando-o como uma segunda DLL em tempo de execução.
   - Como `lasrecomp.exe` foi carregado como DLL e não inicializado como processo raiz, o armazenamento local de thread (TLS) da CRT de 64 bits para este módulo nunca foi alocado para a thread do jogo.
   - No momento em que `f_70082dc200` chamou `rt_dispatch` para consultar a tabela de funções indiretas (`dcache`), a instrução `mov rax, qword ptr [rdx + rax*8]` em `lasrecomp.exe+32d6` tentou acessar a tabela TLS não inicializada, causando a exceção `c0000005`.

### B. Solução Aplicada
1. **Remoção do Executável Duplicado**:
   - Removido o arquivo binário redundante `PokeV-Recomp.exe` para eliminar o conflito de importação PE.
2. **Criação de Atalho Oficial (`PokeV-Recomp.lnk`)**:
   - Criado o atalho `PokeV-Recomp.lnk` apontando diretamente para `lasrecomp.exe`.
   - Dessa forma, o Windows sempre executa o processo com o nome canônico `lasrecomp.exe`, garantindo que todas as chamadas de `lasgame.dll` se resolvam no processo primário com TLS e caches perfeitamente inicializados.
3. **Estado de Compilação Preservado**:
   - O arquivo `extracted/recomp_state.ini` encontra-se travado (`locked = 1`), permitindo abrir `lasrecomp.exe` e entrar diretamente no jogo sem qualquer recompilação.

---
---

## 14. Correção Definitiva: Unificação do Executável `PokeV-Recomp.exe` e Fix de `AcquireBleScanEvent`

### A. Diagnóstico do Crash em `AcquireBleScanEvent` (Log 30568.log)
Na versão anterior, o jogo inicializou com sucesso a interface Bluetooth (`InitializeBtmUserInterface`), mas abortou logo na sequência em `guest #2 70080b9028`:
```text
[sm] GetService bt
[sm] GetService btm:u
[am] IApplicationFunctions cmd 22 (unhandled, ok)
[kernel] abort on result 0x0 (2000-0)
  guest #2 70080b9028
```

**Engenharia Reversa da Rotina (`_ZN2nn3btm4user19AcquireBleScanEventEPNS_2os15SystemEventTypeE`):**
1. O jogo invoca o comando IPC `23` (`AcquireBleScanEvent`) em `IBtmUserCore`.
2. O assembly ARM64 do SDK checa explicitamente o valor booleano retornado no buffer IPC:
   ```arm64
   0x70080b8fe4: ldrb w8, [x29, #0x1c]   ; Lê o booleano de sucesso retornado pelo serviço
   0x70080b8fe8: cbz  w8, #0x70080b9010  ; Se for ZERO (falso), salta para o Abort em 0x70080b9028!
   ```
3. A implementação anterior retornava o handle do evento, mas deixava o buffer de dados vazio (0). O SDK interpretou que a aquisição do scanner BLE falhou e disparou o aborto intencional.

**Correção em `runtime/services/misc.c`:**
- Configurado `OUT(uint8_t, 0) = 1` e `OUT(uint32_t, 0) = 1` com `resp_size(resp, 4)` e handle de evento válido em `copy_handles`.

### B. Transição Arquitetural Completa para `PokeV-Recomp.exe`
Conforme solicitado pelo desenvolvedor, o projeto agora possui **um único executável oficial**, sem depender de atalhos ou de `lasrecomp.exe`:
1. **Makefile**:
   - `EXE := $(B)/PokeV-Recomp.exe`
   - Biblioteca de exportação gerada diretamente como `$(B)/PokeV-Recomp.dll.a`.
   - `GAMELIB_LDFLAGS` configurado para linkar diretamente contra `PokeV-Recomp.dll.a`.
2. **dist.sh**:
   - Empacotamento direto do binário `PokeV-Recomp.exe` e `PokeV-Recomp.dll.a`.
3. **gamebuild.c**:
   - `find_tools` busca primordialmente por `PokeV-Recomp.dll.a`.

---

## 15. Diagnóstico e Correção dos Artefatos Visuais Diagonais (Padrão Tweed / Herringbone nas Malhas 3D)

### A. Diagnóstico Visual e Causa Raiz
Nas capturas em execução real (cutscene da sala de aula, close-up da personagem com Pokébola e vista aérea do estádio a 60 FPS estáveis na GPU Intel Arc B580), observou-se:
1. **O céu e elementos 2D (subtítulos e HUD) renderizam limpos e sem defeitos.**
2. **Todas as superfícies 3D opacas (pele, cabelo, roupas, carteiras da sala, piso e grama do estádio) apresentavam um padrão diagonal de linhas alternadas (dither / interferência de grade).**

**Investigação da Origem:**
- **Não é falha de UV nem de vértices:** As silhuetas, contornos geométricos, perspectiva e proporções anatômicas estão 100% perfeitos (sem deformações de mesh ou spikes). As linhas mantêm a exata mesma espessura e ângulo de 45° em screen-space tanto no primeiro plano quanto no fundo.
- **Causa 1: Distorção de Aspecto Não-Uniforme (`aspect = unlocked` -> 2039x1080):**
  Como a janela rodava em 1920x1017, o cálculo `reshape = (1920 / 1017) / (16 / 9) = 1.062` gerou um alvo de renderização com largura ímpar de `2039x1080`. Como Pokémon Scarlet & Violet não possui patch de câmera widescreen no código convidado, a resolução foi escalonada de forma não-uniforme. Isso forçou cópias de profundidade escaladas via nearest-neighbor (`depth_blit_via_color`) e downscale de caixa (boxdown), gerando interferência Moiré destrutiva sobre a grade de pixels.
- **Causa 2: Desalinhamento do Guard de Auto-Sombreamento (`shadow_resolution = 2`, `shadow_sharpness = 2`):**
  O motor gráfico de Pokémon SV projeta um buffer de profundidade e um mapa de IDs de objetos em resolução nativa 1x (1024x1024). Com `shadow_sharpness = 2`, o estreitamento dos 16 taps do filtro causou dessincronização entre as coordenadas do mapa de profundidade e o mapa de IDs de objeto (conforme detalhado em `runtime/nvn/vulkan/exec.c:5580-5586`), falhando o guard nas bordas e superfícies e desenhando estrias escuras na geometria.
- **Causa 3: Injeção de GTAO (`ambient_occlusion = 1`):**
  O GTAO injetado foi desenvolvido e calibrado para a estrutura de G-Buffer de Pokémon Legends: Z-A / Link's Awakening. Em Scarlet & Violet, a amostragem desse shader injetava ruído oclusivo na imagem sem temporal blending.

### B. Correções Aplicadas
1. **Padronização para 16:9 Nativo (`aspect = original`):**
   - Configurado `.aspect = ASPECT_ORIGINAL` em `runtime/settings.c`, `tools/za/za-default.ini` e `larecomp.ini`.
   - Garante alvo estritamente 1920x1080 a 100% de escala (sem distorção horizontal de 1.062x nem Moiré em `depth_blit`).
2. **Desativação de GTAO Incompatível (`ambient_occlusion = 0`):**
   - Configurado `.gtao = 0` como padrão.
3. **Restabelecimento dos Mapas de Sombra Nativos 1x (`shadow_resolution = 1`, `shadow_sharpness = 1`):**
   - Elimina o desalinhamento de taps no guard de auto-sombreamento.
4. **Atualização da Identidade Visual no HUD:**
   - Em `runtime/ui/menu.mm` (linha 1329), a legenda do F10 foi atualizada de `"PLA Recomp 0.0.19, jogo 1.1.1"` para `"PokeV-Recomp v0.0.7, jogo 3.0.1"`.
   - Em `runtime/paths.c`, mensagens de erro de sistema foram renomeadas de `"PLA Recomp"` para `"PokeV-Recomp"`.

---

## 16. Correção das Linhas Horizontais / Interlaçadas na Intel Arc (Subgroup Size 32) e Correção da Aceleração 2x a 60 FPS (v0.0.8)

### A. Diagnóstico e Causa Raiz das Linhas Horizontais na Cena 3D (`shot_02083.png`)
1. **Diferença entre Elementos 2D e Renderização 3D**:
   Nas capturas em 1:1 (`shot_02083.png`), o mapa 2D (Rotom Map), botões, legendas e o HUD overlay do F10 renderizam de forma cristalina. No entanto, toda a cena 3D ao fundo (personagens, móveis, chão, paredes) apresenta linhas pretas/alternadas a cada 2 pixels (scanlines horizontais).
2. **Arquitetura Maxwell (GM20B) vs. Intel Arc Xe2 Battlemage (B580)**:
   Os shaders originais do Nintendo Switch foram compilados para a GPU Maxwell, que opera com **Warps rígidos de 32 threads**. Operações como derivadas quádruplas de tela (`dFdx`/`dFdy`), shuffles de warp (`subgroupShuffle`) e votações de predicados (`subgroupAll`, `subgroupAny`, `subgroupBallot`) assumem que a onda tem 32 pistas simultâneas.
   Por padrão, o driver Vulkan da Intel Arc compila shaders de fragmento em **SIMD16** (16 pistas).
   No tradutor de shaders (`runtime/nvn/maxwell/translate.c`), a lógica de emulação de warp (`w32()`) checava `gl_SubgroupSize == 32u`. Como `gl_SubgroupSize` era 16:
   - `w32()` avaliava como falso;
   - Os shuffles e derivadas que cruzavam as 32 pistas do warp Maxwell acessavam índices inválidos ou truncados no subgrupo de 16 pistas;
   - O resultado visual era a perda de coerência entre quads e linhas alternadas pretas/interlaçadas em todas as malhas 3D rasterizadas.
3. **Solução: Alinhamento Forçado SIMD32 em Shaders de Fragmento**:
   Em `runtime/nvn/vulkan/exec.c`:
   - Implementada a função `fs_subgroup32(void)`, que consulta `VkPhysicalDeviceSubgroupSizeControlProperties` do Vulkan 1.3 (`sgp.minSubgroupSize <= 32 && sgp.maxSubgroupSize >= 32 && (sgp.requiredSubgroupSizeStages & VK_SHADER_STAGE_FRAGMENT_BIT)`).
   - Inserida a estrutura `VkPipelineShaderStageRequiredSubgroupSizeCreateInfo req32_fs` em `PipeCI`, encadeada em `stages[1].pNext` com `requiredSubgroupSize = 32`.
   - Agora, a GPU Intel Arc compila todos os fragment shaders em SIMD32 nativo, combinando perfeitamente com o modelo de 32 pistas do Maxwell e eliminando os artefatos de interlaçamento.

### B. Diagnóstico e Solução da Aceleração do Jogo a 60 FPS (Velocidade 2x)
1. **Mecanismo de Delta-Time no Motor da Game Freak em Pokémon SV 3.0.1**:
   O motor gráfico de Pokémon Scarlet & Violet armazena uma tabela de tempos de quadro em nanossegundos em `.rodata` do módulo `main` (`0x7003c2fba8`):
   - Modo 0 (`0x7003c2fba8`): `0x00fe502b` = 16.666.667 ns (1/60 s, modo 60 FPS nativo)
   - Modo 1 (`0x7003c2fbb0`): `0x01fca056` = 33.333.334 ns (1/30 s, modo 30 FPS padrão)
   Na rotina do relógio principal (`f_7002b79d74`), a instrução em `0x7002b7a858` (`ldrsb w20, [x10, #0x20]`) carrega o modo desejado (`w20 = 1`).
   Em seguida:
   - `0x7002b7a874`: `add w1, w20, #1` calcula o intervalo de apresentação da janela NVN (`w1 = 1 + 1 = 2`, ou seja, 30 Hz).
   - A rotina passa `w20 = 1` como parâmetro para todos os slots de relógio do jogo (slot 0, slot 1, slot 2 e slot 3).
   Ao forçar a taxa de quadros para 60 FPS, a tela passa a renderizar 60 frames por segundo, mas como `w20` permanecia `1` (33.33 ms por frame), o jogo acumulava 60 * 33.33 ms = **2.0 segundos de tempo de jogo a cada 1.0 segundo real** (jogo em fast-forward 2x).
2. **Implementação do Hook em `tools/sv_patches.py`**:
   Implementada a função `_sv_frame_pace(gen, a)` interceptando o endereço `0x7002b7a858`:
   - Quando `rt_pla_is_60fps()` está ativado: define `c->x[20] = 0` (Modo 0) e atualiza dinamicamente a entrada 1 em `0x7003c2fbb0` para `0x00fe502bull`.
   - O intervalo de apresentação calculado em `0x7002b7a874` (`w20 + 1`) torna-se automaticamente `0 + 1 = 1` (60 FPS vsync).
   - Todos os slots de relógio do jogo recebem `w2 = 0`, lendo `16.666.667 ns` por quadro.
   - O jogo passa a rodar a 60 FPS fluidos em velocidade 1.0x normal, exatamente como o fix desenvolvido no PokeL-ARecomp.
   - Se o usuário desativar o modo 60 FPS no menu F1, o hook restabelece `w20 = 1` e `33.333.334 ns` instantaneamente.

### C. Otimização de Dispatch e TLS Baseada no PokeL-ARecomp v0.0.23
- Migração de `dcache` e `jmps` de variáveis globais `__thread` para a estrutura `Cpu` (`c->dcache` e `c->jmps` em `runtime/cpu.h`), eliminando gargalos de thread-local storage e travamentos em CPUs com 24 threads como o Intel Xeon E5-2650 v4.
- Atualização do F10 HUD overlay para `PokeV-Recomp v0.0.8, jogo 3.0.1`.

---

## 17. Correção Definitiva do Dithering/Scanlines 2x2 na Intel Arc (Alpha-to-Coverage em 1 Sample) e Relógio Mestre Dinâmico a 60 FPS (v0.0.9)

### A. Diagnóstico e Causa Raiz das Linhas Horizontais / Dithering 3D na Intel Arc B580
1. **O Mecanismo Físico do Dither na GPU Intel**:
   - Em `runtime/nvn/vulkan/exec.c`, as pipelines de renderização configuravam:
     ```c
     c->ms = (VkPipelineMultisampleStateCreateInfo){
         .rasterizationSamples = (VkSampleCountFlagBits)k->samples,
         .alphaToCoverageEnable = k->a2c
     };
     ```
   - Em Pokémon Scarlet & Violet, todos os passes de geometria 3D renderizam para G-Buffers com amostragem única (`samples = 1`), porém o estado NVN do jogo mantém `st.ms[0xC] = 1`, repassando `k->a2c = 1`.
   - Nas GPUs NVIDIA (Tegra X1 do Switch e GeForce desktop), `alphaToCoverageEnable` é completamente ignorado pelo hardware quando `rasterizationSamples == VK_SAMPLE_COUNT_1_BIT`.
   - Na **Intel Arc (Xe2 Battlemage B580)**, o driver Vulkan (`igvk64.dll`) interpreta `alphaToCoverageEnable = VK_TRUE` em alvos de 1 amostra aplicando um **dithering Bayer 2x2 em hardware (screen-door transparency)**.
   - Como os shaders de G-Buffer de Pokémon SV gravam rugosidade (roughness), especularidade ou flags de material no canal Alfa (com valores médios entre `0.2` e `0.7`), o teste de cobertura dither da GPU descartava exatamente 50% dos fragmentos em linhas ou padrão de xadrez alternado a cada 2 pixels.
   - Isso explica com 100% de exatidão por que o céu e o minimap 2D apareciam perfeitos (canal alfa = 1.0 ou a2c desligado), enquanto todos os modelos 3D (chão, personagens, montanhas, bancos) ficavam repletos de listras pretas e furos.

2. **Correção Implementada**:
   - Em `runtime/nvn/vulkan/exec.c`, `alphaToCoverageEnable` foi rigidamente condicionado a alvos multisample (`samples > 1`):
     ```c
     bool use_a2c = (k->samples > 1) ? (k->a2c != 0) : false;
     ```
   - Em alvos normais (`samples <= 1`), Alpha-to-Coverage agora permanece **estritamente desativado (`VK_FALSE`)**, e a pipeline utiliza o shader `fs` padrão em vez de `fs_late`.
   - Adicionada a variável de controle `LARECOMP_A2C` para override diagnóstico via linha de comando ou `.ini`.

### B. Relógio Mestre Dinâmico de Quadro a 60 FPS (Eliminação da Aceleração 2x)
1. **Engenharia Reversa da Rotina Mestre de Tick (`f_7002b79f68`)**:
   - Localizada a leitura direta da duração de quadro em nanossegundos em `0x7002b7a784`:
     ```arm64
     0x7002b7a780: blr x8              // Obtém ponteiro do slot de relógio 0 em x0
     0x7002b7a784: ldr d0, [x0, #8]    // Carrega duração em nanossegundos (ex: 33.333.334 ns)
     0x7002b7a794: scvtf d0, d0         // Converte int64 para double
     0x7002b7a798: fdiv d0, d0, d1      // Divide por 1.000.000.000,0 (1e9) -> segundos
     0x7002b7a79c: fcvt s0, d0          // Converte para float s0
     0x7002b7a7a0: mov x0, x20
     0x7002b7a7a4: bl #0x7000c9cdfc     // Atualiza toda a física e simulação do mundo com dt s0!
     ```
   - Mesmo com o hook de `0x7002b7a858` configurando o modo 0 e o swap interval para 1, o slot de relógio mestre continuava lendo o valor original não sincronizado caso o hook estático não sobrescrevesse `d0`.

2. **Implementação do Hook Mestre e Delta-Time Dinâmico**:
   - Portada a função `rt_pla_frame_dt_ns(slot, default_ns)` do PokeL-ARecomp (commit `194de37e11`) para `runtime/hle/framepace.c`, medindo o tempo real entre quadros via `plat_now_ns()`.
   - Adicionado o patch `_sv_frame_clock` em `tools/sv_patches.py` interceptando `0x7002b7a784`:
     ```python
     c->v[0] = (uint64_t)rt_pla_frame_dt_ns(0, orig_ns);
     ```
   - Em 60 FPS, `d0` recebe `16.666.667 ns` (16.67 ms). Dividido por 1e9, resulta em `0.016667s`, fazendo 60 quadros corresponderem a exatamente 1.0 segundo de simulação do jogo (**velocidade normal 1.0x, sem aceleração 2x**).
   - Se o framerate oscilar ou cair abaixo de 60 FPS, o delta-time dinâmico ajusta a fração de segundo em tempo real, impedindo câmera lenta ou saltos abruptos.
   - Mantido o patch `_sv_frame_pace` em `0x7002b7a858` garantindo apresentação vsync a 60 FPS (`interval = 1`).

### C. Atualizações de Versão
- Versão elevada para **`v0.0.9`** em `runtime/ui/launcher.mm` e `runtime/ui/menu.mm`.

---

## 18. Listras / Ruído em Toda a Geometria 3D: `NVNtextureView` de 16 Bytes (v0.0.10)

> **Estado: correção candidata, ainda não validada em jogo.** Esta seção também corrige o diagnóstico das seções 15 a 17:
> as listras continuaram após a v0.0.9, portanto Alpha-to-Coverage, SIMD32 e GTAO não eram a causa.

### A. Como a causa foi isolada
1. **Ampliação dos screenshots**: as listras mudam de direção a cada triângulo (seguem linhas de mesma profundidade), o
   que descarta um dither de tela (que teria o mesmo padrão fixo em toda a imagem).
2. **Teste `LARECOMP_VK_EQUAL_TOL=1`**: sem efeito, descartando z-fighting entre o pré-passe de profundidade e o passe `EQUAL`.
3. **Dump de frame (F9 + `LARECOMP_DUMP_GLSL=1`)**: o albedo do G-buffer sai limpo; a imagem só estraga no passe de
   iluminação diferida (primeiro alvo `0x3f` 1920x1080).
4. **Log do draw de iluminação**: `tex0` e `tex2` são a mesma textura `DEPTH24_STENCIL8` (`0x35`). O shader lê `tex0`,
   extrai o bit 6 e descarta o pixel se estiver ligado (leitura de stencil), mas o GLSL traduzido declarava `sampler2D`
   para os dois: o runtime entregava a profundidade onde o jogo pedia o stencil.
5. **Binário do jogo (`main+0x1664f58`)**: o jogo aloca `0x18` bytes para o objeto da view, chama
   `nvnTextureViewSetDefaults` e grava uma flag própria no offset `0x11`. Ou seja, `NVNtextureView` ocupa 16 bytes nesta
   versão da NVN (o recomp de TotK documenta o mesmo: "NVNtextureView is 16 bytes").

### B. Causa raiz
O runtime (herdado do LAS Recomp / ZA Recomp) usava um layout próprio de 28 bytes dentro da `NVNtextureView` do jogo:
- `target` (offset 16) sobrescrevia as flags do jogo em `0x10` / `0x11`;
- `swizzle` (offset 24) era gravado além dos 24 bytes alocados (corrupção de heap);
- o modo depth/stencil da view não chegava ao pool de texturas, então a view de stencil era amostrada como profundidade.

O shader de iluminação decidia manter ou descartar cada pixel pelos bits baixos do float de profundidade, gerando as
listras por triângulo em tudo que é iluminado. Céu, HUD e minimapa não passam por esse passe e ficavam limpos.

### C. Correção
- `runtime/nvn/nvn.h`: `NvnTextureView` compactada em exatamente 16 bytes (`setmask`, `ds_mode`, `target`, níveis em 1 byte;
  camadas e formato em 16 bits; `swizzle[4]`), com `_Static_assert(sizeof == 16)`.
- `runtime/nvn/objects.c`: `nvnTextureViewSet*/Get*/Compare` acessam os campos por nome em vez de offsets fixos.
- Mudança só de runtime: não altera o `GAMELIB_ID` (não força recompilar `lasgame.dll`).

### D. Pendências
- Validar em jogo (mesmo local dos screenshots). O shader de iluminação será recompilado numa variante com `usampler`.
- Verificar se o brilho verde em montanhas/árvores some junto ou é um problema separado.
- `shader_seen.txt` não grava os slots de stencil: a variante correta é traduzida no primeiro uso a cada execução.

### E. Atualizações de Versão
- Versão elevada para **`v0.0.10`** em `runtime/ui/launcher.mm` e `runtime/ui/menu.mm`.

---

## 19. Crash "no function at 7002a1fc24" (Tabela de Saltos em Função Partida) e Diagnóstico das Views (v0.0.11)

### A. Resultado da v0.0.10
- As listras **continuaram**. O layout de 16 bytes da `NVNtextureView` (seção 18) é uma correção real (o runtime escrevia
  além da alocação do jogo), mas não bastou: o draw de iluminação ainda usa a variante de shader sem `usampler` na
  textura de stencil. O motivo ainda não foi determinado.
- Apareceu um crash: `FATAL: no function at 7002a1fc24`.

### B. Crash: causa e correção (`tools/gen.py`)
- Em `0x7002a1f588` há um `switch` comum (`cmp w8, #0xa; b.hi; adrp/add; adr; ldrh; add; br x10`, 11 casos).
- A função `0x7002a1f54c` é partida pelo gerador em vários pedaços (`f_7002a1f89c`, `f_7002a1f8ec`, ...). Quatro casos
  da tabela caem fora do primeiro pedaço. O gerador rejeitava a tabela inteira quando um destino ficava fora de
  `[entry, end)`, e o fallback só alcança instruções do próprio pedaço: o caso 2 (`0x7002a1fc24`) não tinha função.
- Correção: destinos fora do pedaço, mas dentro do texto e a menos de 0x40000 do `br`, passam a ser aceitos; `scan()`
  os registra como entradas (viram funções) e o `switch` emitido faz tail call para eles.
- Validado localmente: gerador executado no `main` 3.0.1 (180.440 funções, 4.332 tabelas resolvidas), `f_7002a1fc24`
  existe e o arquivo `main_914.c` compila com o `zig cc` distribuído.
- **Efeito colateral esperado**: `gen.py` entra no `GAMELIB_ID`, então o jogo recompila o `lasgame.dll` na primeira
  abertura desta versão.

### C. Diagnóstico adicionado (listras)
- Linhas `[draw]   texN` do dump F9 agora mostram a entrada do pool por trás de cada slot: view registrada (máscara,
  formato, modo depth/stencil, target, swizzle, níveis) e o tipo de sampler com que o shader foi chaveado.
- `[nvn] pool id ...`: primeiros registros de texturas depth/stencil no pool, com e sem view.
- `[nvn] texture view depth/stencil mode ...`: primeiras chamadas de `nvnTextureViewSetDepthStencilMode` com modo != DEPTH.

### D. Atualizações de Versão
- Versão elevada para **`v0.0.11`** em `runtime/ui/launcher.mm` e `runtime/ui/menu.mm`.

---

## 20. Listras: Programa Preparado Usado em Draw que Lê Stencil (v0.0.12)

> **Estado: correção candidata, ainda não validada em jogo.**

### A. Resultado da v0.0.11
- O crash `no function at 7002a1fc24` não se repetiu no teste do usuário (jogo recompilado com o novo `gen.py`).
- O log de diagnóstico respondeu a pergunta pendente da seção 19:
  ```
  [nvn] texture view depth/stencil mode 1 (format 0x35)
  [nvn] pool id 290: depth/stencil texture 1920x1080 fmt 0x35 (ds 0) with a view: mask 0x3f fmt 0x35 ds 1 target 1 swizzle 2,3,4,5
  [draw]   tex0: ... f0x35 ... | slot 28 id 290 view mask 0x3f fmt 0x35 ds 1 ... kind 1
  [draw]   tex2: ... f0x35 ... | slot 21 id 287 no view (texture ds 0) kind 0
  ```
  Ou seja: com o layout de 16 bytes (v0.0.10) a view de stencil chega ao pool e o draw de iluminação é chaveado
  corretamente (`kind 1` no slot 28). Mesmo assim o GLSL em uso declarava `sampler2D t0`.

### B. Causa
- Os programas preparados antes do jogo (`shader_prep`, a partir de `cache/shader_seen.txt`) são traduzidos sem slots de
  stencil / inteiros: os registros não guardam essa informação.
- `prog_content_key()` (a chave com que `get_program_` procura um programa preparado) não incluía
  `fkey->stencil_slots` nem `fkey->sint_slots`, embora a chave própria do `get_program_` inclua. Resultado: todo draw
  desses shaders recebia o programa preparado, inclusive o de iluminação, que precisa de `usampler` no slot 28.

### C. Correção
- `runtime/nvn/vulkan/exec.c`: `prog_content_key()` passa a incluir `stencil_slots` e `sint_slots` do estágio de
  fragmento. Draws com view de stencil / formato inteiro deixam de casar com o programa preparado e ganham uma tradução
  própria (com `usampler` e aspecto `STENCIL`).
- Mudança só de runtime: **não** recompila o `lasgame.dll`.
- Limitação conhecida: como `shader_seen.txt` não grava esses slots, essas variantes são traduzidas no primeiro uso a
  cada execução (uma pausa curta ao entrar no mundo 3D).

### D. Atualizações de Versão
- Versão elevada para **`v0.0.12`** em `runtime/ui/launcher.mm` e `runtime/ui/menu.mm`.

---

## 21. Listras: Stencil Corrigido, Causa Restante em Aberto - Build de Diagnóstico (v0.0.13)

### A. Resultado da v0.0.12
- O draw de iluminação passou a usar a variante correta (`build/glsl/74421cd200.frag`: `usampler2D t0` + `stc(...)`), ou
  seja, as correções das seções 18 e 20 funcionaram: o stencil chega ao shader como inteiro.
- **As listras continuam**, com o mesmo aspecto: o albedo do G-buffer segue limpo e o primeiro alvo HDR (saída da
  iluminação) segue corrompido. Portanto a leitura de stencil não era a única (ou a principal) origem do ruído.
- Hipóteses ainda não verificadas: normais empacotadas (12+12 bits em 3 bytes do alvo `0x25`) gravadas ou lidas com
  formato diferente (por exemplo view sRGB), ou o alvo de material / profundidade.

### B. Diagnóstico adicionado (somente no dump F9)
- Linha `[draw]`: cada slot de cor como ligado (`slots 0:none 1:f0x38/view .../vk <formato Vulkan> pass <formato do passe>`).
- Linhas `[draw]   texN`: formato Vulkan real da imagem amostrada.
- `build/textures/in_<draw>_tex<i>.png`: bytes exatos (alfa preservado) de cada textura 2D de cor lida pelos passes de
  tela cheia que escrevem no alvo HDR (iluminação e seguintes), até 96 arquivos por execução.
- Nenhuma mudança de comportamento fora do dump; não recompila o `lasgame.dll`.

### C. Atualizações de Versão
- Versão elevada para **`v0.0.13`** em `runtime/ui/launcher.mm` e `runtime/ui/menu.mm`.

---

## 22. Listras: Cópia de Feedback do Depth Entregava Profundidade a Quem Pedia Stencil (v0.0.14)

### A. O que o dump da v0.0.13 mostrou
- Entradas da iluminação decodificadas a partir de `build/textures/in_00_tex*.png`: **normais** (12+12 bits), **material**
  e **albedo** estão limpos e contínuos. A hipótese das normais (seção 21) estava errada.
- Saída da iluminação (`pass_042.png`): em cada superfície, 2 de cada 3 pixels saem zerados, numa grade diagonal regular
  que muda de triângulo para triângulo; os pixels restantes variam muito de intensidade. É o padrão de um valor por
  pixel que decide "pular" (bit 6 do stencil) ou escolher o modelo de shading (bits 0..2) vindo de dados errados.
- O log mostra que o draw de iluminação tira um snapshot de feedback (`fbdepth_003`): a textura de depth/stencil da cena é
  ao mesmo tempo o depth attachment do passe e é amostrada duas vezes (tex0 pela view STENCIL, tex2 como profundidade).

### B. Causa
- `resolve_feedback` (`runtime/nvn/vulkan/exec.c`) cria uma única view do snapshot, sempre do aspecto **DEPTH**, e
  `texture_info` a usa para todo slot que aponta para a textura em feedback, ignorando o modo depth/stencil do slot.
- Com as correções das seções 18 e 20 o shader declara `usampler2D` para o stencil, mas recebia a view de profundidade
  (float): amostrador inteiro em formato float, indefinido em Vulkan. Na Arc B580 voltam bits do valor de profundidade,
  que formam uma grade regular ao longo do plano de cada triângulo - as listras.
- Antes da v0.0.10 esse caminho nunca era exercitado em Scarlet/Violet porque o modo STENCIL da view se perdia
  (seção 18); por isso o defeito não aparecia no código herdado.

### C. Correção
- `texture_info`: slot em modo STENCIL sobre uma textura em feedback usa a view do aspecto **STENCIL** do snapshot
  (a cópia já contém os dois aspectos).
- `draw_writes_stencil()`: draws que escrevem stencil (teste ligado, máscara de escrita, operação diferente de KEEP)
  agora invalidam o snapshot do depth, como a escrita de profundidade já fazia - senão o stencil lido poderia estar
  desatualizado.
- Somente runtime; não recompila o `lasgame.dll`.

### D. Estado
- **Validado em jogo em 11/11/2026**: as listras sumiram na v0.0.14 (Intel Arc B580). O brilho verde em
  montanhas/árvores não aparece nas capturas noturnas do teste; não foi confirmado explicitamente de dia.
- Os diagnósticos do dump F9 da v0.0.13 foram mantidos.

### E. Atualizações de Versão
- Versão elevada para **`v0.0.14`** em `runtime/ui/launcher.mm` e `runtime/ui/menu.mm`.

---

## 23. Preparação para Repositório Público, Nova Identidade Visual e Build de Linux (v0.0.15)

### A. Problemas conhecidos após a v0.0.14 (ainda sem investigação)
- Pontinhos / tracinhos brancos ao longo das bordas dos triângulos no chão e na grama.
- Cabelo do personagem e de NPCs em ciano brilhante.
- Taxa de quadros instável no mundo aberto (log da v0.0.14: média de 40 fps, 10% do tempo abaixo de 25, 209 quadros
  lentos em ~12 min, 2236 compilações de shader na sessão).

### B. Identidade visual própria de Pokémon Violet
- **Ícone**: novo desenho original gerado por `tools/sv/make_icon.py` (céu violeta, aurora, lua, montanha com cratera,
  luz ciano com anéis e hexágono, "PV" em dourado). Substitui o ícone anterior (tema de Legends Arceus) em
  `docs/icon/icon_1024.png`, `icon.ico` e `icon.icns`; `docs/icon/icon.svg` (não usado) foi removido.
- **Fundo da tela inicial**: `draw_art` em `runtime/ui/launcher.mm` deixa de desenhar a cidade noturna do Z-A e passa a
  desenhar a mesma cena do ícone. Somente formas desenhadas por código; nenhuma arte do jogo. **Não compilado
  localmente** - validado apenas por uma prévia em Python com as mesmas formas.

### C. Repositório público
- Removidas as capturas de tela herdadas (`docs/screenshots/`, `docs/ultrawide.jpg`: telas de Z-A e de Link's Awakening).
  Continuam no histórico de commits anterior.
- `README.md` / `README.pt-BR.md` reescritos: seção de estado atual e problemas conhecidos, executável correto
  (`PokeV-Recomp.exe`), teclas conferidas no código (F12 captura, F10 painel de desempenho), Scarlet marcado como não
  suportado (só o build do Violet 3.0.1 é reconhecido), aviso legal nas duas línguas, links relativos.
- Repositório renomeado para `fabioschmidt01/PokeV-Recomp`; links da tela inicial atualizados.
- **Verificação de atualização**: a tela inicial consultava as releases do ZA Recomp (`Hexveil404/PokeZ-ARecomp`) e
  ofereceria versões de outro projeto como atualização; agora consulta as releases deste repositório.

### D. Build de Linux reativado
- `build-all.yml`: job `linux` (AppImage via `tools/za/dist-linux.sh`) de volta; a release publica
  `PokeV-Recomp-linux-x86_64.AppImage` quando o job passa e sai só com o zip de Windows quando ele falha.
- **Nunca testado em hardware real neste projeto.** Pendente: teste no Linux do mantenedor.

### E. Atualizações de Versão
- Versão elevada para **`v0.0.15`** em `runtime/ui/launcher.mm` e `runtime/ui/menu.mm`.

---

## 24. Tela Inicial: Nome do Jogo, Sempre em Janela; Investigação de Novos Bugs (v0.0.16)

### A. Correções
- A tela inicial mostrava "POKÉMON LEGENDS: ARCEUS" acima de "Pronto para jogar", e as dicas de erro citavam
  Pokémon Legends Z-A / Arceus e as versões do Z-A: agora "POKÉMON VIOLET" e a versão 3.0.1.
- A tela inicial abre sempre em janela (como no PokeL-ARecomp v0.26.2): `ui_window_init` (device.c) e
  `menu_apply_window_requests` (menu.mm) não aplicam a tela cheia enquanto `g_start_screen` está ligado; o botão Jogar
  aplica a configuração de tela cheia ao entregar a janela ao jogo. Sem a tela inicial, a tela cheia vale desde o início.
- README: crédito à PKG Traduções pelo mod de tradução PT-BR, que se instala e liga/desliga pela aba Mods (não incluído).
  **Não compilado localmente.**

### B. Novos bugs relatados (11/11/2026) e o que se sabe
- **Personagem "piscando" ao andar** (vídeo): quadros consecutivos alternam a pose das pernas, e há quadros com um risco
  fino atravessando a tela (vértices fora do lugar).
- **Clarão branco na iluminação** (captura de 22:54): áreas inteiras estouradas em branco com bordas suaves.
- Hipótese principal, ainda não testada: corrida entre CPU e GPU. A sobreposição CPU/GPU está ligada (o jogo monta o
  quadro N+1 enquanto a GPU desenha o N), mas as cópias de proteção dos storage buffers (`snap_storage`) nunca foram
  feitas em Scarlet/Violet (`snap 0KB/0` em todos os logs): o anel de cópias fica depois da heap do jogo
  (`kernel_heap_size()`), e sem heap ele nunca é ativado. O Hookshot (recomp de Zelda OoT) corrigiu flashes de
  exposição com a mesma causa (NotRexed/Hookshot#645). Teste sem build: F1 > Compatibilidade > "Sobreposição CPU / GPU"
  e "Espelho do skinning" em Desligado, um de cada vez.
- **Cores**: no dump, o alvo sRGB do tonemap (`pass_105` / `pass_106`) parece lavado e a cópia final para a textura da
  janela (`pass_108`, `0x25`) parece normal; a cópia lê o alvo sRGB (decodifica) e grava sem codificar, como o hardware.
  A captura F12 da mesma sessão bate com `pass_108`. Pendente: confirmar com o usuário o que aparece na tela.
- **Jogo "lento" acima de 30 fps**: não investigado (ritmo do relógio do jogo, `[pace]`).

### C. Atualizações de Versão
- Versão elevada para **`v0.0.16`** em `runtime/ui/launcher.mm` e `runtime/ui/menu.mm`.

---

*Documento mantido em sincronia contínua pelo assistente de IA Antigravity (Google DeepMind).*
