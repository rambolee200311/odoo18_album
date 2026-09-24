# WMS Evidence Album — Coding Contract CC-01
# 核心数据模型与后台

## 0. 文档信息

| 项目 | 内容 |
|---|---|
| 模块 | `wd_evidence_album` |
| CC | CC-01 — 核心数据模型与后台 |
| CC 版本 | v1.0.0 |
| 状态 | Frozen Coding Contract |
| Odoo | 18.0 Community Edition |
| 代码目录 | `/Users/lijianqiang/Documents/odoo18_album/mymodules/wd_evidence_album` |
| 上游业务基线 | SRS v1.0.0（Frozen） |
| 上游技术基线 | TDD v1.0.0（Frozen Implementation Baseline） |
| 实施规划基线 | Implementation Plan v1.0.0（Frozen Implementation Plan） |
| 技术验证输入 | TV Report v1.0.0 |
| 项目认知输入 | `wd_evidence_album_Cognition_v1.0.0.md` |

### 0.1 输入材料

- SRS §4、§7、§9、§10、§15、§18；
- TDD §2、§10、§11、§12、§13、§14；
- Implementation Plan §2.1—§2.5；
- TV Report 的 Odoo 18 ORM 和权限相关结论；
- 项目 Cognition 的 Odoo Native First、Simple Models、Explicit Business Logic 和 Robust Before Clever 原则。

### 0.2 对应实施任务

| 任务 | 范围 |
|---|---|
| CC-01-T01 | 模块骨架和依赖 |
| CC-01-T02 | Album ORM 模型 |
| CC-01-T03 | Page ORM 模型 |
| CC-01-T04 | Item ORM 模型和关系完整性 |
| CC-01-T05 | Source Config ORM 模型 |
| CC-01-T06 | 基础 ACL 和 Record Rule |
| CC-01-T07 | 后台视图和排序 |
| CC-01-T08 | CC-01 关闭材料 |

---

## 1. 契约范围声明

### 1.1 本 CC 覆盖

本 CC 覆盖：

- TDD §2：数据模型设计；
- TDD §10：后台界面设计中属于基础模型和后台管理的部分；
- TDD §11：ACL、Record Rule 和后台角色；
- Implementation Plan §2.3 的 CC-01-T01 至 CC-01-T08；
- Implementation Plan §2.4 的 9 条 CC-01 验收条件。

### 1.2 本 CC 不覆盖

以下内容明确不属于 CC-01：

- 动态来源字段的实际业务记录读取和 `record[field_name]` 集成（CC-02）；
- 从业务记录创建相页或选择业务媒体（CC-02）；
- 直接上传图片/视频（CC-02）；
- 审核、发布、Token、有效期和撤销动作的业务实现（CC-03）；
- Portal 访问策略、媒体 Controller、图片/视频流和 OWL（CC-04）；
- 多选 ZIP、ZIP 限制和临时下载（CC-05）；
- 完整代码、测试用例、排期、估工和部署方案。

Album 表单可以预留 CC-03 动作按钮位置，但本 CC 不实现审核/发布动作的业务行为。

### 1.3 前置条件

CC-01 无硬门禁，可以在冻结 TDD 和 Implementation Plan 的基础上开始。

以下是允许存在但不阻塞 CC-01 的待确认项：

- TDD-Q-001：空相册是否允许发布；
- TDD-Q-002：标题/描述默认字段映射；
- TDD-Q-003：来源信息展示配置；
- TDD-Q-004：ZIP 资源配置；
- TDD-Q-007：缩略图实现方式；

TDD-Q-008 不阻塞 CC-01 的模型和后台开发，但必须在 CC-01 结束前解决或形成明确验证证据；否则阻塞 CC-02 的来源采集部分。

### 1.4 后续依赖

CC-02 依赖本 CC 产出的：

- 四个 ORM 模型及关系；
- Item 附件唯一性和可用性边界；
- Source Config 的字段校验接口；
- 后台基础权限；
- Album/Page/Item 的后台管理界面。

TDD-Q-008 必须在 CC-01 结束前解决或形成明确验证证据，但不属于 CC-01 的来源采集实现。

---

## 2. 模块骨架契约

### 2.1 模块元数据

| 项目 | 契约 |
|---|---|
| 技术名 | `wd_evidence_album` |
| 依赖 | `base`、`mail`、`portal`、`web` |
| 模块版本 | 遵循项目 Odoo 模块版本规则；具体 manifest 版本号在项目级版本策略确认前标为“待项目确认” |
| 安装方式 | 标准 Odoo 模块安装和升级 |
| 来源依赖 | 不依赖任何具体来源业务模块 |

`__manifest__.py` 的 `depends` 只能包含 TDD/SRS 已确定的依赖。实现验证应检查依赖列表，不得出现任何具体业务模块名或 `wd_qooling.*`。

### 2.2 推荐目录结构

```text
mymodules/wd_evidence_album/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── album.py
│   ├── page.py
│   ├── item.py
│   └── source_config.py
├── views/
│   ├── album_views.xml
│   ├── page_views.xml
│   ├── item_views.xml
│   ├── source_config_views.xml
│   └── menus.xml
├── security/
│   ├── security.xml
│   └── ir.model.access.csv
├── data/
└── tests/
    ├── __init__.py
    └── (测试文件由后续 CC 按需增加)
```

CC-01 不创建 Controller、OWL、Portal 模板、ZIP 组件或来源 Resolver 实现目录。后续 CC 可按已冻结 TDD 增加目录。

### 2.3 命名规范

| 对象 | 规范 |
|---|---|
| ORM 模型技术名 | `wd.evidence.album`、`wd.evidence.album.page`、`wd.evidence.album.item`、`wd.evidence.album.source.config` |
| Python 文件 | 小写下划线，按模型职责命名 |
| 字段名 | 小写下划线；关系字段使用 Odoo 语义命名，如 `page_ids`、`item_ids` |
| 业务动作 | `action_*`，动作必须是显式业务入口 |
| 约束方法 | `_check_*` 或 `_constraint_*`，仅承担约束检查 |
| 计算方法 | `_compute_*`，只计算，不执行跨对象业务动作 |
| XML ID | `{module}.{object_type}_{business_name}`；具体 XML ID 清单如需对外引用，须在实现前固定 |
| 安全组 XML ID | `group_album_user`、`group_album_reviewer`、`group_album_manager` |
| ACL 文件 | `security/ir.model.access.csv` |
| 安全组文件 | `security/security.xml` |

项目没有单独冻结的 Python 测试命名规范；测试文件命名标记为“待项目确认”，不影响本 CC 的模型和后台契约。

当其他模块或后续 CC 的 Controller、Portal 模板需要引用本模块 XML ID 时，必须在 CC-01 关闭材料中登记该 XML ID；仅模块内部使用的 XML ID 可以按本命名规范确定。

### 2.4 禁止事项

- 不 import 任何 `wd_qooling.*` 或其他具体来源业务模块；
- 不 inherit 任何具体来源业务模型；
- 不写死来源模型名或来源附件字段名；
- 不修改 Odoo 官方核心代码或官方模块；
- 不把核心约束只实现为视图隐藏；
- 不在 CC-01 实现 CC-02～CC-05 的功能。

---

## 3. 模型契约

### 3.1 `wd.evidence.album`

#### 3.1.1 字段清单

| 字段 | 类型 | 必填 | 默认/计算 | 说明 |
|---|---|---:|---|---|
| `name` | `Char` | 是 | 无默认值 | 相册名称 |
| `customer_id` | `Many2one(res.partner)` | 是 | 写入时规范化 | 保存 Commercial Partner |
| `description` | `Text` | 否 | 空 | 相册描述 |
| `state` | `Selection` | 是 | `draft` | `draft`、`pending_review`、`approved`、`published`、`revoked` |
| `token` | `Char` | 否 | 草稿为空 | 发布时由 CC-03 生成；唯一、索引 |
| `valid_until` | `Datetime` | 否 | 空 | 有效期；不是状态 |
| `published_at` | `Datetime` | 否 | 空 | 发布时间，由 CC-03 写入 |
| `revoked_at` | `Datetime` | 否 | 空 | 撤销时间，由 CC-03 写入 |
| `reviewed_by` | `Many2one(res.users)` | 否 | 空 | 审核人，由 CC-03 写入 |
| `page_ids` | `One2many(wd.evidence.album.page)` | 否 | 空集合 | 相册内相页，按 `sequence` 排序 |

CC-01 只建立字段和模型边界。Token 生成、状态动作、发布和撤销的业务实现属于 CC-03。

#### 3.1.2 关系

```text
wd.evidence.album 1 ─── N wd.evidence.album.page
```

`page_ids` 的反向字段为 `album_id`。相册删除时 Page 记录按 TDD 删除策略处理，但不得删除 Page 下 Item 所引用的 `ir.attachment`。

#### 3.1.3 约束

- `name` 和 `customer_id` 必填；
- `customer_id` 写入和修改时规范化为 `customer_id.commercial_partner_id`；
- `state` 的取值范围通过 Python constraint 或 `@api.constrains` 保证，不依赖 `Selection` 字段本身的隐式约束；允许值为冻结的五个状态；
- `token` 非空时必须唯一；
- `valid_until` 若设置，必须是合法的时间值；
- 已发布 Album 禁止直接删除；删除门禁必须在 ORM 业务层存在，不能只依赖视图；
- Page 必须通过 `album_id` 归属当前 Album。

Python 约束接口至少覆盖客户规范化、状态值和已发布删除门禁。数据库约束至少覆盖 Token 唯一性；具体 SQL 约束名称由实现确定。

`valid_until` 只用于有效期判断，不改变 `state`；访问时由 CC-03/CC-04 的授权链判断是否过期。

#### 3.1.4 索引

- `state`；
- `customer_id`；
- `token` 唯一索引；
- `valid_until`。

#### 3.1.5 业务动作接口

下列方法签名是 CC-01 建立的模型接口边界；业务行为由 CC-03 实现。CC-01 不实现状态流转逻辑。

| 方法签名 | CC-01 接口要求 | 前置状态 | 后置状态 |
|---|---|---|---|
| `action_submit_review(self)` | 方法入口可被后台按钮引用 | `draft` | `pending_review`（CC-03） |
| `action_approve(self)` | 方法入口可被审核按钮引用 | `pending_review` | `approved`（CC-03） |
| `action_reject(self)` | 方法入口可被拒绝按钮引用 | `pending_review` | `draft`（CC-03） |
| `action_publish(self)` | 方法入口可被发布按钮引用 | `approved` | `published`（CC-03） |
| `action_revoke(self)` | 方法入口可被撤销按钮引用 | `published` | `revoked`（CC-03） |
| `action_reset_token(self)` | 方法入口可被重置 Token 按钮引用 | 已有 Token/按 CC-03 权限 | 新 Token（CC-03） |

如果 CC-01 需要为了视图加载声明动作占位，必须保持接口签名稳定，不得在 CC-01 中提前实现 CC-03 的业务规则。

### 3.2 `wd.evidence.album.page`

#### 3.2.1 字段清单

| 字段 | 类型 | 必填 | 默认/计算 | 说明 |
|---|---|---:|---|---|
| `album_id` | `Many2one(wd.evidence.album)` | 是 | 当前 Album | 所属相册 |
| `title` | `Char` | 是 | 无默认值 | 相页标题 |
| `description` | `Text` | 否 | 空 | 相页描述 |
| `sequence` | `Integer` | 是 | 默认排序值 | Album 内顺序 |
| `item_ids` | `One2many(wd.evidence.album.item)` | 否 | 空集合 | 相页媒体项，按 `sequence` 排序 |

#### 3.2.2 关系与约束

```text
wd.evidence.album.page 1 ─── N wd.evidence.album.item
```

- Page 只能属于一个 Album；
- `album_id` 必填；
- Page 的 `album_id` 修改为另一个 Album 时必须拒绝；
- Page 只能在所属 Album 内调整 `sequence`；
- Page 不保存来源模型、来源记录或来源字段；
- 删除 Page 级联删除 Item 记录，但不 unlink 任何附件。

#### 3.2.3 索引

- `(album_id, sequence)`；
- `album_id` 普通索引可由复合索引覆盖。

### 3.3 `wd.evidence.album.item`

#### 3.3.1 字段清单

| 字段 | 类型 | 必填 | 默认/计算 | 说明 |
|---|---|---:|---|---|
| `page_id` | `Many2one(wd.evidence.album.page)` | 是 | 当前 Page | 所属相页 |
| `album_id` | `Many2one(wd.evidence.album)` | 是 | 存储型 related，自 `page_id.album_id` 派生 | 技术字段，不允许独立编辑 |
| `attachment_id` | `Many2one(ir.attachment)` | 否 | 空 | `ondelete="set null"` |
| `source_type` | `Selection` | 是 | 无或由采集入口提供 | `record`、`upload` |
| `source_model` | `Char` | 条件必填 | 空 | `record` 时保存来源模型名 |
| `source_record_id` | `Integer` | 条件必填 | 空 | `record` 时保存来源记录 ID |
| `source_field_name` | `Char` | 条件必填 | 空 | `record` 时保存来源字段名 |
| `media_type` | `Selection` | 是 | 由采集入口提供 | `image`、`video` |
| `sequence` | `Integer` | 是 | 默认排序值 | Page 内顺序 |
| `note` | `Text` | 否 | 空 | 媒体说明 |
| `availability_state` | `Selection` | 是 | 由 Item 模型刷新 | `available`、`unavailable` |

CC-01 建立字段和一致性边界；来源字段实际读取、直接上传和媒体合法性入口属于 CC-02。

#### 3.3.2 关系和派生一致性

```text
wd.evidence.album.item
    ├── page_id → wd.evidence.album.page
    ├── album_id → page_id.album_id（stored related）
    └── attachment_id → ir.attachment
```

必须满足：

- `item.page_id.album_id == item.album_id` 始终成立；
- 用户不能直接写入 `album_id`；
- 写入 `page_id` 时由 Page 的 Album 自动同步 `album_id`；
- 若任何写入数据造成 `page_id.album_id != album_id`，写入必须被拒绝；
- Page 跨 Album 移动必须拒绝，不能依赖 related 字段事后修复；
- `album_id` 的存储设计仅用于 Album 级唯一性和授权查询，不改变领域归属。

#### 3.3.3 约束

- `page_id` 必填；
- `attachment_id` 为空时，Item 必须保留且 `availability_state="unavailable"`；
- `source_type="record"` 时来源快照字段必须完整；
- `source_type="upload"` 时来源快照字段必须为空；
- `media_type` 只能是 `image` 或 `video`；
- 同一 Album 中非空 `attachment_id` 只能出现一次；
- 数据库唯一约束保护 `(album_id, attachment_id)`；PostgreSQL 对 NULL 的默认行为允许多个空 `attachment_id` 共存，符合“空附件不参与重复约束”的需求，实现时不需要额外的部分索引；
- 业务检查在创建/修改前提前拒绝重复附件；
- Item 删除不能调用附件删除。

#### 3.3.4 可用性刷新时机

`availability_state` 刷新逻辑集中在 Item 模型，不散落在视图或 Controller。至少在以下时机刷新：

| 时机 | 触发方 |
|---|---|
| Item 创建或 `attachment_id` 关联变化 | Item 模型的 `create` / `write` |
| 附件创建/修改导致 Item 重新建立引用 | Item 模型的 `write` |
| 原始附件删除后 `attachment_id` 被置空 | `ondelete="set null"` 触发 Item 模型的 `write` |
| 媒体读取或下载前 | 后续 CC 的 Controller 主动调用 Item 模型的刷新方法 |
| ZIP 或 Portal 读取前 | 后续 CC 的 Controller 主动调用 Item 模型的刷新方法 |

CC-01 负责建立模型级刷新边界；媒体采集和读取入口分别由 CC-02/CC-04 实现。

#### 3.3.5 删除策略和索引

- Item 删除只删除 Item；
- `attachment_id` 对附件使用 `set null`；
- Page 删除级联 Item；
- 不删除 `ir.attachment`；
- `(page_id, sequence)` 索引；
- `(album_id, attachment_id)` 唯一索引，空附件不参与重复约束。

### 3.4 `wd.evidence.album.source.config`

#### 3.4.1 字段清单

| 字段 | 类型 | 必填 | 默认/计算 | 说明 |
|---|---|---:|---|---|
| `model_id` | `Many2one(ir.model)` | 是 | 无 | 配置来源模型 |
| `field_name` | `Char` | 是 | 无 | 附件字段名 |
| `label` | `Char` | 是 | 无 | 后台显示标签 |
| `title_field_name` | `Char` | 否 | 空 | 标题映射字段 |
| `description_field_name` | `Char` | 否 | 空 | 描述映射字段 |
| `active` | `Boolean` | 是 | `True` | 是否启用 |

#### 3.4.2 约束和校验接口

保存和启用配置时必须校验：

- `model_id` 存在；
- 模型在当前 Odoo Registry 中可用；
- `field_name` 在目标模型中存在；
- 字段 `ttype="many2many"`；
- 字段 `relation="ir.attachment"`；
- 标题/描述字段属于同一模型并允许读取；
- `(model_id, field_name)` 唯一；
- 当前后台用户具有来源模型和字段的读取权限。

字段校验必须形成稳定的模型级调用接口，与 CC-02-T01 Resolver 的调用方式一致。CC-02 只能调用该接口，不得重新定义第二套字段校验逻辑。

#### 3.4.3 停用和删除策略

- `active=False` 不影响已创建 Item；
- 停用配置不得继续创建新的来源 Item；
- 候选字段元数据发现不等于自动暴露；
- 配置删除优先采用停用；
- 已被已有 Item 的来源快照引用时，删除应被拒绝；
- Source Config 不保存动态来源记录，也不承担 Portal 权限。

---

## 4. ACL 和 Record Rule 契约

### 4.1 组定义

| 组 XML ID | 组名 | 职责 |
|---|---|---|
| `group_album_user` | WMS 业务用户 | 创建和编辑自己创建的 Album、Page、Item |
| `group_album_reviewer` | WMS 审核人 | 管理审核范围内 Album，并在 CC-03 执行审核/发布 |
| `group_album_manager` | 管理员 | 全部后台管理 |

组继承关系：

- `group_album_reviewer` 继承 `group_album_user` 的基础访问能力；
- `group_album_manager` 继承审核人能力；
- 不允许 Portal 组继承任何后台管理组；
- 审核/发布动作的业务权限由 CC-03 进一步实现，本 CC 只建立组和基础访问边界。

### 4.2 `ir.model.access.csv` 行契约

权限列顺序为：`model_id`、`group_id`、`read`、`write`、`create`、`unlink`。

| 模型 | 业务用户 | 审核人 | 管理员 |
|---|---|---|---|
| Album | 1/1/1/0 | 1/1/1/0 | 1/1/1/1 |
| Page | 1/1/1/0 | 1/1/1/1 | 1/1/1/1 |
| Item | 1/1/1/0 | 1/1/1/1 | 1/1/1/1 |
| Source Config | 1/0/0/0 | 1/0/0/0 | 1/1/1/1 |

说明：

- 业务用户不能通过 ACL 删除 Album；已发布 Album 的删除还必须由模型业务门禁拒绝；
- 审核人可删除 Page/Item 以完成审核整理，但不因此获得删除已发布 Album 的权限。该能力是 CC-01 基于审核流程需要作出的技术判断；如果 SRS 认为审核人不应删除 Page/Item，必须回到 SRS 修订。当前按“审核人可删除 Page/Item”处理，因为审核整理需要删除不应分享的媒体；
- Source Config 的实际新增、修改和停用只由管理员完成；
- Portal 用户不通过这些后台 ACL 获取媒体内容。

如果 Odoo 组继承导致权限合并结果与表格不同，必须以最小权限原则修正。

### 4.3 Record Rule

| 规则名 | 模型 | Domain | 组 | 权限 |
|---|---|---|---|---|
| Album: own records | `wd.evidence.album` | `[('create_uid', '=', user.id)]` | `group_album_user` | 读/写/创建 |
| Album: reviewer access | `wd.evidence.album` | 项目审核范围；默认由审核组访问规则承载 | `group_album_reviewer` | 读/写/创建 |
| Album: manager access | `wd.evidence.album` | `[(1, '=', 1)]` | `group_album_manager` | 全部 |
| Page: inherited ownership | `wd.evidence.album.page` | `[('album_id.create_uid', '=', user.id)]` | `group_album_user` | 读/写/创建 |
| Item: inherited ownership | `wd.evidence.album.item` | `[('album_id.create_uid', '=', user.id)]` | `group_album_user` | 读/写/创建 |

实现时必须把审核人和管理员规则设计为不被业务用户规则意外收窄；具体共享/全局规则组合需按 Odoo 18 Record Rule 语义验证。

验证方式：使用审核人账号访问一个非自己创建的 Album，确认可以访问；使用业务用户账号访问同一个 Album，确认不能访问。该验证只针对后台模型权限，不替代后续 Portal Controller 授权。

来源记录权限不由 Album Record Rule 替代。CC-02 读取来源记录时必须使用当前后台用户的普通权限。

### 4.4 与 SRS §9 对应

| SRS 角色 | CC-01 契约 |
|---|---|
| WMS 业务用户 | 可创建和编辑自己创建的 Album；可管理其 Page/Item |
| WMS 审核人 | 具备后台管理和整理权限；审核/发布动作由 CC-03 补齐 |
| Portal 客户 | 无后台模型权限；Portal 访问由 CC-04 Controller 授权 |
| 管理员 | 具备全部后台模型和配置权限 |

---

## 5. 后台视图契约

### 5.1 Album 表单视图

字段分组：

- 基础信息：`name`、`customer_id`、`description`；
- 状态信息：`state`、`valid_until`、`published_at`、`revoked_at`、`reviewed_by`；
- 相页区域：`page_ids`；
- Token 信息：`token`，仅后台授权角色可见且只读。

只读字段：

- `state`；
- `token`；
- `published_at`；
- `revoked_at`；
- `reviewed_by`。

按钮区域预留：

- 提交审核；
- 批准；
- 拒绝；
- 发布；
- 撤销；
- 重置 Token。

按钮可按状态和组隐藏，但按钮隐藏只是 UI 优化，不构成权限实现；权限必须由 ORM 动作方法和 ACL/Record Rule 保证。CC-01 只建立按钮位置、调用方法名和基本可见性；业务动作由 CC-03 实现。

### 5.2 Album 列表和搜索视图

可见字段：

- `name`；
- `customer_id`；
- `state`；
- `valid_until`；
- `published_at`；
- `reviewed_by`。

默认排序按创建时间倒序或项目现有 Odoo 约定；如果项目未确认默认排序，标记为“待项目确认”。搜索过滤至少提供：

- 状态；
- 客户；
- 有效期；
- 我的相册。

### 5.3 Page 表单/列表视图

字段：

- `title`；
- `description`；
- `sequence`；
- `item_ids`；
- 所属 Album 只读显示。

排序：

- 以 `sequence` 为主排序；
- 允许在同一 Album 内编辑 `sequence` 或使用 Odoo 标准排序交互；
- 不提供目标 Album 选择器，因此不能通过 UI 跨 Album 移动 Page。

### 5.4 Item 表单/列表视图

字段：

- `attachment_id`；
- 媒体类型；
- `availability_state`；
- `note`；
- `sequence`；
- `source_type`；
- 来源模型、来源记录 ID、来源字段名。

只读字段：

- `album_id`；
- `attachment_id` 的来源审计信息；
- `source_model`；
- `source_record_id`；
- `source_field_name`；
- `availability_state`（由模型刷新）。

`source_model`、`source_record_id`、`source_field_name` 默认只读，不允许普通用户编辑来源追溯信息。

显示：

- 支持的附件缩略图或低成本预览；
- 媒体类型；
- 不可用标识。

CC-01 只提供 Item 管理结构；直接上传和媒体采集入口属于 CC-02。

### 5.5 Source Config 表单/列表视图

字段：

- `model_id`；
- `field_name`；
- `label`；
- `title_field_name`；
- `description_field_name`；
- `active`。

配置校验失败必须显示明确错误，不能静默保存为可用配置。候选字段可以由元数据提供，但候选不自动启用。

### 5.6 菜单和动作

菜单结构：

```text
Evidence Album
├── Albums
└── Configuration
    └── Evidence Sources
```

需要定义标准 `ir.actions.act_window`：

- Album 列表/表单动作；
- Source Config 列表/表单动作；
- Page/Item 作为 Album/Page 内嵌管理，不要求独立顶级菜单。

具体 XML ID、菜单序号和父菜单 ID 在实现时按模块内部命名规范确定；若需要被其他模块引用，必须在 CC-01 关闭材料中登记。

### 5.7 状态和跨相册 UI 门禁

- 普通编辑器不能直接编辑 `state`；
- Page 编辑器不提供跨 Album 移动操作；
- 排序操作只作用于当前 Album 或当前 Page；
- UI 隐藏不能替代 ORM 约束和权限检查。

---

## 6. 验收条件

以下断言对应 Implementation Plan §2.4 的 9 条验收条件。这里只规定断言和验证手段，不定义测试用例。

### AC-01 模块可安装且无具体来源依赖

- **断言**：模块可以被 Odoo 18 安装；manifest 只依赖 `base`、`mail`、`portal`、`web`；不依赖任何具体来源业务模块。
- **验证方式**：Odoo 模块安装/升级验证；检查 manifest 依赖清单和 CI 依赖扫描结果。
- **追溯**：SRS §0、§1.3；TDD §1.1、§14；Implementation Plan §2.4 条件 1、CC-01-T01。

### AC-02 四个模型和关系符合 TDD

- **断言**：四个技术模型、字段、关系、ondelete、派生字段和索引与本 CC §3/TDD §2 一致。
- **验证方式**：ORM 元数据检查、模型加载检查和关系结构审阅。
- **追溯**：SRS §4；TDD §2；Implementation Plan §2.4 条件 2、CC-01-T02 至 T05。

### AC-03 删除不删除原始附件

- **断言**：删除 Page 或 Item 后，原始 `ir.attachment` 仍存在；附件删除后 Item 保留并变为不可用。
- **验证方式**：ORM 生命周期验证和删除策略审阅；不使用数据库客户端或裸 SQL。
- **追溯**：SRS §1.3、§15.2；TDD §2.3、§2.4；Implementation Plan §2.4 条件 3、CC-01-T03/T04。

### AC-04 `album_id` 派生和一致性有效

- **断言**：Item 的 `album_id` 由 `page_id.album_id` 派生且不可独立编辑；不一致写入被拒绝；Page 跨 Album 移动被拒绝。
- **验证方式**：ORM 字段属性检查、业务约束验证和模型写入边界审阅。
- **追溯**：SRS §4.2、§15.5；TDD §2.4、TD-003；Implementation Plan §2.4 条件 4、CC-01-T04。

### AC-05 同一附件同一 Album 不重复

- **断言**：同一 `attachment_id` 在同一 Album 的不同 Page 中也不能重复；不同 Album 可以分别引用同一附件。
- **验证方式**：数据库唯一约束元数据检查、ORM 业务检查和并发保护审阅。
- **追溯**：SRS §15.5、§18 AC-29；TDD §2.4、TD-003；Implementation Plan §2.4 条件 5、CC-01-T04。

### AC-06 排序边界有效

- **断言**：Page 只能在同一 Album 内调整顺序；Item 只能在同一 Page 内调整顺序；跨 Album 移动 Page 被拒绝。
- **验证方式**：后台视图操作验证、ORM 写入约束审阅和排序字段检查。
- **追溯**：SRS §4.2、§7.5、§18 AC-10/11/30；TDD §2.3、§10；Implementation Plan §2.4 条件 6、CC-01-T03/T07。

### AC-07 后台角色权限符合 SRS

- **断言**：业务用户、审核人、管理员的模型 ACL、Record Rule 和后台界面权限符合 SRS §9；业务用户只能管理自己的 Album。
- **验证方式**：Odoo ACL/Record Rule 元数据检查、真实角色访问验证和权限矩阵审阅。
- **追溯**：SRS §9；TDD §11；Implementation Plan §2.4 条件 7、CC-01-T06。

### AC-08 Source Config 不自动暴露所有候选字段

- **断言**：元数据候选字段只能显示为候选；只有管理员显式启用的配置可供后续 CC-02 使用；CC-01 不自动暴露所有 Many2many 附件字段。
- **验证方式**：配置模型约束、后台界面和启用状态审阅；不执行 CC-02 实际来源读取。
- **追溯**：SRS §4.4、§5；TDD §2.5、§3；Implementation Plan §2.4 条件 8、CC-01-T05/T07。

### AC-09 CC-01 关闭材料形成

- **断言**：IHR、ATR、HVR 和 FR 草稿四类关闭材料均已形成，并区分已验证、未验证和被阻塞部分。
- **验证方式**：关闭材料清单审阅和 CC 评审。
- **追溯**：Implementation Plan §2.3 CC-01-T08、§8；项目 Workflow。

---

## 7. 关闭材料清单

### 7.1 IHR — Interface Handover Record

IHR 至少包含：

- 四个模型的模型名、字段、类型、必填和关系；
- Page/Item/Attachment 的删除策略；
- `album_id` 派生和 `availability_state` 刷新边界；
- Album 业务动作方法签名、状态接口和 CC-03 延后项；
- 三个后台组及其继承关系；
- ACL 行和 Record Rule 清单；
- 视图、菜单和动作 XML ID 清单；
- CC-02 需要调用的 Source Config 字段校验接口。

### 7.2 ATR — Automated Test Record

ATR 记录本 CC 的自动化验收结果，至少覆盖以下测试类型：

- ORM 模型字段和关系；
- SQL/Python 约束；
- `album_id` 派生和跨 Album 拒绝；
- 附件删除和 Item 保留；
- 同 Album 附件唯一性；
- ACL 和 Record Rule；
- 视图动作和模块安装/升级。

本 CC 不写具体测试代码或测试用例；ATR 记录的是“哪些测试类型被执行、结果如何、证据在哪里”，而不是测试代码本身。测试代码由后续 CC 或独立测试任务编写。ATR 只记录执行结果、证据位置和失败项。

### 7.3 HVR — Human Verification Record

HVR 至少记录人工验证：

- 模块安装和后台菜单进入；
- Album/Page/Item 表单字段和只读状态；
- Page/Item 排序；
- 跨 Album 移动被拒绝；
- 不同后台角色的可见和可编辑范围；
- Source Config 候选/启用界面；
- 证据类型包括截图、日志和手工步骤记录。

### 7.4 FR — Feature Record 草稿

FR 草稿至少包含：

- CC-01 完成范围；
- 对应验收条件逐项状态；
- 已验证部分；
- 未验证部分；
- 被 TDD-Q-008 或其他待确认项阻塞的部分；
- 遗留问题和进入 CC-02 的前置条件；
- 是否建议进入下一 CC。

每个 CC 的关闭材料必须包含 IHR、ATR、HVR 和 FR 四类。没有证据的内容必须标记为未验证，不得写成通过。

---

## 8. 未解决项和风险

### 8.1 待确认项

| 项目 | CC-01 处理 |
|---|---|
| TDD-Q-008 | CC-01 结束前解决或形成验证证据；未解决则阻塞 CC-02 来源采集部分，但不阻塞直接上传 |
| TDD-Q-001 | 不阻塞 CC-01；CC-03-T03 前解决 |
| TDD-Q-002 | 不阻塞 CC-01；CC-02-T02 前解决 |
| TDD-Q-003 | 不阻塞 CC-01；CC-04 Portal 数据结构前解决 |
| TDD-Q-004 | 不阻塞 CC-01；CC-05 开始前解决 |
| TDD-Q-007 | 不阻塞 CC-01；CC-04-T05 前解决 |

### 8.2 风险清单

| 风险 | 影响范围 | 缓解方式 | 责任方 |
|---|---|---|---|
| Odoo Registry 中没有可用于来源验证的模型 | CC-02 来源采集 | CC-01 结束前使用专用测试模型或真实上游模块完成 TDD-Q-008 验证；生产代码不耦合测试模型 | 技术负责人 |
| `album_id` related 存储字段与 `page_id` 写入不一致 | Item 唯一性、权限和后续 Controller | 集中在 Item 模型同步并拒绝不一致写入；以数据库唯一约束兜底 | 技术负责人 |
| 并发创建相同附件 Item | SRS 附件唯一性 | Python 提前检查 + 数据库唯一约束 + 明确异常转换；数据库唯一约束触发的异常必须转换为用户可理解的业务错误，不向用户暴露 PostgreSQL 原始异常 | 技术负责人 |
| `ondelete="set null"` 未覆盖所有附件删除路径 | Item 可用性和审计 | Item 模型集中刷新可用性；ORM 生命周期验证；不允许视图自行维护状态 | 技术负责人 |
| Record Rule 组合过宽或过窄 | 后台数据泄露或业务用户无法工作 | 使用真实角色验证，按最小权限修正；Portal 不依赖后台 Record Rule | 技术负责人 + 测试负责人 |
| CC-03 动作按钮提前出现但动作未实现 | 后台用户误操作 | CC-01 只建立稳定接口/视图位置；按钮按状态和权限控制，动作行为由 CC-03 接管 | 技术负责人 |
| 项目版本号或 XML ID 规范未确认 | 安装升级和后续引用 | 在 CC-01 关闭前记录最终清单；未确认项不得被其他模块依赖 | 技术负责人 |

---

## 附录 A：追溯矩阵

| 契约 | SRS | TDD | Implementation Plan |
|---|---|---|---|
| 模块骨架和依赖 | §1.3 | §1.1、§14 | §2.3 CC-01-T01 |
| Album 字段和 `customer_id` Commercial Partner 规范化 | §4.1、§9 | §2.2、§6.2、§11 | §2.3 CC-01-T02 |
| Album 状态字段和动作接口 | §10.1 | §2.2、§5 | §2.3 CC-01-T02 |
| Page 所属 Album 和同 Album 排序 | §4.2、§7.5 | §2.3、§10 | §2.3 CC-01-T03/T07 |
| Item `page_id` 和 `album_id` 派生一致性 | §4.3、§15.5 | §2.4、TD-003 | §2.3 CC-01-T04 |
| Item 附件删除后保留 | §1.3、§15.2 | §2.4、TD-004 | §2.3 CC-01-T04 |
| 同 Album 附件唯一性 | §15.5、§18 AC-29 | §2.4、TD-003 | §2.3 CC-01-T04 |
| Source Config 显式允许列表 | §4.4、§5 | §2.5、§3、TD-005 | §2.3 CC-01-T05 |
| 业务用户、审核人、管理员权限 | §9 | §11 | §2.3 CC-01-T06 |
| Album/Page/Item 后台视图 | §7.1、§7.5、§7.6 | §10 | §2.3 CC-01-T07 |
| CC-01 关闭材料 | §18 | TDD §15、项目 Workflow | §2.3 CC-01-T08、§8 |

---

## 附录 B：CC-01 明确不承诺的接口

以下接口只允许在后续 CC 中实现，本 CC 不得提前扩大：

- Source Resolver 的真实来源记录读取行为：CC-02；
- 上传入口和媒体合法性采集：CC-02；
- 状态动作的完整业务实现、Token 和有效期：CC-03；
- Portal Access Policy 和 `sudo()` 媒体 Controller：CC-04；
- OWL 查看器和缩略图：CC-04；
- ZIP Builder 和批量下载：CC-05。
