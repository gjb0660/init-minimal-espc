# Initialize Minimal ESPC Baseline

Bootstrap a repository with a minimal ESPC baseline.

`init-minimal-espc` 是一个面向新仓库的 bootstrap skill，用于初始化一套最小、可执行的 ESPC baseline：

`ESPC` 由 **Explorer → Spec → Plan → Code** 四个 Agent 核心概念组成。

它不试图提供完整的 process framework，而是提供一个足够稳定的起点，使仓库从一开始就具备：

- one feature → one spec
- 明确的 goal、scope、acceptance
- 稳定的 source of truth
- 最小治理结构

## Two-Layer Architecture

1. 元技能层（Meta-Skill Layer）：负责“如何生成”
2. 项目规则层（Project-Rules Layer）：负责“如何执行”

## What this repository does

这个仓库包含：

- `docs/` — supporting documentation，一些设计原则、结构说明等
- `references/seed_repo/` — seed baseline bundle，一套模板结构
- `scripts/` — baseline generator implementation，一个底层执行器
- `SKILL.md` — agent skill definition，技能的主体说明

它的作用是在项目初始阶段建立最小的 spec-driven workflow，并为后续 agent execution 提供稳定结构。

## When to use it

适用场景包括：

- 初始化一个新的 repository
- 为已有小型项目建立基础治理结构
- 为 AI agents 提供统一的 execution model
- 收敛零散的 notes、plans 和 instructions

## How to use it

`init-minimal-espc` 使用方式，是将其作为一个 skill 交给 Agent 执行。

> 建议 `plan mode` 计划模式，这将允许 Agent 在执行前先发起提问，再思考与规划。

在执行过程中，通常会先明确三个维度：

- **Goal**：初始化之后希望立即具备的能力
- **Scope**：目标 repository path，以及是否覆盖已有内容
- **Acceptance**：初始化完成后的验证条件

这些信息用于确定初始化的边界与结果。

### 生成结构

执行该 skill 后，会生成一套结构：

```text
<project-root>/
├── AGENTS.md                       # Agents 行为规范
├── .agents/skills/
│   ├── minimal-espc/               # 设计+实现 skill
│   └── converge-commit/            # 审查+提交 skill
├── .github/
│   ├── copilot-instructions.md     # Repository 规范
│   └── instructions/               # Repository Domain 规范
└── specs/
    ├── features/                   # 执行单元（SSOT）
    ├── contracts/                  # 稳定约束与边界
    ├── knowledge/                  # 可复用事实与原则
    └── index.md                    # specs 自描述入口
```

生成内容以结构为主，不包含具体项目知识。
`knowledge` 部分由后续的研究与整理补充完成。

### 技能说明

初始化完成后，有两大技能可供 Agent 使用：

1. 使用 `minimal-espc` 技能 Agent 可以：
    - 发起提案，创建新的 feature
    - 变更需求，修改已有的 feature
    - 制定规则，形成新的 contract
    - 调研问题，收集并整理成新的 knowledge
    - spec-code对齐，SSOT 原则扫描偏离，并进行修复

    > 这是一个发散性的操作，建议 `plan mode` 计划模式，
    > 让 Agent 在执行前先发起提问，澄清需求与边界

2. 使用 `converge-commit` 技能 Agent 可以：
    - 检查代码和设计，消除坏味道，消除冗余，遵循 SSOT 原则
    - 重构代码和设计，收敛到最小可持续方案
    - 审查暂存修改并提交

    > 这是一个收敛性的技能，可以不用 `plan mode` 计划模式

3. 使用 `decision-import` 技能 Agent 可以：
    - 从暂存区的修改中提取决策证据，更新 spec

> 显式调用 skill 通常会优于自动触发；
> 借助 prompts/agents.md/skills 三者的协同作用，有助于 Agent 集中注意力。

### 示例1：使用 `minimal-espc` 发起提案

新项目初始化完成后，可以使用 `minimal-espc` 技能向 Agent 发起第一个 feature 的执行请求。
提示词示例如下：

```text
/minimal-espc 发起一个 bootstrap 的提案：

基于 STFT 实现一个简单的麦克风阵列波束形成器，输入是多通道音频数据，输出是单通道增强后的音频数据。

开启第一性原理思考，应用奥卡姆剃刀的方式，充分调研，充分设计后再实现，用苏格拉底提问，挑战我的底层假设
现在，通过提问一起讨论下
```

### 示例2：使用 `minimal-espc` 调研

遇到一个复杂问题需要调研时，可以使用 `minimal-espc` 技能向 Agent 发起调研的提案：
提示词示例如下：

```text
/minimal-espc 调研 GCC-PHAT 算法的原理和实现细节, 以及在麦克风阵列波束形成中的应用
整理成一个 knowledge，放在 specs/knowledge/ 下
```

```text
/minimal-espc 分析 xxx 这个项目的源码，有关 DOA 的设计与实现细节
整理成一个 knowledge，放在 specs/knowledge/references/ 下
```

### 示例3：使用 `converge-commit` 收敛提交

完成设计和开发后，可以使用 `converge-commit` 技能做一个提交前的审查：
提示词示例如下：

```text
/converge-commit 使用第一性原理审查一遍暂存的修改，收掉坏味道的代码，
然后使用奥卡姆剃刀消除冗余代码，收敛到最小可持续的方案。
完成并门禁检查通过后，做一次原子提交
```

## Core design

Minimal ESPC 将 spec 作为 execution center。

受到第一性原则和奥卡姆剃刀的启发，
每个 feature 随时间收敛到一个持续演化的 spec，
spec 中包含 facts、decisions 与 execution state。

在此基础上：

- contracts 表达稳定边界
- knowledge 沉淀可复用理解
- instructions 引用明确的 source of truth

这种结构用于保持 design、execution 与 governance 的一致性，同时避免平行文档持续增长。

该项目保持一个最小化取向：

- first-principles over ceremony：第一性原则优先于形式主义
- Occam's razor over framework inflation：奥卡姆剃刀优先于框架膨胀
- structure first, content second：先建立结构，再填充内容
- explicit decisions over implicit conventions：明确决策优先于隐式约定

## Links

- [SKILL.md](./SKILL.md) 定义了 skill 的目标、输入输出、执行步骤等细节
- [docs/minimal-espc.md](./docs/minimal-espc.md) 提供了对 Minimal ESPC 设计原则与结构的详细说明
