# WMS Evidence Album — CC-03 HVR
# Human Verification Record

## 0. 文档治理

| 项目 | 内容 |
|---|---|
| Intent ID | `wd-evidence-album-cc-03` |
| CC | [CC-03 Coding Contract](./wd_evidence_album_CC-03_Coding_Contract_v1.0.0.md) |
| IHR | [CC-03 IHR](./wd_evidence_album_CC-03_IHR_v1.0.0.md) |
| ATR | [CC-03 ATR](./wd_evidence_album_CC-03_ATR_v1.0.0.md) |
| 模块 | `wd_evidence_album` |
| 环境 | Odoo 18 Community Edition；数据库 `odoo18ce` |
| 当前状态 | Passed；六个场景均由用户确认通过 |
| 验证日期 | 2026-09-28 |

浏览器观察不能替代用户人工确认。只有用户明确确认的场景才计入正式 HVR PASS。

## 1. 验证总览

| 指标 | 当前值 |
|---|---:|
| Required scenarios | 6 |
| User-confirmed PASS | 6 |
| Agent-observed | 6（辅助证据） |
| FAIL | 0 |
| BLOCKED | 0 |
| User confirmation | Confirmed by user on 2026-09-28 |

## 2. HVR 场景

### HVR-SCN-001 — 合法状态动作和按钮

- **步骤**：打开一个 Draft Album，执行 Submit Review；检查 Pending Review 状态和 Approve/Reject 按钮；批准后检查 Approved 和 Publish 按钮；发布后检查 Published。
- **通过标准**：状态按冻结路径变化，非法状态按钮不显示。
- **当前证据**：Agent 已在 Album `ALB/00009` 观察到 Draft → Pending Review，并看到 Approve/Reject。
- **证据类型**：`user-confirmed`；Agent 辅助观察

### HVR-SCN-002 — 空 Album 审核门禁

- **步骤**：对无 Page/Item 的 Pending Review Album 点击 Approve。
- **通过标准**：显示明确错误；Album 保持 Pending Review；不写入审核人、发布时间或 Token。
- **当前证据**：Album `ALB/00009` 显示 `An empty album cannot be approved or published. Add a page and media first.`。
- **证据类型**：`user-confirmed`；Agent 辅助观察

### HVR-SCN-003 — 有媒体 Album 发布

- **步骤**：为 Album 添加 Page 和合法媒体，提交审核、批准、发布。
- **通过标准**：状态为 Published；生成 Token；显示发布时间；Page/Item 保留。
- **当前证据**：Album `ALB/00010` 显示 Published、Token、Published At 和 Page `HVR Evidence`。
- **证据类型**：`user-confirmed`；Agent 辅助观察

### HVR-SCN-004 — Token 重置和撤销

- **步骤**：在 Published Album 点击 Reset Token，再点击 Revoke。
- **通过标准**：Token 发生变化；撤销后状态为 Revoked；Page、Item 和附件不被删除。
- **当前证据**：Odoo Shell 已验证 Token 变化和撤销；浏览器已观察到两个按钮。
- **证据类型**：`user-confirmed`；自动化和 Agent 辅助观察

### HVR-SCN-005 — 管理员延长有效期

- **步骤**：在 Published Album 点击 Extend Validity，输入晚于当前服务器时间的新时间并提交。
- **通过标准**：打开专用向导；延长后状态仍为 Published；Token、Published At、Reviewed By 不变。
- **当前证据**：Album `ALB/00010` 已观察到 Extend Validity 按钮和向导。
- **证据类型**：`user-confirmed`；Agent 辅助观察

### HVR-SCN-006 — 有效期和撤销边界

- **步骤**：验证过期 Album 仍为 Published；管理员延长后恢复有效；撤销后再次延长。
- **通过标准**：过期不产生新状态；已撤销 Album 不能通过延长恢复。
- **当前证据**：Odoo Shell 已验证 `is_expired()`、管理员权限和撤销后拒绝；浏览器用户确认待执行。
- **证据类型**：`user-confirmed`；自动化和 Agent 辅助观察

## 3. Agent 观察记录

| 观察 ID | 页面/对象 | 观察结果 |
|---|---|---|
| AGENT-OBS-001 | Album 28 / `ALB/00009` | Draft 提交后变为 Pending Review，显示 Approve/Reject |
| AGENT-OBS-002 | Album 28 / `ALB/00009` | 空 Album Approve 被明确拒绝，状态保持 Pending Review |
| AGENT-OBS-003 | Album 29 / `ALB/00010` | Published 页面显示 Revoke、Reset Token、Extend Validity |
| AGENT-OBS-004 | Album 29 / `ALB/00010` | Extend Validity 打开专用有效期向导 |

## 4. 用户确认登记

| 日期 | 验证者 | 确认内容 | 结果 |
|---|---|---|---|
| 2026-09-28 | 本会话用户 | “6项全部pass” | `user-confirmed`；PASS 6 |
