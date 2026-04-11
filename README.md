# 🚀 Minimal ESPC

> A spec-driven execution model for AI-native development.

Minimal ESPC 是一个面向 AI 协作开发的规格驱动执行模型。
它用一份持续演进的 Spec 作为单一事实来源（SSOT），把探索、决策、实现与验证收敛到同一条闭环里。

---

## 🧠 What is ESPC?

**ESPC (Explorer → Spec → Plan → Code)** 是一个用于软件构建的闭环系统。
核心思想不是“多文档管理”，而是“单规格驱动”。

> **One feature → one spec → one source of truth**

---

## 🔁 Core Model

每个 Spec 都是一个自包含执行循环：

```text
Goal
→ Facts
→ Decision
→ Acceptance
→ Plan
→ Progress
→ (feedback → Facts)
```

- 不是线性流程
- 不是阶段切换
- 而是持续收敛系统

---

## 📁 Project Structure

```text
specs/
├── features/    # 执行单元（SSOT）
├── contracts/   # 不可破坏约束
├── knowledge/   # 可复用事实与原则
├── ideas.md     # 原始输入
└── index.md     # 导航索引
```

---

## 🧱 Three Core Layers

### 1. Features → Execution

- 定义系统“做什么”
- 一个 Feature 对应一个 Spec 文件
- 执行状态只存在于 Feature Spec

### 2. Contracts → Constraints

- 定义“不能破坏什么”
- 与 Feature 解耦
- 稳定、可复用、可审计

### 3. Knowledge → Understanding

- 定义“为什么这样设计”
- 记录事实、原理、外部系统认知
- 只读，不承载执行状态

---

## 📄 Spec File (Single Source of Truth)

每个 Feature Spec 都是活文档：

```md
## Goal
## Non-Goals

## Facts
## Decision

## Acceptance
## Plan

## Progress
## Todo
```

Spec 同时承载：设计、计划、执行状态与变更记录。

---

## ⚙️ How It Works

### Rules

- 不存在 Spec 就不进入编码
- 单 Feature 不拆分为多个并行 Spec
- 不创建平行真源（parallel sources of truth）

### Execution Flow

1. **Explorer**：建立事实
2. **Spec**：明确目标与决策
3. **Plan**：收敛最小执行路径
4. **Code**：实现并同步更新 Spec

### Critical Constraint

> Spec 与代码必须原子同步演进（atomic sync）

---

## ⚖️ Separation Principles

为避免语义污染，必须保持边界：

- Facts ≠ Decision
- Plan ≠ Todo
- Goal ≠ Acceptance

同时保持层级职责分离：

- Feature = execution
- Contract = constraint
- Knowledge = reasoning

---

## 🚫 Anti-Patterns

- 一个 Feature 维护多份执行文档
- 把假设当作事实写入 Facts
- 混合当前 Plan 与未来想法
- 在 Knowledge 中写执行进度
- 在 Contracts 中编码 Feature 细节

---

## 🧠 Mental Model

```text
Knowledge → defines reality
Contract  → defines boundaries
Feature   → drives execution
```

---

## 💡 Why ESPC?

ESPC 为 AI Agent 场景而设计：

- 降低上下文碎片化
- 防止 Spec 与代码漂移
- 支持增量、可验证执行
- 强制显式推理与可追溯决策

> ESPC 不是流程模板，而是决策收敛系统。

---

## 📌 One-Sentence Summary

> 通过持续更新一份反映事实、决策与执行状态的 Spec 来构建软件。
