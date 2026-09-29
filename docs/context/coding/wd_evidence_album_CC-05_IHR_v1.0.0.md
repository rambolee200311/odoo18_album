# WMS Evidence Album — CC-05 IHR
# Implementation History Record

## 0. 文档治理

| 项目 | 内容 |
|---|---|
| Intent ID | `wd-evidence-album-cc-05` |
| CC | [CC-05 Coding Contract](./wd_evidence_album_CC-05_Coding_Contract_v1.0.0.md) |
| 变更契约 | [CC-05 Frozen Change Contract](./wd_evidence_album_CC-05_Technical_Debt_Draft_v1.0.0.md) |
| 模块 | `wd_evidence_album` |
| 环境 | Odoo 18 Community Edition；数据库 `odoo18ce`；Python venv `venv` |
| 当前状态 | CC-05 实施完成；HVR-CC05-001 至 HVR-CC05-008 全部通过；CC-05 已冻结 |
| 日期 | 2026-09-29 |

## 1. 实施结果

| 任务 | 状态 | 实现位置 |
|---|---|---|
| CC-05-T01 Source Config 字段候选 | 已实施并通过验证 | `models/source_config.py`、`views/source_config_views.xml`、`tests/test_source_config.py` |
| CC-05-T02 动态来源运行时验证 | 已实施；TDD-Q-008 仍按独立技术债管理 | `models/source_config.py`、`tests/test_source_config.py` |
| CC-05-T03 当前 Page 多选 | 已实施并通过 HVR | `static/src/js/evidence_album_viewer.js`、`views/portal_templates.xml` |
| CC-05-T04 ZIP 授权和资源限制 | 已实施并通过 HVR | `controllers/portal.py`、`models/settings.py` |
| CC-05-T05 ZIP 生成和文件名安全 | 已实施并通过 HVR | `controllers/portal.py` |
| CC-05-T06 关闭材料 | IHR、ATR、HVR 已完成；CC-05 已冻结 | 本组 CC-05 文档 |

## 2. 已实现边界

- Source Config 增加 `ir.model.fields` 候选入口，仅展示当前模型中 Many2many 到 `ir.attachment` 的字段。
- 原有 `field_name` 文本配置仍保留；候选选择只同步字段名，不自动启用配置。
- Source Config 初始化时写入 ZIP 默认资源参数，管理员可通过 `ir.config_parameter` 覆盖。
- Portal 批量请求只接收 Item ID，并限制在一个 Page 内。
- 批量下载先完成 Portal 用户、Commercial Partner、Album 状态、撤销、有效期、Page/Item 归属和媒体可用性校验，再读取附件。
- ZIP 只在请求期间生成，不写入长期业务附件。
- 文件名经过控制字符、路径分隔符和危险路径清洗，并在 ZIP 内唯一化。
- ZIP 生成失败、超限、超时或包含不可用媒体时明确失败，不生成部分成功文件。
- 内存流通过 `with`/`finally` 路径释放；并发通过进程内信号量限制。

## 3. 偏差、限制和技术债边界

### 3.1 TDD-Q-008

CC-05 已完成字段候选入口和基础 Resolver 定向测试。以下内容不作为 CC-05 HVR 的未通过项，仍作为独立 TDD-Q-008 技术债证据补强项：

- Registry 中配置模型的动态访问；
- `record[field_name]` 的运行时读取；
- 附件 Recordset 的权限边界；
- 成功和失败路径的明确业务错误；
- 不引入具体业务模块依赖。

因此 TDD-Q-008 仍保持 Open。

### 3.2 Portal HVR（已完成）

Portal 用户已完成 HVR-CC05-001 至 HVR-CC05-008，全部通过。验证覆盖：

- 当前 Page 多选、全选、全消和半选；
- ZIP 下载、内容和文件名边界；
- Item ID-only 请求；
- 超限、不可用媒体和越权错误路径；
- CC-04 单文件预览、下载和授权回归。

### 3.3 资源参数（独立债务仍开放）

本阶段已实现默认参数、后台 ZIP Settings 和读取机制。TDD-Q-004 的正式决策记录仍需按技术债流程维护；HVR 已确认配置限制行为生效，不能替代技术负责人和运维的正式决策记录。

### 3.4 Portal 命名和路由收口

根据 Portal 验证反馈，用户可见名称已由 Evidence Albums 统一调整为 Media Albums：

- Portal 页面、面包屑、卡片和查看器文案；
- 后台菜单、动作、设置、权限显示名称；
- 主路由统一为 `/my/media-albums`；
- 旧 `/my/evidence-albums` 路由保留兼容；
- 内部模型名、XML ID 和模块技术标识保持不变。

同时完成相册列表搜索、排序、分页、封面缩略图和实时搜索交互。

## 4. 变更文件

### 4.1 后端

- `mymodules/wd_evidence_album/controllers/portal.py`
- `mymodules/wd_evidence_album/models/source_config.py`

### 4.2 Portal 和后台视图

- `mymodules/wd_evidence_album/static/src/js/evidence_album_viewer.js`
- `mymodules/wd_evidence_album/views/portal_templates.xml`
- `mymodules/wd_evidence_album/views/source_config_views.xml`

### 4.3 测试

- `mymodules/wd_evidence_album/tests/test_source_config.py`
- `mymodules/wd_evidence_album/tests/__init__.py`

### 4.4 交互和配置

- `mymodules/wd_evidence_album/static/src/js/evidence_album_list.js`
- `mymodules/wd_evidence_album/models/settings.py`
- `mymodules/wd_evidence_album/views/settings_views.xml`

## 5. 关闭结论和后续治理

CC-05 的编码范围、实施材料和 Portal HVR 已完成，HVR-CC05-001 至 HVR-CC05-008 全部通过，CC-05 状态为 Frozen/实施完成。

后续仅保留独立治理事项：

1. 按独立证据补强并关闭 TDD-Q-008；
2. 由技术负责人和运维维护 TDD-Q-004 的正式资源决策记录；
3. 根据独立关闭证据更新 Technical Debt Register；
4. 不因 CC-05 HVR 全部通过而自动关闭 TD-001、TDD-Q-008 或 TDD-Q-004。

## 6. 变更轮次记录

| 日期 | 轮次 | 变更 |
|---|---|---|
| 2026-09-28 | 初始实施 | 完成 Source Config 字段候选、Portal 当前 Page 多选、ZIP 授权与资源限制、IHR/ATR 初稿。 |
| 2026-09-28 | HVR 修复 | 修复 Portal 查看器 JavaScript 语法、ZIP 配置初始化、后台 ZIP Settings、全选/全消和选择状态同步。 |
| 2026-09-29 | Portal 验证 | 使用 Portal 用户完成 ZIP 下载、越权拒绝、Item ID 边界、资源限制和 CC-04 回归验证；HVR 全部通过。 |
| 2026-09-29 | 查看器体验 | 增加 Page Tabs、相册/Page 元信息、媒体筛选、视频播放标识、选择高亮和当前 Page 下载语义。 |
| 2026-09-29 | 列表页体验 | 增加相册描述、页数/图片/视频统计、发布时间、搜索、排序、分页和相册封面。 |
| 2026-09-29 | 命名与路由 | 用户可见名称统一为 Media Albums，主 Portal 路由切换为 `/my/media-albums`，保留旧路由兼容。 |
