# WMS Evidence Album — CC-02 IHR
# Implementation History Record

## 0. 文档治理

| 项目 | 内容 |
|---|---|
| Intent ID | `wd-evidence-album-cc-02` |
| CC | [CC-02 Coding Contract](./wd_evidence_album_CC-02_Coding_Contract_v1.0.0.md) |
| 模块 | `wd_evidence_album` |
| 上游基线 | SRS v1.0.0、TDD v1.0.0、Implementation Plan v1.0.0 |
| 前置基线 | CC-01 implementation committed at `9443848` |
| 当前状态 | Implementation in progress；来源/上传核心流程已实现，关闭材料未完成 |

本 IHR 只记录 CC-02 实际发生的实施事实，不把定向验证结果替代 ATR，也不把 Agent/Tool 观察替代 HVR。

## 1. 实施范围

| 任务 | 实际状态 |
|---|---|
| CC-02-T01 动态来源 Resolver | 已实现；使用 `ir.model`/Registry 和普通权限读取 |
| CC-02-T02 标题/描述映射 | 已实现显式配置映射；TDD-Q-002 已确认未配置字段时拒绝创建，不做隐式推导 |
| CC-02-T03 媒体合法性校验 | 已实现 JPG/JPEG/PNG/MP4 MIME、扩展名、内容签名校验 |
| CC-02-T04 从记录创建 Page | 已实现单来源记录 Page/Item 创建和来源快照 |
| CC-02-T05 向既有 Page 添加媒体 | 已实现来源字段内选择和 Album 唯一性检查 |
| CC-02-T06 直接上传 | 已实现标准 `ir.attachment` 创建、上传 Item 和失败清理 |
| CC-02-T07 关闭材料 | IHR/ATR 已建立；HVR/FR 尚未完成 |

## 2. 实际变更

### 2.1 后台来源采集可用性修正

- Source Config 使用 `label` 作为记录显示名称，后台下拉不再显示模型名和数据库 ID；
- Page 使用 `title` 作为记录显示名称，向导和关联字段不再显示 `wd.evidence.album.page,<id>`；
- 来源采集向导使用按 Source Config 动态生成的临时记录选择器：用户只从该配置模型的可读记录显示名称中选择来源记录，不要求输入数据库 ID，也不再重复选择模型；
- 业务动作仍以来源记录 ID 执行服务端校验和快照保存，UI 显示与业务追溯字段保持分离。

- 新增 `wd.evidence.album.media` 媒体服务模型；
- Source Config 增加运行时配置校验、Resolver 和标题/描述映射；
- Album 增加从单一来源记录创建 Page/Item 的业务入口；
- Page 增加来源附件选择和直接上传入口；
- Item 增加统一媒体校验入口和来源/上传语义校验；
- 不 import、不 inherit 任何具体 `wd_qooling.*` 或来源业务模块；
- 直接上传附件不设置业务单据 `res_model`/`res_id`；
- 删除 Item 不删除附件，沿用 CC-01 附件生命周期。

## 3. TDD-Q-008 验证替代方案

使用已加载的 Odoo `mail.message` 模型作为专用验证模型：

- 配置模型：`mail.message`；
- 动态字段：`attachment_ids`；
- 字段关系：Many2many → `ir.attachment`；
- 标题/描述字段：`subject` / `body`；
- 验证内容：Registry 加载、`record[field_name]`、普通权限读取、单记录附件集合；
- 该模型只用于验证，不写入生产 manifest 依赖，也不写入生产代码硬编码。

## 4. 未解决项和限制

- TDD-Q-002 已解决：未配置标题/描述字段时拒绝从记录创建 Page，不使用隐式默认字段；
- 来源集成仍需补充更多权限、空值和多记录证据；
- CC-02 HVR 尚未执行；
- CC-02 FR 尚未形成；
- CC-02 尚未冻结或关闭。
