# WMS Evidence Album — CC-06 IHR
# Implementation History Record

## 0. 文档治理

| 项目 | 内容 |
|---|---|
| Intent ID | `wd-evidence-album-cc-06` |
| CC | [CC-06 Coding Contract](./wd_evidence_album_CC-06_Coding_Contract_v1.0.0.md) |
| 模块 | `wd_evidence_album` |
| 环境 | Odoo 18 Community Edition；数据库 `odoo18ce`；Python venv `venv` |
| 当前状态 | 已完成；预览 500 已修复，自动化验证和浏览器 HVR 均通过 |
| 日期 | 2026-09-29 |

本 IHR 记录实际实施事实，不将 Agent 观察替代用户 HVR。用户明确授权在 SRS/Implementation Plan/Technical Debt Register 上游补齐前开始实施；该治理偏差保留记录，不能视为上游文档已补齐。

## 1. 任务实施状态

| 任务 | 实际状态 | 实现位置 |
|---|---|---|
| CC-06-T01 预览入口和路由 | 已实施 | `models/album.py`、`views/album_views.xml`、`controllers/portal.py` |
| CC-06-T02 后台预览授权 | 已实施 | `controllers/portal.py` |
| CC-06-T03 Portal Viewer 展示复用 | 已实施；复用现有 Portal 模板、OWL Viewer 和媒体 URL 结构 | `views/portal_templates.xml`、`static/src/js/evidence_album_viewer.js` |
| CC-06-T04 预览限制和返回 | 已实施；用户确认通过 | `views/portal_templates.xml`、`controllers/portal.py` |
| CC-06-T05 关闭材料 | IHR/ATR/HVR/FR 已建立 | 本组 CC-06 文档 |

## 2. 实际变更

- Album Form 增加 `Preview Portal` 按钮，仅在 Draft/Confirmed 可见；
- `action_preview_portal()` 检查后台读取权限和状态，返回新窗口预览 URL；
- 新增后台预览路由 `/odoo/evidence-albums/<album_id>/preview`；
- 预览使用后台 Album 记录规则，不使用 Portal `base.group_portal`、Commercial Partner、Token 或有效期；
- Published/Revoked 预览由入口隐藏并在服务端拒绝；
- 预览使用当前 Album/Page/Item 数据，不创建模拟记录；
- Portal Viewer 模板增加 Preview 模式提示；
- Preview 模式隐藏 Select all、媒体选择和批量 Download；
- 图片/视频媒体请求通过同一媒体 Controller 的 `?preview=1` 分支执行后台授权；
- 复用 CC-04 的 Item ID 媒体 URL、缩略图、视频 Range/响应处理和 Viewer 前端逻辑；
- 预览页返回 Album Form，媒体不可用时沿用 CC-04 错误语义。
- 修复预览路由复用 `portal.portal_layout` 时缺少网站上下文导致的 500；
- 增加 Viewer 挂载和 Page Tab 的页面级兜底绑定，确保预览页面可切换 Page。

## 3. 偏差和限制

- 当前 Album 实际状态模型使用 `confirmed` 表示已审核/待发布基线；CC-06 的 Approved 语义映射到 `confirmed`；
- 审核流程当前没有独立审核页面，未新增该页面，预览入口仅放在 Album Form；
- 单文件下载和批量 ZIP 不属于 Preview；预览不提供批量选择和下载控件；
- 预览媒体 URL 复用 CC-04 Controller，但通过受保护的预览查询参数选择后台授权分支；
- 用户于 2026-09-29 明确确认 CC-06 验证通过，HVR 已登记为 `user-confirmed`；
- Playwright 已观察预览页面返回 200、提示显示、选择框/批量控件隐藏，并通过事件验证 Page 切换；
- SRS BR、Implementation Plan CC-06 和 Technical Debt Register 新条目仍待上游治理补齐。

## 4. 变更文件

- `mymodules/wd_evidence_album/models/album.py`
- `mymodules/wd_evidence_album/controllers/portal.py`
- `mymodules/wd_evidence_album/views/album_views.xml`
- `mymodules/wd_evidence_album/views/portal_templates.xml`
- `mymodules/wd_evidence_album/tests/test_preview.py`
- `mymodules/wd_evidence_album/tests/__init__.py`

## 5. 关闭状态和遗留治理项

- CC-06 实施、自动化验证和用户确认型 HVR 已完成，当前实施状态为已完成。
- SRS BR、Implementation Plan CC-06 和 Technical Debt Register 新条目仍待上游治理补齐；该遗留项不改写为已完成。
- 上游文档补齐后，应回填 CC-06 追溯矩阵中的具体引用。
