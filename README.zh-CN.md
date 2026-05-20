# 实用 Agent Skills

[English](README.md) | [简体中文](README.zh-CN.md)

这是一个本地优先的 agent skills 集合，面向真实工作流中“普通 prompt 不够稳定”的实用问题：财务控制、客户升级交接、离职访问撤销、供应商银行信息变更、合同续约、SaaS 许可证 rightsizing、安全问卷、CI 故障取证、CSV 导入检查、Feature Flag 清理，以及 AI 工作产出审查。

每个 skill 的目标是：

- **解决真实工作问题**：优先选择高频、会造成时间/金钱/质量/风险损失的场景。
- **比普通 prompt 更可靠**：内置规则、模板、fixture、脚本、分类体系或安全边界。
- **方便多运行时使用**：支持 Codex/OpenAI 风格 metadata、Claude Code mirror，以及 OpenClaw 安装说明。
- **适合开源审查**：本地验证不需要密钥，没有隐藏遥测，也不会默认调用外部 SaaS/API。

## Skills

| Skill | 适合谁 | 输出什么 | 验证状态 |
|---|---|---|---|
| [`重复付款预检查`](ap-duplicate-payment-preflight/SKILL.md) | 财务、AP、Ops 在付款前审核付款批次。 | 重复付款风险报告，标记 hold/review 行。 | 已接入 `quick_validate.py` fixture。 |
| [`拒付证据包整理`](chargeback-evidence-pack/SKILL.md) | 商家、电商、支付运营处理拒付/争议。 | 按 reason code 组织的证据清单与挑战建议。 | 已接入 `quick_validate.py` fixture。 |
| [`合同续约风险预检查`](contract-renewal-risk-preflight/SKILL.md) | 采购、财务、IT、Ops 在供应商续约前检查自动续约和通知窗口。 | 自动续约风险报告、通知截止日、owner 行动计划。 | 已接入 `quick_validate.py` fixture。 |
| [`客户升级时间线重建`](customer-escalation-timeline/SKILL.md) | Support、CS、CX、工程升级团队在关闭升级或高层 review 前重建客户交接上下文。 | 升级时间线、交接包、owner/SLA/客户更新 closure gate。 | 已接入 `quick_validate.py` fixture。 |
| [`CSV 导入预检查`](csv-import-preflight/SKILL.md) | Ops/CS/内部工具团队导入 CSV/TSV 前检查风险。 | Block/review/pass 导入报告和风险行。 | 已接入 `quick_validate.py` fixture。 |
| [`员工离职访问预检查`](employee-offboarding-access-preflight/SKILL.md) | IT、安全、HR Ops、MSP、合规 owner 在离职或转岗访问 review 关闭前检查残留权限。 | 残留账号、直登 SaaS、session/MFA、密钥、群组、设备的 closure-gate 报告。 | 已接入 `quick_validate.py` fixture。 |
| [`Feature Flag 债务审计`](feature-flag-debt-audit/SKILL.md) | 工程/平台团队清理陈旧 feature flags。 | 清理候选、保护性 guardrails、代码引用、ticket。 | 已接入 `quick_validate.py` fixture。 |
| [`不稳定 CI 取证`](flaky-ci-forensics/SKILL.md) | 工程团队分析不稳定 CI/测试失败。 | 失败聚类、flake 置信度、成本估算、修复计划。 | 已接入 `quick_validate.py` fixture。 |
| [`SaaS 许可证 Rightsize`](saas-license-rightsize/SKILL.md) | IT、财务、采购、MSP、Ops 在续约或预算审查前检查 SaaS 席位。 | reclaim/downgrade/重复账号/离职员工/stale admin 行动计划和节省估算。 | 已接入 `quick_validate.py` fixture。 |
| [`安全问卷分流`](security-questionnaire-triage/SKILL.md) | B2B 团队回答安全问卷。 | 基于证据的回答草稿和升级标签。 | 已接入 `quick_validate.py` fixture。 |
| [`供应商银行信息变更预检查`](vendor-bank-change-preflight/SKILL.md) | 财务、AP、会计、采购在付款前审核供应商银行信息变更。 | 付款重定向风险报告，标记 hold/verify/release 行。 | 已接入 `quick_validate.py` fixture。 |
| [`Workslop 审查`](workslop-review/SKILL.md) | 管理者和 IC 审查含糊的 AI 辅助工作产出。 | Rubric 审查和更清晰的改写版本。 | Prompt/workflow skill，无脚本依赖。 |

## 独立仓库

这些重点 skill 有各自面向具体用户的独立仓库：

- [`ap-duplicate-payment-preflight`](https://github.com/oceanfsdfsvfdsvs/ap-duplicate-payment-preflight)：在付款前发现重复供应商付款。
- [`chargeback-evidence-pack`](https://github.com/oceanfsdfsvfdsvs/chargeback-evidence-pack)：整理商家拒付/争议证据包。
- [`flaky-ci-forensics`](https://github.com/oceanfsdfsvfdsvs/flaky-ci-forensics)：把 flaky CI 失败变成可执行的排查报告。
- [`feature-flag-debt-audit`](https://github.com/oceanfsdfsvfdsvs/feature-flag-debt-audit)：清理陈旧 feature flags，同时避免误删 kill switch 和关键 guardrails。

## 快速开始

克隆或复制仓库后，运行本地 fixture 验证：

```bash
python3 quick_validate.py
```

在 agent 中使用某个 skill 时，指向对应目录的 `SKILL.md`：

```text
Use the flaky-ci-forensics skill on this JUnit XML, CI log, and history CSV.
```

对于带脚本的 skill，可以先运行本地工具，再把输出交给 agent：

```bash
python3 ap-duplicate-payment-preflight/scripts/ap_duplicate_payment_preflight.py \
  --payments ap-duplicate-payment-preflight/scripts/fixtures/ap_payments.csv
```

## 运行时安装

### Codex / OpenAI 风格 Agents

把任意 skill 目录复制到配置好的 skills 目录，或在支持本地 skill 的 agent 中直接引用仓库路径。每个 skill 都包含：

- `SKILL.md`
- `agents/openai.yaml`
- 可选的 `scripts/`、`templates/`、`references/`、`examples/` 和运行时说明

### Claude Code

Claude Code 可以使用 `.claude/skills/<skill-name>/SKILL.md` 下的 mirror 文件。安装全部 mirror：

```bash
mkdir -p ~/.claude/skills
cp -R .claude/skills/* ~/.claude/skills/
```

如果 skill 依赖脚本，请保留完整仓库，这样相对路径能正常解析。

### OpenClaw

把 skill 目录复制到 OpenClaw workspace 的 skills 目录。每个 skill 都带有 `openclaw/README.md` 安装说明。

如果你的 OpenClaw CLI 支持，可以运行：

```bash
openclaw skills check <skill-name>
```

如果当前 OpenClaw 版本要求 registry URL 或 ClawHub package，可以先把本仓库作为源码使用。

## 兼容矩阵

| Skill | Codex/OpenAI | Claude Code | OpenClaw | 本地脚本 |
|---|---|---|---|---|
| 重复付款预检查 | `SKILL.md`, `agents/openai.yaml` | 已提供 mirror | 已提供安装说明 | 有 |
| 拒付证据包整理 | `SKILL.md`, `agents/openai.yaml` | 已提供 mirror | 已提供安装说明 | 有 |
| 合同续约风险预检查 | `SKILL.md`, `agents/openai.yaml` | 已提供 mirror | 已提供安装说明 | 有 |
| 客户升级时间线重建 | `SKILL.md`, `agents/openai.yaml` | 已提供 mirror | 已提供安装说明 | 有 |
| CSV 导入预检查 | `SKILL.md`, `agents/openai.yaml` | 已提供 mirror | 已提供安装说明 | 有 |
| 员工离职访问预检查 | `SKILL.md`, `agents/openai.yaml` | 已提供 mirror | 已提供安装说明 | 有 |
| Feature Flag 债务审计 | `SKILL.md`, `agents/openai.yaml` | 已提供 mirror | 已提供安装说明 | 有 |
| 不稳定 CI 取证 | `SKILL.md`, `agents/openai.yaml` | 已提供 mirror | 已提供安装说明 | 有 |
| SaaS 许可证 Rightsize | `SKILL.md`, `agents/openai.yaml` | 已提供 mirror | 已提供安装说明 | 有 |
| 安全问卷分流 | `SKILL.md`, `agents/openai.yaml` | 已提供 mirror | 已提供安装说明 | 有 |
| 供应商银行信息变更预检查 | `SKILL.md`, `agents/openai.yaml` | 已提供 mirror | 已提供安装说明 | 有 |
| Workslop 审查 | `SKILL.md`, `agents/openai.yaml` | 已提供 mirror | 已提供安装说明 | 无，prompt workflow |

## 验证

运行全部本地 smoke checks：

```bash
python3 quick_validate.py
```

这些检查只使用本地 fixtures，不需要凭据或网络访问。

## 安全边界

- 本地验证不需要 secrets。
- 不要把 token、private key、`.env`、完整银行卡数据、原始客户数据或私有审计证据粘贴进 prompt 或 fixtures。
- 脚本只读取显式传入的路径；只有在调用者传入 output path 时才写报告。
- Skills 不会隐藏调用网络，也不会修改真实 SaaS、会计系统或 CI 系统。
