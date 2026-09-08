# cki-lite Desktop v1

Escopo fechado do `cki-lite Desktop`: um agente visual mínimo, nativo e
específico para Windows, construído em C# + Windows Forms. O produto deve
continuar sendo um operador de terminal com IA, não uma IDE, um editor de
código ou um cliente genérico de chat.

## Regras do Projeto

- Manter WinForms e dependências mínimas.
- Compilar com o `csc.exe` do .NET Framework disponível no Windows 11.
- Não exigir Visual Studio, .NET SDK, Electron, Tauri ou instaladores externos.
- Priorizar NVIDIA NIM e operações locais do Windows.
- Usar PowerShell como shell padrão; oferecer CMD como alternativa.
- Manter a execução de ferramentas sob controle explícito do usuário.
- Não adicionar arquitetura enterprise, plugins ou branding pesado.
- Preservar o binário pequeno e portátil.
- Nunca versionar chaves de API, `.env` ou artefatos de build.

## Estado Atual

Implementado no código atual:

- [x] Aplicação nativa WinForms compilável com `csc.exe`.
- [x] Chat com histórico de mensagens.
- [x] Seletor de provider e seletor de modelo visíveis.
- [x] Catálogo remoto de modelos com cache local.
- [x] Catálogo NVIDIA NIM sem filtro artificial de modelos.
- [x] NVIDIA NIM em `/models` e `/chat/completions`.
- [x] Fallback automático entre modelos disponíveis.
- [x] Providers adicionais já suportados: Groq, OpenRouter, Ollama e Gemini.
- [x] Configuração de chave fora da barra principal, em janela Config.
- [x] Base URL configurável por provider.
- [x] Carregamento de `.env` e persistência opcional de chaves.
- [x] Loop de conversação com tool calling.
- [x] Tool única `terminal` com PowerShell padrão e CMD opcional.
- [x] Execução de comandos com timeout, diretório de trabalho e captura de stdout/stderr.
- [x] Uso de `EncodedCommand` para preservar comandos PowerShell complexos.
- [x] Modos de segurança `Safe`, `Ask` e `Auto`, com `Ask` como padrão.
- [x] Dialog de confirmação antes de comandos do agente.
- [x] Aba de saída do terminal.
- [x] Trace básico integrado ao chat e checkbox `Trace`.
- [x] Persistência e exportação de sessões JSON.
- [x] Diagnóstico de DNS, TCP, TLS e HTTP.
- [x] TLS 1.2/1.3 habilitado explicitamente.
- [x] Ícone embutido no executável.
- [x] Menu de contexto para copiar, copiar tudo e limpar o chat.
- [x] Testes automatizados de core, providers, TLS e conexões reais.

## V1: Interface WinForms

### Layout principal

- [x] Reorganizar a tela no formato definitivo: sessões à esquerda, chat à
  direita, trace recolhível e entrada fixa na parte inferior.
- [ ] Manter o seletor de modelo no topo, com o provider ativo claramente
  identificado.
- [ ] Manter Config separado da barra principal.
- [ ] Exibir estado de conexão, provider e modelo atual sem depender apenas do
  texto do chat.
- [ ] Garantir layout utilizável em janela redimensionada e em resolução menor.

### Sessões

- [x] Criar painel lateral com lista de sessões salvas.
- [x] Permitir criar uma nova sessão.
- [x] Permitir selecionar e carregar uma sessão existente.
- [x] Exibir o identificador da sessão como identificação temporária.
- [x] Permitir excluir uma sessão com confirmação.
- [ ] Manter exportação JSON da sessão.

### Chat e saída

- [x] Enviar mensagens com Enter e botão Enviar.
- [x] Exibir mensagens do usuário, resposta do modelo e resultado de tool.
- [x] Copiar output e limpar histórico visível.
- [ ] Adicionar formatação visual consistente para blocos de tool, erro e
  resultado.
- [ ] Adicionar botão explícito para interromper a execução atual.
- [ ] Garantir que comandos longos e saídas grandes não congelem a interface.

### Trace do agente

- [x] Criar painel de trace separado e recolhível.
- [x] Exibir modelo utilizado e número do loop.
- [x] Exibir shell, diretório, comando, resultado e exit code no trace básico.
- [x] Permitir limpar o trace sem apagar a conversa ao iniciar uma nova sessão.
- [ ] Manter o trace opcional e desligado por padrão.

### Modos de operação

- [ ] Adicionar toggle `Chat | Agent`.
- [ ] Modo Chat: uma pergunta gera uma resposta sem execução automática de tool.
- [ ] Modo Agent: objetivo, tool, resultado e novos loops até a conclusão.
- [ ] Manter `Ask` como padrão no modo Agent.
- [ ] Definir comportamento claro quando o usuário cancela uma tool.

## V1: Agent Core

- [x] Implementar loop de conversação.
- [x] Implementar tool calling compatível com APIs OpenAI-style.
- [x] Implementar fallback automático quando o modelo falhar.
- [x] Limitar loops para evitar execução infinita.
- [x] Persistir mensagens e resultados de tools na sessão.
- [ ] Separar claramente contexto da conversa, trace e histórico persistido.
- [ ] Implementar cancelamento cooperativo do loop do agente.
- [ ] Garantir que cancelamento de uma tool seja retornado ao modelo como
  resultado estruturado.
- [ ] Validar e normalizar argumentos de tool antes da execução.
- [ ] Evitar que respostas sem tool sejam tratadas como comandos.
- [ ] Definir política para saída excessivamente grande, com truncamento seguro
  no contexto e saída completa disponível no trace.

## V1: NVIDIA NIM Client

- [x] Implementar `GET /models`.
- [x] Implementar `POST /chat/completions`.
- [x] Suportar chave via variável de ambiente e `.env`.
- [x] Suportar base URL configurável.
- [x] Habilitar TLS moderno no .NET Framework.
- [x] Exibir todos os modelos retornados pelo catálogo NIM.
- [x] Cachear catálogo localmente.
- [ ] Implementar streaming de tokens na interface.
- [ ] Tratar respostas parciais, desconexão e retry sem perder a mensagem.
- [ ] Exibir latência e status HTTP no trace.
- [ ] Cobrir streaming com testes locais determinísticos.

## V1: Windows Tools

### Tool única

Manter uma única tool pública para o modelo:

```text
terminal(command, cwd, timeout, shell)
```

- [x] PowerShell como shell padrão.
- [x] CMD como shell alternativo.
- [x] `cwd` opcional.
- [x] Timeout configurável e limitado.
- [x] Captura separada de stdout e stderr.
- [x] Exit code estruturado.
- [x] Limpeza de sequências ANSI.
- [ ] Cancelamento real do processo em execução.
- [ ] Encerrar também processos filhos quando possível.
- [ ] Exibir processo e tempo de execução no trace.

### Segurança

- [x] Modo `Safe`: bloqueia execução do agente.
- [x] Modo `Ask`: pede confirmação antes de executar.
- [x] Modo `Auto`: executa sem confirmação explícita.
- [x] `Ask` como padrão.
- [x] Mostrar comando completo antes da confirmação.
- [ ] Detectar comandos potencialmente destrutivos e destacá-los na confirmação.
- [ ] Mostrar aviso específico para remoção, formatação, alteração de serviços,
  firewall, registro e operações administrativas.
- [ ] Permitir cancelar a execução sem marcar a sessão como concluída.
- [ ] Não executar comandos fora do contrato da tool.

### Comandos suportados pelo uso natural

Validar manualmente, sem criar wrappers específicos para cada ferramenta:

- PowerShell e CMD.
- `winget`, `git`, `ssh`, `wsl`, `docker`.
- `sc.exe`, `netsh`, `Get-Service`, `Get-Process` e `Get-WinEvent`.
- Diagnóstico de disco, memória, processos, serviços, rede e Docker.

## V1: Organização do Código

O código pode continuar compilando como um executável único, mas deve ser
organizado em arquivos por responsabilidade, sem alterar o modelo de build:

```text
cki-lite-desktop/
├── Program.cs
├── MainForm.cs
├── MainForm.Designer.cs       # somente se não aumentar a complexidade
├── Services/
│   ├── AgentService.cs
│   ├── NimClient.cs
│   ├── ShellService.cs
│   ├── SessionService.cs
│   └── ModelService.cs
├── Models/
│   ├── ChatMessage.cs
│   ├── ToolCall.cs
│   ├── NimModel.cs
│   └── Session.cs
└── Properties/
```

- [ ] Separar UI, core, serviços e modelos do arquivo monolítico atual.
- [ ] Manter namespaces simples e dependências unidirecionais.
- [ ] Evitar abstrações genéricas sem uso real.
- [ ] Atualizar `build.bat`, `build.ps1` e `test.bat` para compilar os arquivos
  separados.
- [ ] Manter compatibilidade com o compilador C# disponível no ambiente alvo.
- [ ] Não introduzir `System.Text.Json` se isso quebrar a compilação sem SDK;
  usar o parser atual ou uma alternativa compatível com o runtime suportado.

## V1: Testes e Qualidade

- [x] Testar parser e serializer JSON.
- [x] Testar providers e carregamento de `.env`.
- [x] Testar execução de shell e limpeza ANSI.
- [x] Testar TLS 1.2/1.3.
- [x] Testar DNS, TCP, TLS e HTTP.
- [x] Testar `GET /models` real em providers disponíveis.
- [ ] Testar carregamento, criação, troca, exclusão e exportação de sessões.
- [ ] Testar modos Safe/Ask/Auto sem exibir diálogos em testes automatizados.
- [ ] Testar cancelamento de processo e timeout.
- [ ] Testar redimensionamento e controles essenciais da UI.
- [ ] Testar streaming e recuperação após erro de rede.
- [ ] Executar build limpo sem Visual Studio ou .NET SDK.
- [ ] Confirmar que `.env`, chaves, sessões privadas e binários não entram no Git.

## Fora Da V1

Os itens abaixo não fazem parte deste projeto fechado:

- MCP.
- Editor de código.
- Diff avançado.
- Interface Git.
- Browser embutido.
- Plugins.
- Marketplace ou extensões.
- Sistema de agentes múltiplos.
- Roteamento enterprise ou servidores remotos.
- Banco de dados.
- Electron ou Tauri.
- Suporte multiplataforma no Desktop.
- Branding pesado Chronokairo.
- Wrappers dedicados para cada comando do Windows.

## Critérios De Aceite Da V1

A v1 estará concluída quando todos os critérios abaixo forem verdadeiros:

- [ ] O app compila em uma instalação limpa do Windows 11 usando apenas os
  scripts do projeto e o `csc.exe` disponível.
- [ ] O app inicia sem instalação de runtime adicional além do suporte esperado
  do Windows/.NET Framework.
- [ ] O usuário consegue configurar a chave, carregar o catálogo NIM e escolher
  qualquer modelo retornado pelo provider.
- [ ] O usuário consegue conversar em modo Chat sem executar comandos.
- [ ] O usuário consegue operar em modo Agent com PowerShell e CMD.
- [ ] Nenhum comando do agente é executado sem respeitar o modo Safe/Ask/Auto.
- [ ] O usuário consegue cancelar uma execução em andamento.
- [ ] O usuário consegue visualizar trace, stdout, stderr, exit code e duração.
- [ ] O usuário consegue criar, trocar, carregar, excluir e exportar sessões.
- [ ] O streaming aparece progressivamente no chat e sobrevive a erros
  recuperáveis de rede.
- [ ] Os testes automatizados passam sem depender de uma API externa; os testes
  de conexão reais permanecem separados e opcionais.
- [ ] Nenhuma chave de API é gravada no código, no histórico ou no repositório.
- [ ] O produto continua pequeno, nativo e focado em operar o Windows.

## Release Checklist

- [ ] Atualizar README com o layout final, modos Chat/Agent, sessões, trace,
  cancelamento e segurança.
- [ ] Confirmar `.gitignore` para `.env`, `bin/`, sessões e artefatos temporários.
- [ ] Gerar o ícone final e embuti-lo no executável.
- [ ] Executar build de release.
- [ ] Executar testes automatizados.
- [ ] Fazer teste manual do fluxo NIM completo.
- [ ] Fazer teste manual de comando seguro, perigoso, cancelado e com timeout.
- [ ] Verificar que o executável inicia e encerra sem processos órfãos.
- [ ] Revisar tamanho do binário e dependências distribuídas.
- [ ] Documentar limitações conhecidas da primeira versão.
