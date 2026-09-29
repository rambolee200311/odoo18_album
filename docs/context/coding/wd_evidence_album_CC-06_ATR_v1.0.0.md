# WMS Evidence Album — CC-06 ATR
# Automated Test Record

## 0. 文档治理

| 项目 | 内容 |
|---|---|
| Intent ID | `wd-evidence-album-cc-06` |
| 环境 | Odoo 18 Community Edition；数据库 `odoo18ce`；Python venv `venv` |
| 当前状态 | PASS（定向自动化通过；浏览器验证由用户确认通过） |
| 日期 | 2026-09-29 |

## 1. 自动化运行记录

| 运行 | 命令/范围 | 结果 |
|---|---|---|
| CC06-ATR-001 | `python -m py_compile`：Preview Controller、Album Model | PASS |
| CC06-ATR-002 | `node --check evidence_album_viewer.js` | PASS |
| CC06-ATR-003 | Album/Portal XML 解析 | PASS |
| CC06-ATR-004 | `git diff --check` | PASS |
| CC06-ATR-005 | Odoo 模块升级 `-u wd_evidence_album --stop-after-init` | PASS |
| CC06-ATR-006 | `TestEvidenceAlbumPreview`：Draft 预览动作和 Published 拒绝 | PASS |
| CC06-ATR-007 | 用户确认预览入口、Portal Viewer 展示、预览限制、返回行为和权限边界 | PASS；证据来源 `user-confirmed` |

## 2. 已覆盖的自动检查

- 预览 URL 返回 `ir.actions.act_url`；
- Preview 路由使用后台 `auth="user"`；
- Published/Revoked 不属于预览状态；
- Preview 模式模板不挂载选择/批量下载控制；
- Preview 媒体 URL 使用 Item ID 和受保护媒体 Controller；
- CC-04 Portal 路由和媒体路径未被删除或改写。
- 模块升级后 `wd_evidence_album` 状态为 `installed`，Odoo 服务已重启加载 CC-06 路由和视图。
- Playwright 访问 `/odoo/evidence-albums/14/preview`：修复前 500；启用 `website=True` 并升级模块后页面正常返回。
- 预览模式 DOM 无媒体选择框和批量下载控件；Page Tab 切换事件可切换可见 Page。

## 3. 尚未覆盖的自动检查

- 后台业务用户、审核人、管理员的实际 ACL 和记录规则矩阵；
- 跨客户/跨公司和无记录权限拒绝；
- 未登录重定向及登录后返回原 URL；
- Preview 不改变 Album 状态、Token、`published_at`、`revoked_at`；
- CC-04 GET/HEAD、Range、MIME、404 和缩略图完整回归。

## 4. 证据限制

- 本 ATR 不把 Agent 的页面观察写成用户 HVR；
- HVR 必须分别标注 `user-confirmed`、`agent-observed` 或 `automated`；
- 本 ATR 的 PASS 表示 CC-06 实施验证已通过，不表示上游 SRS、Implementation Plan 和 Technical Debt Register 门禁已补齐；
- 上游文档门禁仍按 CC-06 Coding Contract §1.3 和 §14 单独跟踪。
