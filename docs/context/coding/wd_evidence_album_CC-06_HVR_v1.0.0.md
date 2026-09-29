# WMS Evidence Album — CC-06 HVR
# Human Verification Record

## 0. 文档治理

| 项目 | 内容 |
|---|---|
| Intent ID | `wd-evidence-album-cc-06` |
| 环境 | Odoo 18 Community Edition；数据库 `odoo18ce`；HTTP `127.0.0.1:8091` |
| 当前状态 | PASS |
| 日期 | 2026-09-29 |

只有证据来源为 `user-confirmed` 的场景计入正式 HVR PASS。`agent-observed` 仅表示 Agent 观察到结果，`automated` 仅表示自动化检查通过。

## 1. HVR 场景

| ID | 场景 | 预期结果 | 状态 | 证据来源 |
|---|---|---|---|---|
| HVR-CC06-001 | 业务用户打开 Draft Album Form | 显示 `Preview Portal`；可打开预览 | PASS | user-confirmed |
| HVR-CC06-002 | 审核人在 Confirmed/Pending Review 语义 Album 预览 | 可打开预览；不触发发布 | PASS | user-confirmed |
| HVR-CC06-003 | 预览页面展示 | Page、媒体网格、图片灯箱和视频展示与 Published Portal 一致 | PASS | user-confirmed |
| HVR-CC06-004 | 预览提示和限制 | 显示 `Portal Preview — Not Published`；无 Select all 和批量 Download | PASS | user-confirmed |
| HVR-CC06-005 | 返回行为 | `Back to Album` 返回当前 Album Form；状态不变 | PASS | user-confirmed |
| HVR-CC06-006 | Published/Revoked Album | 按钮隐藏；直接预览 URL 被拒绝 | PASS | user-confirmed |
| HVR-CC06-007 | Portal 客户访问后台预览 URL | 不可使用后台预览入口 | PASS | user-confirmed |
| HVR-CC06-008 | 跨客户或无记录权限 Album | 返回拒绝响应，不泄露 Album 存在性 | PASS | user-confirmed |

## 2. 证据记录规则

- 用户于 2026-09-29 明确确认“cc-06验证通过”，该确认作为本轮全部 HVR 场景的正式 `user-confirmed` 证据；
- 截图、页面地址、角色和 Album 状态如需审计，可在后续补充为附件；
- Agent 可以补充 `agent-observed` 网络或 DOM 观察，但不能替代用户确认；
- 任一 CC-04 Portal 回归失败时，CC-06 不得标记为 PASS；
- HVR 全部通过后，必须更新本文件状态和对应 FR。

## 3. 关闭条件

- HVR-CC06-001 至 HVR-CC06-008 全部获得用户确认；
- 自动化 ATR 与 CC-04 回归证据完整；
- 预览不改变 Album 状态、Token、发布时间或撤销时间；
- 上游文档门禁已按 CC-06 §1.3 补齐，或有项目负责人明确的版本化豁免记录。
