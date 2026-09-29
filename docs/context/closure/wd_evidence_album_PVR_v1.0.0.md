# WMS Evidence Album — Project Verification Record
# 项目验证记录 PVR

## 0. 文档治理

| 项目 | 内容 |
|---|---|
| PVR ID | `PVR-20260929-001` |
| 项目 | `wd_evidence_album` |
| PVR 版本 | v1.0.0 |
| 状态 | Frozen Evidence Record |
| 日期 | 2026-09-29 |
| 上游工作流 | Project Closure Workflow Extension v1.0.0 Frozen |

本 PVR 记录项目级验证事实，不作 Project Closure 判断；Closure 判断见 [PCR](./wd_evidence_album_PCR_v1.0.0.md)。

## 1. Final Project Baselines

### 1.1 Final Project Authority Baseline

| Authority | Final Version | 状态 |
|---|---|---|
| SRS | v1.0.0 Frozen | 当前项目实际基线 |
| DDD | N/A | 项目未提供独立 DDD |
| TDD | v1.0.0 Frozen | 当前项目实际基线 |

组织工作流示例要求更高版本的最终 Authority Baseline；本项目当前没有 SRS v1.1 或 TDD v1.2 文件，因此不虚构版本，作为 PCR 的 Baseline Governance Gap 记录。

### 1.2 Final Project Code Baseline

| 字段 | 值 |
|---|---|
| Repository | `/Users/lijianqiang/Documents/odoo18_album` |
| Branch | `main` |
| Commit | `7376344` |
| Commit message | `implement wd_evidence_album v1.0 release baseline` |
| Module version | `18.0.1.0.0` |
| Odoo | 18 Community Edition |
| Database | `odoo18ce` |
| Python | `/Users/lijianqiang/Documents/odoo18_album/venv/bin/python` |
| HTTP | `127.0.0.1:8091` |

## 2. Verification Snapshot

| 指标 | 结果 |
|---|---|
| 纳入 Closure 的 Requirement Groups | SRS §4–§15、§18 |
| MAPPED | CC-01、CC-02、CC-03、CC-04、CC-06、CC-07 覆盖的范围 |
| PARTIALLY MAPPED | SRS §16/§18 中原 CC-05 编号仍需与 CC-07 迁移说明交叉引用 |
| UNMAPPED | CC-06 Portal Preview 的正式 SRS BR 尚未补入 SRS |
| VERIFIED | CC-02、CC-03、CC-04、CC-05/CC-07、CC-06 已有 FR/HVR 证据的范围 |
| NOT VERIFIED | CC-01 正式 HVR 身份/Run、项目最终基线回归的未覆盖范围 |
| EVIDENCE MISSING | CC-01 FR Closure、部分 TDD-Q-008 运行时矩阵 |
| Open Findings | PVR-FIND-001 至 PVR-FIND-004 |
| Verification Evidence Complete | No |

## 3. Project Coverage Matrix

| SRS 范围 | Coding Contract / FR | Mapping Status | Project Evidence | Verification Status | 说明 |
|---|---|---|---|---|---|
| §4–§5 数据模型、来源配置 | CC-01 / CC-02；CC-01 FR BLOCKED、CC-02 FR | PARTIALLY MAPPED | CC-01/02 IHR、ATR、HVR | NOT VERIFIED | CC-01 正式 HVR 身份证据不足 |
| §6 Page 标题/描述与媒体采集 | CC-02 / CC-02 FR | MAPPED | CC-02 ATR/HVR/FR | VERIFIED | TDD-Q-008 仍有证据补强项 |
| §7 审核、发布、撤销、有效期 | CC-03 / CC-03 FR | MAPPED | CC-03 ATR/HVR/FR | VERIFIED | 专用 TransactionCase 仍属测试残余风险 |
| §8.1–§8.7 Portal 查看器与单文件媒体 | CC-04 / CC-04 FR | MAPPED | CC-04 ATR/HVR/FR | VERIFIED | CC-04 回归由 CC-07 HVR 继续覆盖 |
| §8.8 多选 ZIP 下载 | CC-07 / CC-07 FR | MAPPED | CC-07 ATR/HVR/FR | VERIFIED | 原 CC-05 已迁移为 CC-07 |
| CC-06 发布前 Portal 预览 | CC-06 / CC-06 FR | PARTIALLY MAPPED | CC-06 ATR/HVR/FR | VERIFIED WITH GAP | 正式 SRS BR 和 Implementation Plan 历史引用仍需补齐 |
| §9–§15 权限、状态、路由、非功能和业务规则 | CC-01–CC-07 | PARTIALLY MAPPED | 各 CC FR、定向回归 | NOT VERIFIED | 尚未在最终基线上完成项目级全面覆盖判断 |

## 4. Final Regression Assessment

### 4.1 强制问题回答

- 存在可执行自动化测试：是；
- 多轮 CC 存在跨变更回归风险：是，尤其是 CC-04/CC-06/CC-07 Portal Viewer、媒体 Controller 和授权链；
- 已在最终代码 Commit `7376344` 上执行定向回归：是；
- 是否保留历史 ATR：是，仅作为各 CC 的辅助证据，不替代最终基线回归；
- 是否执行完整项目级 Final Baseline Regression：否；
- 不执行完整回归的理由：当前项目没有统一的全量测试套件，且 CC-01 FR/Authority Baseline 仍有治理缺口；
- 替代验证：Python/JavaScript/XML 静态检查、Odoo 模块升级、CC-01/02/03/06/07 定向测试及用户 HVR；
- 残余风险：项目级全覆盖和最终 Authority Baseline 一致性尚未证明。

### 4.2 PVR-ARUN-001

| 字段 | 值 |
|---|---|
| Final Code Baseline | `7376344` |
| Environment | Odoo 18 CE、`odoo18ce`、备用 HTTP 端口 8092 |
| Scope | Python compile、JS syntax、XML parse、`git diff --check`、CC-07/CC-06/CC-01/CC-02/CC-03 定向测试 |
| Result | PASS |
| Evidence | `PVR-EVD-001` |

执行命令包括：

```text
./venv/bin/python -m py_compile ...
node --check mymodules/wd_evidence_album/static/src/js/evidence_album_viewer.js
Odoo -u wd_evidence_album --test-enable --test-tags ... --stop-after-init
```

## 5. E2E / UAT Evidence

| Evidence | 范围 | 结果 |
|---|---|---|
| CC-01 HVR | 后台模型、权限、排序、附件生命周期 | 6 项历史通过，但正式 HVR 身份记录不完整 |
| CC-02 HVR | 来源采集、标题描述映射、上传和媒体校验 | 6 项用户确认通过 |
| CC-03 HVR | 审核、发布、Token、撤销、有效期 | 6 项用户确认通过 |
| CC-04 HVR | Portal 列表、Viewer、媒体预览和下载 | 已有用户确认记录 |
| CC-06 HVR | 发布前 Portal 预览 | 全部用户确认通过 |
| CC-07 HVR | 当前 Page 多选、ZIP、拒绝和 CC-04 回归 | 全部用户确认通过 |

## 6. Outstanding Findings

| ID | 事实 | 影响 |
|---|---|---|
| PVR-FIND-001 | CC-01 HVR 文档仍标记正式人类验证身份/Run 不完整 | CC-01 FR 不能进入无条件 SATISFIED |
| PVR-FIND-002 | SRS 尚无正式 Portal Preview BR | CC-06 追溯存在上游缺口 |
| PVR-FIND-003 | 当前工作流要求的更高版本 Final Authority 文件不存在 | PCR 无法确认最终权威版本一致性 |
| PVR-FIND-004 | Final Baseline 只有定向回归，未形成统一项目级测试套件 | 存在项目级残余回归风险 |

PVR 不对以上 Findings 作 Closure 判定。
