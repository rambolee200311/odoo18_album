# WMS Evidence Album — CC-07 IHR
# Implementation History Record

## 0. 文档治理

| 项目 | 内容 |
|---|---|
| Intent ID | `wd-evidence-album-cc-07` |
| CC | [CC-07 Coding Contract](./wd_evidence_album_CC-07_Coding_Contract_v1.0.0.md) |
| 模块 | `wd_evidence_album` |
| 环境 | Odoo 18 Community Edition；数据库 `odoo18ce`；Python venv `venv` |
| 当前状态 | 已完成；核心代码、定向自动化和 HVR 均通过 |
| 日期 | 2026-09-29 |

本 IHR 记录 CC-07 的实际实施事实。原 Implementation Plan 仍需完成 CC-05 → CC-07 的正式编号修订；该治理事项不被本记录视为已完成。

## 1. 任务实施状态

| 任务 | 状态 | 实现位置 |
|---|---|---|
| CC-07-T01 Source Config 字段候选 | 已实施 | `models/source_config.py`、`views/source_config_views.xml` |
| CC-07-T02 动态来源运行时验证 | 已实施；TDD-Q-008 证据仍需独立治理 | `models/source_config.py`、`tests/test_source_config.py` |
| CC-07-T03 Portal 当前 Page 多选 | 已实施 | `static/src/js/evidence_album_viewer.js`、`views/portal_templates.xml` |
| CC-07-T04 ZIP 授权和资源限制 | 已实施 | `controllers/portal.py`、`models/settings.py`、`views/settings_views.xml` |
| CC-07-T05 ZIP 生成和文件名安全 | 已实施 | `controllers/portal.py` |
| CC-07-T06 回归与关闭材料 | IHR/ATR/HVR 已建立；FR 待关闭 | 本组 CC-07 文档 |

## 2. 已实施接口和数据边界

- Source Config 通过 `ir.model.fields` 仅提供 Many2many 到 `ir.attachment` 的候选字段；
- `field_id` 只同步 `field_name`，不会自动启用配置；
- Resolver 使用普通权限读取来源模型、来源记录和附件 Recordset；
- Portal 批量请求只接受 Item ID，并限制为同一 Page；
- Portal 授权先于附件 `sudo()` 读取；
- 批量请求复核 Portal 用户、Commercial Partner、Album 状态、撤销、有效期、Page/Item 归属和媒体可用性；
- ZIP 在请求期间通过内存流生成，不写入长期业务附件；
- 文件名清洗控制字符、路径分隔符和危险路径，并在 ZIP 内保证大小写不敏感的唯一性；
- ZIP 文件数、总大小、内存、超时和并发通过 `ir.config_parameter` 控制；
- CC-04 单文件媒体路由和 Portal 授权路径未被替换。

## 3. 变更文件

### 3.1 后端

- `mymodules/wd_evidence_album/controllers/portal.py`
- `mymodules/wd_evidence_album/models/source_config.py`
- `mymodules/wd_evidence_album/models/settings.py`

### 3.2 前端和视图

- `mymodules/wd_evidence_album/static/src/js/evidence_album_viewer.js`
- `mymodules/wd_evidence_album/views/portal_templates.xml`
- `mymodules/wd_evidence_album/views/source_config_views.xml`
- `mymodules/wd_evidence_album/views/settings_views.xml`

### 3.3 测试

- `mymodules/wd_evidence_album/tests/test_source_config.py`
- `mymodules/wd_evidence_album/tests/test_portal.py`
- `mymodules/wd_evidence_album/tests/test_preview.py`

## 4. 偏差、限制和遗留项

- 原 CC-05 的实现基础已存在，本阶段将其按冻结 CC-07 契约重新归档和验证；
- Implementation Plan 当前仍使用 CC-05 编号，需在 CC-07 关闭前修订；
- TDD-Q-004 的正式资源决策仍需维护；
- TDD-Q-008 的动态 Registry 和运行时字段读取证据仍需独立补强；
- TD-001 的兼容迁移策略和关闭状态仍需独立治理；
- Portal 用户于 2026-09-29 确认 HVR 全部通过，证据来源为 `user-confirmed`；
- CC-07 FR 尚未建立，关闭材料仍需补齐。
