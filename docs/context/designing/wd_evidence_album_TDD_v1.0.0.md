# WMS Evidence Album — Technical Design Document (TDD) v1.0.0

## 0. 文档信息

| 项目 | 内容 |
|---|---|
| 模块名 | `wd_evidence_album` |
| 中文名 | WMS 客户证据相册 |
| TDD 版本 | v1.0.0 |
| 状态 | Frozen Implementation Baseline |
| Odoo | 18.0 Community Edition |
| Python 环境 | `/Users/lijianqiang/Documents/odoo18_album/venv` |
| 上游业务基线 | `wd_evidence_album_SRS_v1.0.0.md`（Frozen） |
| 技术验证输入 | `wd_evidence_album_TV_v1.0.0.md`（v1.0.0） |
| 项目认知输入 | `wd_evidence_album_Cognition_v1.0.0.md` |
| 依赖 | `base`、`mail`、`portal`、`web` |

### 0.1 文档定位

本文档把 SRS 的业务契约和 TV Report 已验证的 Odoo 18 技术事实转换为实现设计。它决定模型、授权边界、Controller、前端和技术约束，但不包含完整代码、实施任务、排期或测试用例。

### 0.2 追溯规则

本文档使用以下引用：

- **SRS §x.y**：业务范围、规则、状态和验收要求；
- **TV-01 至 TV-05**：Odoo 18 技术验证事实；
- **Cognition §x**：项目共同认知，仅作导航，不改变 SRS 权威语义。

若 TDD 与 SRS 的业务语义发生冲突，必须回到 SRS 修订；TDD 不得自行改变冻结需求。

---

## 1. 架构概览

### 1.1 模块定位

模块位于 `ir.attachment` 与客户 Portal 之间：

- 上游 Media Widget 或其他业务功能产生附件；
- 本模块通过已配置来源字段选择附件，或创建直接上传附件；
- 本模块建立 Album/Page/Item 的整理、审核和发布边界；
- Portal 通过本模块的授权 Controller 查看和下载，不直接暴露附件默认内容路由。

模块不 import、不 inherit 任何 `wd_qooling.*` 模型。来源模型只通过 `ir.model` / `ir.model.fields` 配置和运行时字段名解析。

### 1.2 逻辑架构

```text
┌──────────────────────────────┐
│ Media Widget / 业务模型       │
│ 业务记录 + ir.attachment       │
└──────────────┬───────────────┘
               │ 已配置来源字段
               ▼
┌──────────────────────────────┐
│ wd_evidence_album             │
│ Album                         │
│  ├─ Page                      │
│  │   └─ Item → ir.attachment │
│  ├─ Source Configuration      │
│  └─ Review / Publish Policy   │
└──────────────┬───────────────┘
               │ 授权后的自定义 HTTP
               ▼
┌──────────────────────────────┐
│ Authenticated Customer Portal │
│ List / Viewer / Media / ZIP   │
└──────────────────────────────┘
```

### 1.3 分层职责

| 层 | 职责 |
|---|---|
| ORM Model | 数据关系、状态动作、约束、来源快照和后台权限承载 |
| Source Resolver | 解析来源配置、校验动态字段、读取来源附件 |
| Album Business Actions | 创建相页、采集媒体、审核、发布、撤销和重置 Token |
| Portal Access Policy | 登录、Portal 角色、Commercial Partner、发布和有效期判断 |
| Media Controller | 授权后读取附件并返回媒体流或下载 |
| ZIP Builder | 在请求期间校验、限制和生成临时 ZIP |
| QWeb/OWL Frontend | 展示列表、查看器、媒体交互和选择状态 |

### 1.4 冻结设计原则

以下原则直接继承 **SRS §1.3**：

1. 不复制附件，只引用 `ir.attachment`；
2. 不耦合 `wd_qooling.*`；
3. 不写死来源字段名；
4. 不绕过 Portal 权限；
5. ZIP 请求时生成，不长期保存；
6. 相册是独立证据集合，不是实时业务记录视图；
7. 删除相册项不删除原始附件，原始附件删除后 Item 保留为不可用；
8. Token 不提供独立授权。

实现默认采用 Odoo Native First、Simple Models、Explicit Business Logic 和 Robust Before Clever（Cognition §10）。

---

## 2. 数据模型设计

### 2.1 模型关系

```text
wd.evidence.album
        │ 1 ─── N
        ▼
wd.evidence.album.page
        │ 1 ─── N
        ▼
wd.evidence.album.item ─── N:1 ─── ir.attachment
        │
        └── source_model + source_record_id + source_field_name

wd.evidence.album.source.config
        ├── N:1 ir.model
        └── title_field_name / description_field_name
```

Page 不保存来源记录关系；来源关系只保存在 Item 上。这直接落实 **SRS §4.2、§4.3 和 §6.2**。

### 2.2 `wd.evidence.album`

| 字段 | 类型 | 必填 | 设计和约束 |
|---|---|---:|---|
| `name` | `Char` | 是 | 相册名称；创建时必填，后台可编辑 |
| `customer_id` | `Many2one(res.partner)` | 是 | 业务上保存 Commercial Partner；创建/写入时规范化 |
| `description` | `Text` | 否 | 相册描述 |
| `state` | `Selection` | 是 | `draft`、`pending_review`、`approved`、`published`、`revoked`；默认 `draft` |
| `token` | `Char` | 否 | 发布时生成，唯一、索引、不可作为独立授权 |
| `valid_until` | `Datetime` | 否 | 可选过期时间；过期不是状态 |
| `published_at` | `Datetime` | 否 | 发布动作写入 |
| `revoked_at` | `Datetime` | 否 | 撤销动作写入 |
| `reviewed_by` | `Many2one(res.users)` | 否 | 审核通过或拒绝时写入审核人 |
| `page_ids` | `One2many(wd.evidence.album.page)` | 否 | 相册内相页，按 `sequence` 排序 |

设计说明：

- `customer_id` 采用 `Many2one` 而不是联系人字符串，保证 Portal 授权使用 Odoo Partner 关系；
- `token` 只用于 URL 标识，Controller 永远不能仅凭 Token 放行；
- `state` 只由显式业务动作改变，禁止通过普通 `write` 任意跳转；
- `reviewed_by` 记录审核责任人，不承担 Portal 授权。

关系和删除策略：

- Page 的 `album_id` 使用 `Many2one`，相册删除时级联删除 Page；
- 相册删除时级联删除 Page 和 Item，但不得删除 Item 引用的 `ir.attachment`；
- 已发布相册禁止直接删除，必须先撤销或由管理员按明确业务策略处理；
- `token` 建立唯一索引，允许草稿为空；每次重置生成新值并使旧 URL 失效。

建议索引：

- `state`；
- `customer_id`；
- `token` 唯一索引；
- `valid_until`（用于列表和访问过滤）。

### 2.3 `wd.evidence.album.page`

| 字段 | 类型 | 必填 | 设计和约束 |
|---|---|---:|---|
| `album_id` | `Many2one(wd.evidence.album)` | 是 | 所属相册；不可跨相册移动 |
| `title` | `Char` | 是 | 相页标题 |
| `description` | `Text` | 否 | 相页描述 |
| `sequence` | `Integer` | 是 | 相册内排序号，默认递增值 |
| `item_ids` | `One2many(wd.evidence.album.item)` | 否 | 相页媒体项，按 `sequence` 排序 |

设计说明：

- Page 只负责组织和展示，不保存来源模型、来源记录或来源字段；
- 从记录创建 Page 时，标题、描述和 Item 一次性填充，之后与来源记录脱钩；
- `album_id` 变更必须检查目标相册与原相册相同；不同相册直接拒绝；
- 删除 Page 级联删除 Item 记录，但不删除附件。

建议索引：

- `(album_id, sequence)`；
- 必要时对 `album_id` 建普通索引，以支持后台和 Portal 查询。

### 2.4 `wd.evidence.album.item`

| 字段 | 类型 | 必填 | 设计和约束 |
|---|---|---:|---|
| `page_id` | `Many2one(wd.evidence.album.page)` | 是 | 所属相页 |
| `album_id` | `Many2one(wd.evidence.album)` | 是 | 从 Page 存储关联得到的技术字段，用于跨页唯一性和授权查询 |
| `attachment_id` | `Many2one(ir.attachment)` | 否 | 原始附件引用；`ondelete="set null"`，以保留附件删除后的 Item |
| `source_type` | `Selection` | 是 | `record` 或 `upload` |
| `source_model` | `Char` | 条件必填 | `record` 时保存来源模型名 |
| `source_record_id` | `Integer` | 条件必填 | `record` 时保存来源记录 ID |
| `source_field_name` | `Char` | 条件必填 | `record` 时保存实际来源字段名 |
| `media_type` | `Selection` | 是 | `image` 或 `video` |
| `sequence` | `Integer` | 是 | 相页内排序号 |
| `note` | `Text` | 否 | 客户可见的媒体说明 |
| `availability_state` | `Selection` | 是 | `available` 或 `unavailable` |

设计说明：

- `album_id` 是从 `page_id.album_id` 派生的存储型相关字段，不改变领域关系；它让 `(album_id, attachment_id)` 可以用数据库唯一约束表达；
- `album_id` 不允许用户独立编辑；写入 `page_id` 时由 Page 的 Album 自动计算并同步；
- `attachment_id` 使用 `set null`，因为 SRS §15.2 要求附件删除后 Item 保留；
- `availability_state` 在附件创建、修改、删除关联和读取前统一刷新；`attachment_id` 为空时必须是 `unavailable`；
- `source_model/source_record_id/source_field_name` 是创建时的追溯快照，不作为 Portal 授权依据；
- `source_type="upload"` 时来源字段全部为空，上传附件不绑定业务单据；
- `media_type` 只能由通过 MIME、扩展名和内容可读性校验的 JPG/JPEG/PNG/MP4 产生。

删除策略：

- Item 删除只删除 Item；
- `attachment_id` 对原始附件使用 `set null`；
- 不允许 Item 的删除动作调用附件 unlink；
- Page 删除 Item 使用级联关系，但保留附件。

约束和索引：

- 数据库唯一约束：非空附件的 `(album_id, attachment_id)` 唯一；空附件不参与重复约束；
- 业务约束：Item 的 Page 必须属于 Item 的 Album；
- 一致性约束：`item.page_id.album_id == item.album_id` 必须始终成立；
- 写入 `page_id` 时必须同步派生 `album_id`；如果提交值与 `page_id.album_id` 不一致，写入必须被拒绝；
- Page 移动到其他 Album 的操作必须被拒绝，不能依赖存储型相关字段事后修复不一致；
- `(page_id, sequence)` 索引；
- `(album_id, attachment_id)` 唯一索引；
- `availability_state` 与附件存在性不一致时，业务动作必须拒绝或重新计算。

### 2.5 `wd.evidence.album.source.config`

| 字段 | 类型 | 必填 | 设计和约束 |
|---|---|---:|---|
| `model_id` | `Many2one(ir.model)` | 是 | 配置的来源模型 |
| `field_name` | `Char` | 是 | 指向 `ir.attachment` 的 Many2many 字段名 |
| `label` | `Char` | 是 | 后台选择时显示的标签 |
| `title_field_name` | `Char` | 否 | 相页标题映射字段 |
| `description_field_name` | `Char` | 否 | 相页描述映射字段 |
| `active` | `Boolean` | 是 | 是否允许使用，默认启用 |

约束：

- `(model_id, field_name)` 唯一；
- 保存和启用时验证模型存在、字段存在、`ttype="many2many"`、`relation="ir.attachment"`；
- 标题和描述字段存在时验证属于同一模型并允许读取；
- 停用配置不影响已经创建的 Item，但不允许继续创建新的来源 Item；
- 配置删除采用停用优先；若已有 Item 引用，删除应被拒绝。

设计理由：

- 使用 `ir.model` 关系而不是硬编码模型名，避免直接耦合任意具体业务模块；
- 保留字符串字段名，因为运行时访问必须使用解析出的真实字段名；
- 配置是“允许列表”，候选字段元数据发现不等于自动暴露。

---

## 3. 证据来源字段发现机制

### 3.1 发现流程

1. 根据 `model_id.model` 找到目标 Odoo 模型元数据；
2. 查询 `ir.model.fields`；
3. 过滤 `model_id`、`ttype="many2many"`、`relation="ir.attachment"`；
4. 将候选字段显示给管理员；
5. 管理员创建或启用 `source.config` 后，字段才成为合法来源；
6. 每次使用配置前重新确认字段仍存在且配置有效。

候选发现不自动创建配置，也不向 Portal 暴露候选字段。这对应 **SRS §5.1、§5.4**。

### 3.2 配置校验

配置创建、修改和启用时必须校验：

- `ir.model` 记录存在；
- 模型当前在 Odoo Registry 中可用；
- 字段名存在于该模型；
- 字段类型为 `many2many`；
- relation 精确为 `ir.attachment`；
- 当前后台用户可读取来源模型和来源字段；
- 标题字段若配置，必须存在且适合文本读取；
- 描述字段若配置，必须存在且适合文本读取；
- 配置处于启用状态。

来源字段读取前还必须对选定来源记录执行普通 ORM 权限检查。不得因为之后需要读取附件而提前 `sudo()`。

### 3.3 动态访问

解析配置后，运行时使用字段名访问：

```text
record[field_name]
```

多记录场景必须明确逐记录处理或使用 `mapped(field_name)`，不能依赖 `record[field_name]` 对多记录的隐式行为。读取结果必须是 `ir.attachment` Recordset，并逐个执行媒体合法性校验。

### 3.4 多字段和缓存

- 同一模型允许存在多条启用配置；
- 创建相页或添加媒体时，用户必须先选择具体配置；
- 配置选择界面使用当前数据库查询结果；
- 可以使用进程内短生命周期缓存减少重复元数据查询，但缓存键必须包含数据库、模型和字段名；
- 配置写入、停用、模块升级或 Registry 重载后必须失效相关缓存；
- 缓存只缓存元数据，不缓存权限结论、业务记录或附件内容；
- 第一版不引入独立 Redis 或持久化缓存。

### 3.5 TV-03 对设计的限制

根据 **TV-03**：

- `ir.model` / `ir.model.fields` 的候选发现已通过真实 ORM 验证；
- `record[field_name]` 的 Odoo API 契约成立；
- TV 使用了当前数据库中已有的一个业务模型字段作为探针样本，但该样本只是验证材料，不是本模块的依赖、默认配置或代码耦合对象；
- 当前环境没有可用于完整运行时读取的来源业务记录，因此真实 `record[field_name]` 读取尚未完成；
- 当前用户的来源记录 ACL、空字段、多记录和配置失效行为仍需集成验证。

没有任何具体来源模型或来源数据时，模块仍可独立开发和安装。缺少来源模型只会阻塞“从该来源记录采集媒体”的集成验证，不阻塞 Album/Page/Item、直接上传、审核发布、Portal 和 ZIP 等功能。实施阶段可以使用专用测试模型或已安装的真实上游业务模块验证动态读取，但生产模块不得 import 或 inherit 该测试模型。

---

## 4. 相册创建与媒体采集设计

### 4.1 手工相页

1. 用户在草稿相册中填写标题和可选描述；
2. 系统创建 Page，绑定当前 Album；
3. 用户通过来源配置选择媒体，或使用直接上传；
4. 媒体建立 Item 引用；
5. 用户可继续编辑 Page 标题和描述。

Page 创建不要求绑定来源记录。

### 4.2 从记录创建相页

1. 用户选择启用的来源配置；
2. 系统验证当前用户可读取目标来源记录；
3. 系统读取配置的标题字段和描述字段；
4. 系统动态读取配置的附件字段；
5. 对每个附件执行类型、空内容、权限和重复校验；
6. 创建 Page 和 Item；
7. 把标题、描述和 Item 作为初始值写入；
8. 用户可以覆盖标题和描述；
9. 完成后只保留 Item 的追溯快照，不保留 Page 到来源记录的持续绑定。

如果标题或描述没有配置，使用 SRS §6.3 允许的默认推导规则；具体默认字段优先级属于“待确认”，在 TDD 冻结前必须确定，不能在实现中静默猜测。

### 4.3 从业务记录添加媒体

- 用户在既有 Page 中选择来源配置和来源记录；
- 普通 ORM 环境读取记录和字段；
- 只接受配置字段返回的附件；
- 每个附件必须存在、非空、类型合法且当前附件不在同一 Album；
- 创建 Item 时保存 `source_model`、`source_record_id` 和 `source_field_name`；
- 来源记录后续新增附件不会自动同步。

### 4.4 直接上传

- 用户在后台 Page 上上传单个或多个图片/视频；
- 系统先校验 MIME、扩展名、内容可读性和大小边界；
- 创建不绑定业务模型的 `ir.attachment`；
- 创建 `source_type="upload"` 的 Item；
- 上传附件只由 Item 引用，不设置业务单据归属；
- Item 删除时不得删除该附件。

直接上传的附件归属策略对应 **SRS §15.4**。上传失败或 Item 创建失败时，事务必须回滚，避免形成不可追踪附件。

### 4.5 附件唯一性

唯一性以 Album 为边界，而不是 Page：

```text
同一 Album + 同一 attachment_id = 禁止重复
```

使用 Item 的存储型 `album_id` 和数据库唯一约束作为最终保护，同时在业务动作中提前检查并返回明确错误。并发创建以数据库约束作为最后一道保护。

---

## 5. 审核与发布设计

### 5.1 状态技术映射

| SRS 状态 | 技术值 | 允许进入 |
|---|---|---|
| 草稿 | `draft` | 创建、审核拒绝 |
| 待审核 | `pending_review` | 草稿提交审核 |
| 已审核 | `approved` | 审核人批准 |
| 已发布 | `published` | 已审核发布 |
| 已撤销 | `revoked` | 已发布撤销 |

只有显式业务动作可以改变 `state`。普通表单写入不得直接写入任意状态值。

### 5.2 动作规则

- `action_submit_review`：仅草稿可执行；
- `action_approve`：仅待审核可执行，写入 `reviewed_by`；
- `action_reject`：仅待审核可执行，回到草稿并保留审核人；
- `action_publish`：仅已审核可执行，发布前重新校验客户、Page、Item、媒体和权限；
- `action_revoke`：仅已发布可执行，写入 `revoked_at`；
- `action_reset_token`：后台授权用户可执行，生成新 Token，旧 Token 立即失效。

### 5.3 发布前检查

发布动作必须验证：

- 状态为 `approved`；
- 客户存在并已规范化；
- 至少有一个有效 Page/Item（是否允许空相册发布需在 SRS 待确认项中明确）；
- 所有 Item 的附件存在、可用、媒体类型合法；
- 同一 Album 无重复附件；
- 审核人已记录；
- 有效期若设置则有效；
- 当前操作用户具有发布权限。

“空相册是否允许发布”是 SRS 当前未明确的行为，标记为 **SRS 待补充项**，在 TDD 冻结前必须确认。

### 5.4 Token

- 使用密码学随机源生成不可预测 Token；
- Token 只存储相册 URL 标识，不参与独立授权；
- 不在 Portal 路由中仅凭 Token 放行；
- Controller 仍必须要求登录、Portal 角色、Commercial Partner、发布状态、撤销和有效期均通过；
- Token 只在发布或显式重置时生成/替换；
- 草稿和撤销相册可以保留历史值，但访问检查必须拒绝；
- Token 字段不可在普通后台表单中任意编辑。

### 5.5 有效期

`valid_until` 为空表示未设置有效期；非空时按当前服务器时间判断：

```text
now < valid_until  => 未过期
now >= valid_until => 已过期
```

过期不改变 `state`，只在列表、查看器、媒体和 ZIP 的访问策略中拒绝。

---

## 6. Portal 访问控制设计

### 6.1 Portal 用户识别

Controller 使用 Odoo 当前请求用户：

1. 路由认证为 `auth="user"`；
2. 显式检查 `base.group_portal`；
3. 非 Portal 后台用户不通过客户 Portal 路由访问；
4. 未登录请求由 Odoo 认证层拦截。

这对应 **TV-01** 的 `auth="user"` 结论和 **SRS §8.2**。

### 6.2 Commercial Partner 策略

相册写入时将 `customer_id` 规范化为：

```text
customer_id.commercial_partner_id
```

读取时仍再次归一化双方，使用：

```text
album.customer_id.commercial_partner_id
==
request.env.user.partner_id.commercial_partner_id
```

写入规范化减少数据分歧，读取归一化防御历史数据和手工数据。

### 6.3 完整授权链

所有 Portal 相册列表、查看器、媒体、单文件下载和 ZIP 请求共用同一个授权策略：

1. 当前请求已认证；
2. 当前用户属于 Portal 组；
3. Album 存在；
4. Album 的客户 Commercial Partner 与当前用户 Commercial Partner 相同；
5. Album 状态为 `published`；
6. `revoked_at` 为空；
7. `valid_until` 为空或尚未过期；
8. Item/Page 属于该 Album；
9. Item 的媒体可用；
10. 对媒体执行操作前完成以上业务授权。

### 6.4 `sudo()` 边界

授权检查必须在任何 `sudo()` 附件读取之前完成：

```text
普通 env 查询 Album/Page/Item
→ 普通 env 完成 Portal/Commercial Partner/状态/有效期校验
→ 普通 env 确认 Item 媒体可用
→ 只对已确认的 attachment_id 使用 sudo() 读取二进制流
→ 返回已授权的媒体响应
```

禁止：

- 先 `sudo()` 按附件 ID 查询，再尝试补授权；
- 直接以 Token 或 `attachment_id` 作为授权；
- 在 Portal Controller 中重新检查来源业务记录 ACL。

### 6.5 TV-02 对应

**TV-02** 已确认 Commercial Partner 逻辑能够覆盖同一公司的多个 Portal 联系人；当前数据库只有一个 Portal 用户样本，因此多联系人真实 ACL 行为仍需集成验证。TDD 采用“写入规范化 + 读取归一化”的双层策略。

---

## 7. 媒体访问设计

### 7.1 路由资源标识

媒体路由使用 `item_id`，不使用只带 `attachment_id` 的公开资源路由：

```text
/my/evidence-albums/items/<int:item_id>/media
```

这样 Controller 可以先确认 Item 属于某个已授权 Album，再读取其附件，降低 ID 枚举和跨相册引用风险。

### 7.2 授权前置流程

1. 使用普通请求环境按 Item 查询；
2. 检查 Item、Page、Album 关系；
3. 执行完整 Portal 授权链；
4. 检查 `availability_state` 和 `attachment_id`；
5. 检查媒体类型允许值；
6. 取得已授权的附件 ID；
7. 仅此时使用 `sudo()` 读取附件二进制流；
8. 构造响应。

### 7.3 响应方式

- 图片返回 `image/jpeg`、`image/png` 等准确 MIME；
- 视频返回 `video/mp4`；
- 设置 `Content-Length`、安全的 `Content-Disposition` 和缓存策略；
- 预览响应为 inline，下载响应为 attachment；
- 不调用默认 `/web/content` 作为媒体授权路由；
- 不把附件的原始 URL 直接交给 Portal。

### 7.4 视频 Range

V1 必须支持 HTTP Range。视频拖动播放依赖 Range；对大 MP4 进行无条件全量加载不符合 SRS §12 的低成本预览和性能要求。

媒体 Controller 设计为：

- 读取 `Range` 请求头；
- 返回部分内容时使用 `206 Partial Content`；
- 设置 `Accept-Ranges: bytes`、`Content-Range` 和准确长度；
- 无效范围返回 `416 Range Not Satisfiable`；
- 无 Range 时返回完整流；
- HEAD 请求如实现，必须复用授权链并只返回响应头。

TV-01 只验证了图片/视频 HTTP 响应原语，真实浏览器 Range 播放尚未验证。因此 Range 是 V1 的技术设计要求，但必须在实施阶段集成验证；不能把 TV 的流响应验证扩大解释为浏览器播放已通过。

### 7.5 媒体不可用

- `attachment_id` 为空或附件 `.exists()` 失败时，返回 404；
- 不返回原始来源信息或附件存在性细节；
- Item 保留为 `unavailable`，后台可见并可删除/整理；
- ZIP 中跳过不可用 Item 或整体拒绝，具体策略统一为：请求中包含不可用 Item 时返回明确业务错误，避免客户得到不完整 ZIP。

该 ZIP 行为是 TDD 的技术一致性选择，不改变 SRS 的“不可用媒体不能下载”；如需“自动跳过”必须先补充 SRS。

### 7.6 TV-01 对应

TV-01 证明了默认 `/web/content` 会执行附件权限检查，也证明自定义 Controller 可以在业务授权后使用 `sudo()`。因此本设计将 Album 授权放在 `sudo()` 前，并使用 Item ID 而不是单独 Attachment ID。

---

## 8. ZIP 下载设计

### 8.1 生成方式

ZIP 请求只在 HTTP 请求期间生成：

1. 接收 Item ID 集合；
2. 去重并验证数量上限；
3. 对每个 Item 执行同一 Portal 授权链；
4. 验证 Item 所属 Album、可用性和媒体类型；
5. 读取附件内容并累计总大小；
6. 文件名清洗并确保 ZIP 内唯一；
7. 使用内存流和标准 ZIP 生成器写入；
8. 返回 `application/zip` 附件响应；
9. 请求结束后释放内存，不保存附件或 ZIP 文件。

### 8.2 限制

最大文件数量和最大总大小是配置项，不在本 TDD 中擅自确定具体数值。配置必须有有限、非零的默认值，并由管理员可见。

限制检查必须在读取全部文件前完成：

- 选中数量超过上限，立即返回业务错误；
- 累计原始文件大小超过上限，立即停止；
- 不允许通过压缩率绕过原始总大小限制。

如果数据库字段没有可信文件大小，必须在读取附件之前使用可获得的附件元数据；无法可靠估算时应拒绝生成，而不是无界读取。

### 8.3 文件名清洗

- 仅使用安全 basename；
- 删除路径分隔符、控制字符和不可接受的保留字符；
- 空名称使用稳定的 Item 序号和扩展名；
- 同名文件添加稳定后缀；
- 不允许 `../`、绝对路径或目录项；
- 文件名清洗不改变原始附件名称字段。

### 8.4 错误处理

- 未登录/非 Portal/跨客户/未发布/已撤销/过期：按统一未授权响应处理；
- 数量超限：返回明确的用户可见业务错误；
- 总大小超限：返回明确的用户可见业务错误；
- Item 不可用：返回明确错误，不生成不完整 ZIP；
- 附件读取失败：记录服务器错误并返回通用失败，不暴露内部路径或堆栈。

### 8.5 资源策略

V1 采用内存 ZIP，不落盘；因此 TDD 必须保留：

- 单请求内存上限；
- 最大并发 ZIP 请求；
- 请求超时；
- 大文件拒绝或分批下载提示。

具体数值是本 TDD 的待确认配置决策，不应在实现中写死。

### 8.6 TV-05 对应

TV-05 已验证 `BytesIO + zipfile.ZipFile` 和 Odoo HTTP 附件响应原语可行，也验证了数量和总大小限制策略。文件名清洗、大文件内存、超时和并发仍需集成和运行时验证；V1 不强制依赖 OCA `attachment_zipped_download`。

---

## 9. 前端设计

### 9.1 Portal 页面

Portal 提供：

- 相册列表页：分页显示已发布、未撤销、未过期相册；
- 相册查看器页：显示相册名称、客户名称、相页和媒体；
- 媒体流/下载由自定义 Controller 提供；
- 页面不把 Token 当作授权依据。

### 9.2 OWL 组件边界

建议组件结构：

```text
AlbumList
└── AlbumViewer
    ├── PageTabs
    ├── MediaFilter
    ├── MediaGrid
    │   ├── ImagePreview
    │   └── VideoPreview
    ├── ImageLightbox
    └── DownloadSelectionBar
```

OWL 只负责：

- 当前相页和媒体类型筛选状态；
- 多选状态；
- 灯箱前后切换；
- 触发单文件或 ZIP 下载；
- 媒体加载失败时显示不可用状态。

核心授权、媒体是否可用和 ZIP 限制必须在 Controller/Model 中完成，不能依赖前端隐藏按钮。

### 9.3 媒体网格和缩略图

- 推荐优先使用 Odoo 原生 `ir.attachment` 图像处理能力生成受授权保护的低成本缩略图变体；
- 如果当前 Odoo 原生能力不足，退回到 Controller 内存实时生成缩略图，并使用短生命周期缓存；
- 图片网格使用自定义媒体 Controller 的缩略图变体或等效低成本预览；
- 列表不无条件加载原始大文件；
- 图片点击后再请求受授权保护的较大预览；
- 视频网格使用低成本 poster/媒体占位展示，不在列表中自动加载完整 MP4；
- 视频播放使用同一授权媒体 Controller；
- 缩略图生成不得创建长期业务附件副本；
- 无论使用原生能力还是内存生成，都必须保留同一授权链、资源边界和不复制附件原则。

视频 poster 若没有可用的 Odoo 原生能力，应使用媒体类型占位而不是引入视频转码；视频转码明确不在 SRS 范围内。

### 9.4 图片灯箱和视频播放

- 图片灯箱支持放大、全屏、上一张/下一张；
- 视频使用原生 `<video controls>`；
- `src` 直接指向自定义媒体路由；
- 媒体路由返回的 Range 行为决定视频拖动和续播体验；
- 访问失败时前端显示不可用，不暴露附件内部详情。

### 9.5 TV-04 对应

TV-04 已验证 Portal 前端资源可以承载 OWL，且 `<img src>` / `<video src>` 可以指向自定义 HTTP 路由。真实 QWeb 挂载点、浏览器播放、灯箱和 Range 行为仍需集成/E2E 验证。

---

## 10. 后台界面设计

### 10.1 相册表单

表单显示：

- 名称、客户、描述；
- 状态、有效期、发布时间、撤销时间；
- 审核人；
- 相页列表；
- 审核、拒绝、发布、撤销、重置 Token 动作；
- 状态不允许通过普通编辑器直接修改。

客户选择显示联系人，但保存时规范化为 Commercial Partner。

### 10.2 相页管理

- Album 表单内使用 One2many 列表和表单管理 Page；
- Page 显示标题、描述、排序号和 Item 数量；
- 支持同一 Album 内拖动或编辑 `sequence`；
- 目标 Album 不在 Page 编辑器中可选；
- 跨 Album 移动由模型约束拒绝。

### 10.3 相册项管理

- Page 内展示缩略图/媒体类型、说明、来源类型、可用性和排序号；
- 允许编辑说明和顺序；
- 允许删除 Item，不显示删除附件的选项；
- 不可用 Item 明确标识；
- 来源追溯字段默认只读。

### 10.4 来源配置界面

管理员界面提供：

- 模型选择；
- 候选附件字段选择；
- 标签；
- 标题字段和描述字段选择；
- 启用/停用；
- 配置校验错误。

候选字段由 `ir.model.fields` 动态提供，不能把所有 Many2many 附件字段自动展示为可用来源。

### 10.5 批量操作

允许的批量操作限于 SRS 范围：

- 调整顺序；
- 删除相册项；
- 编辑说明；
- 审核前整理。

批量发布、批量撤销或批量跨相册移动不在 SRS 范围内，不在本 TDD 添加。

---

## 11. 权限设计

### 11.1 后台组

建议建立以下模块组：

- `group_album_user`：WMS 业务用户；
- `group_album_reviewer`：审核人；
- `group_album_manager`：管理员。

组之间的继承关系只授予明确的 SRS 权限，不让普通用户继承发布权限。

### 11.2 ACL

| 对象 | 业务用户 | 审核人 | 管理员 | Portal |
|---|---:|---:|---:|---:|
| Album | 创建/读写自己的 | 创建/读写/审核/发布 | 全部 | 不通过 ORM ACL 直接浏览 |
| Page | 自己相册内 | 全部可管理 | 全部 | Controller 授权读取 |
| Item | 自己相册内 | 全部可管理 | 全部 | Controller 授权读取 |
| Source Config | 只读候选 | 只读/使用 | 管理 | 无 |

### 11.3 Record Rule

- 业务用户只能读取和修改自己创建的 Album；“自己的”以 `create_uid` 为技术归属；
- Page/Item 通过所属 Album 继承同一归属边界；
- 审核人可访问需审核和已发布 Album；
- 管理员绕过所有模块业务记录限制；
- Portal 用户不依赖业务记录 Record Rule 获得媒体；Portal Controller 使用独立授权策略；
- 来源记录的读取必须使用当前后台用户普通权限，不能通过相册模块替代业务模型权限。

### 11.4 审核/发布门禁

- 业务用户没有审核、发布和撤销权限；
- 审核人可以批准/拒绝/发布；
- 管理员拥有全部动作；
- Model action 方法再次检查组和状态，不能只依赖按钮隐藏。

### 11.5 与 SRS 权限矩阵

该设计落实 **SRS §9**：

- WMS 业务用户：创建、编辑自己的相册；
- WMS 审核人：创建、编辑、审核、发布；
- Portal 客户：仅通过受保护 Portal 查看自己的已发布相册；
- 管理员：全部后台能力；
- Portal 不校验来源业务记录权限，但必须通过 Album Commercial Partner 授权。

---

## 12. 路由设计

| 路由 | 方法 | 认证 | 授权检查 | 返回 | 未授权 | 业务错误 | 服务器错误 |
|---|---|---|---|---|---|---|---|
| `/my/evidence-albums` | GET | `user` | Portal、Commercial Partner、已发布、未撤销、未过期 | Portal HTML | 302 登录 | 404 | 500 |
| `/my/evidence-albums/<album_id>` | GET | `user` | 同上，并校验 Album | Portal HTML | 404 | 404 | 500 |
| `/my/evidence-albums/items/<item_id>/media` | GET/HEAD | `user` | 完整 Album/Item 授权、媒体可用 | 图片/视频流 | 404 | 404 | 500 |
| `/my/evidence-albums/items/<item_id>/download` | GET | `user` | 完整 Album/Item 授权、媒体可用 | 单文件下载 | 404 | 404 | 500 |
| `/my/evidence-albums/zip` | POST | `user` | 完整 Album/Item 授权、数量/大小限制 | 临时 ZIP | 404 | 400 | 500 |

### 12.1 路由共同规则

- 所有路由显式使用 `auth="user"`；
- 所有路由显式检查 `base.group_portal`；
- 所有路由调用同一 Portal Access Policy；
- Token 不作为独立认证；
- 媒体和下载路由不使用默认 `/web/content`；
- 未授权优先返回 404，避免资源存在性泄露；
- 相册列表的未登录请求由 `auth="user"` 按 Portal 标准重定向到登录页；
- ZIP 数量/大小等可预期业务错误返回 400，资源不存在、不可用或未授权统一按 404 处理；
- 业务错误使用项目统一的用户可见响应，不泄露堆栈、文件路径或来源 ACL 细节。

### 12.2 ZIP 请求形状

ZIP 接收 Item ID 集合，不接收可直接读取的附件 ID 集合。这样授权对象始终是 Album Item，避免攻击者只提交附件 ID 绕过 Album 关系。

---

## 13. 关键设计决策

### TD-001：Item 使用 Item ID 作为媒体资源边界

- **决策**：媒体和下载路由使用 `item_id`，不直接暴露 `attachment_id`。
- **理由**：授权需要先确认 Item → Page → Album 关系；符合 SRS §8.2、§11 和 TV-01。
- **备选**：使用 `/media/<attachment_id>`。
- **未选原因**：仅附件 ID 容易形成 ID 枚举和跨相册引用风险，必须额外反查关系。

### TD-002：相册客户写入和读取均使用 Commercial Partner

- **决策**：写入时规范化，读取时双方再次归一化比较。
- **理由**：满足 SRS §8.2 和 TV-02 的同公司多联系人语义。
- **备选**：只保存联系人并直接比较 partner ID。
- **未选原因**：同一客户公司的其他 Portal 联系人会被错误拒绝。

### TD-003：Item 保存存储型 `album_id`

- **决策**：Item 保留 Page 关系，同时存储相关 Album ID。
- **理由**：支持跨 Page 的 Album 级附件唯一性、索引和 Controller 查询。
- **备选**：只通过 Page 反查并在 Python 中检查重复。
- **未选原因**：无法用数据库唯一约束保护并发重复创建。

### TD-004：附件删除采用 `set null`，Item 保留

- **决策**：`attachment_id` 断开后保留 Item，并标记不可用。
- **理由**：直接落实 SRS §15.2 和设计原则 7。
- **备选**：附件删除时级联删除 Item。
- **未选原因**：会丢失相册整理和审核历史。

### TD-005：来源配置采用显式允许列表

- **决策**：元数据只提供候选，管理员确认后由 Source Config 启用。
- **理由**：满足 SRS §4.4、§5，避免默认暴露所有附件字段。
- **备选**：自动启用全部 Many2many → `ir.attachment` 字段。
- **未选原因**：扩大证据暴露面并违反冻结设计原则。

### TD-006：媒体读取在授权后 `sudo()`

- **决策**：普通环境完成 Album 授权，`sudo()` 只包围已授权附件读取。
- **理由**：TV-01 已验证该边界是自定义 Controller 的安全前提。
- **备选**：整个 Controller 使用 `sudo()`。
- **未选原因**：会在业务授权前失去 Record Rule 保护，造成越权。

### TD-007：ZIP 使用请求期间内存生成

- **决策**：`BytesIO` + 标准 ZIP 生成，不长期落盘。
- **理由**：满足 SRS §8.8、设计原则 5 和 TV-05。
- **备选**：使用 OCA ZIP 模块或持久化 ZIP 附件。
- **未选原因**：V1 需求不需要额外依赖，持久化也违反不长期保存原则。

### TD-008：视频列表使用占位/低成本 poster，不做转码

- **决策**：网格不加载完整 MP4；没有原生 poster 时显示视频类型占位。
- **理由**：满足 SRS §12 的低成本预览要求，同时遵守明确不做视频转码。
- **备选**：引入 ffmpeg 生成持久化视频缩略图。
- **未选原因**：增加外部依赖和存储生命周期，超出 SRS 范围。

### TD-009a：业务语义待确认项

- **决策**：空相册是否允许发布、标题/描述默认字段优先级、来源信息展示开关的具体配置载体在实现前明确。
- **理由**：SRS §6.3、§8.6、§19 留有待确认项，TDD 不擅自填补业务语义。
- **备选**：在代码中选择默认行为。
- **未选原因**：会把未冻结的业务决策伪装成技术实现。
- **状态**：需要业务确认；若改变规范性行为，必须先修订 SRS。

### TD-009b：ZIP 资源配置待确认项

- **决策**：ZIP 最大文件数量、最大总大小、内存、超时和并发阈值作为项目配置，在 CC-05 开始前确定。
- **理由**：这些是技术资源边界，不应在实现中散落硬编码；TV-05 已验证限制机制可行，但未验证生产规模资源行为。
- **备选**：在 Controller 中写死数值或不设上限。
- **未选原因**：写死难以运维，不设上限会造成资源风险。
- **状态**：属于项目配置，不自动触发 SRS 修订；若配置导致正常业务无法完成并改变 SRS 语义，必须回到 SRS 评估。

---

## 14. 设计约束

以下六条直接来自 **TV Report“必须在 TDD 中明确的条件”**，并对应本 TDD 的落实位置：

| TV 约束 | TDD 落实 |
|---|---|
| 授权检查必须发生在任何 `sudo()` 附件读取之前 | §6.4、§7.2、TD-006；普通环境完成完整授权链后才读取附件 |
| Portal 路由必须显式要求登录并校验 Portal 角色 | §6.1、§12.1；所有 Portal 路由 `auth="user"` + `base.group_portal` |
| 媒体 URL 必须校验 Album、Item、Commercial Partner、发布、撤销、有效期和可用性 | §6.3、§7.2、§12；所有媒体/下载复用统一授权策略 |
| 相册客户应规范化为 Commercial Partner，或所有入口统一比较 | §6.2、TD-002；写入规范化，读取再次归一化 |
| 动态字段必须验证模型、字段类型、relation、可读权限和配置有效性 | §3.2、§3.3、§3.5；配置保存和每次读取都校验 |
| ZIP 文件名、数量、总大小和大文件资源策略必须明确 | §8.2—§8.5；安全文件名、有限配置、内存/超时/并发门禁 |

其他冻结约束：

- 不使用默认 `/web/content` 暴露相册媒体；
- 不复制附件；
- 不依赖 `wd_qooling.*`；
- 不让 Token 替代 Portal 授权；
- 不允许跨相册移动 Page；
- 不允许同一附件在同一 Album 重复。

---

## 15. 已知未验证项与集成测试计划

### 15.1 TV Report 未验证项

以下内容在 TV Report 中明确未完成，不得在 TDD 中写成已验证：

- 真实相册 ORM 模型、ACL 和 Record Rule；
- 真实自定义 Controller HTTP 请求；
- 未登录、跨客户、已撤销和过期场景的真实响应；
- 真实来源业务记录的权限和附件读取；
- 浏览器图片灯箱、视频播放和 HTTP Range；
- 真实动态 Many2many 记录读取；
- 大文件 ZIP 的内存、超时和并发行为；
- 不同运行配置下的实际 HTTP 状态码。

### 15.2 TV-03 补充结果

已通过 Odoo Shell 只读 ORM 验证：

- 项目数据库可以通过 Odoo ORM 连接；
- `ir.model.fields` 可以发现实际数据库中的 Many2many 附件字段候选；
- 候选字段的 `ttype` 和 `relation` 可以按设计条件校验。

TV 使用的具体业务模型和字段仅用于技术探针，不构成本模块的开发或运行依赖。尚未验证：

- 任意真实来源模型在目标运行环境中是否加载到 Registry；
- 对任意真实来源记录执行 `record[field_name]`；
- 来源模型 ACL、字段 ACL、多记录和空值行为。

该未验证项只影响来源采集集成，不影响模块独立开发。可以通过测试模型、测试数据或安装真实上游业务模块完成补充验证。

### 15.3 实施阶段需要验证的能力

后续验证应覆盖：

- Odoo ORM：模型关系、约束、状态动作、附件生命周期和 Record Rule；
- Odoo 集成：Portal 用户、Commercial Partner、发布/撤销/过期访问；
- Controller：媒体授权顺序、404、MIME、下载头和 Range；
- Portal E2E：列表、相页切换、筛选、灯箱、视频和多选下载；
- ZIP 运行时：数量/大小拒绝、文件名清洗、不可用 Item 和资源边界；
- 动态来源：真实 Registry 模型、配置校验、来源记录权限和多字段。

### 15.4 建议的验证类型

- Odoo 单元/集成测试：模型、动作、约束、权限和 Controller；
- Odoo HTTP 测试：认证、授权、响应状态和媒体头；
- Playwright 或等效浏览器 E2E：Portal 页面、媒体交互和下载；
- 人工验证：审核/拒绝、撤销、过期、异常提示和移动端体验。

本节只定义需要验证的对象和验证类型，不定义测试用例、实施步骤或测试代码。

---

## 16. 与 CC 的对应关系

| Coding Contract | 技术范围 | 对应 TDD 章节 | 前置依赖 |
|---|---|---|---|
| CC-01 核心数据模型与后台 | 四个 ORM 模型、字段、约束、ACL、后台视图和排序 | §2、§10、§11 | 无 |
| CC-02 媒体采集 | 来源配置解析、记录选择、上传、媒体校验、Item 唯一性 | §3、§4 | CC-01；TDD-Q-008 必须在 CC-02 开始前解决 |
| CC-03 审核与发布 | 状态动作、审核权限、Token、有效期、撤销 | §5、§6、§11 | CC-01、CC-02 |
| CC-04 Portal 查看器 | Portal 列表、查看器、OWL、媒体 Controller、单文件下载 | §6、§7、§9、§12 | CC-03 |
| CC-05 批量下载 | 多选状态、ZIP Controller、限制、文件名和资源边界 | §8、§9、§12 | CC-03、CC-04 |

CC 之间按业务依赖顺序推进，但本表不是 Implementation Plan，不规定排期、任务拆分或估工。

---

## 17. 明确不在 TDD 范围内的内容

以下内容不由本文档定义：

- Implementation Plan、任务拆分、排期和估工；
- 完整 Python、JavaScript、XML 或安全 CSV 代码；
- 具体测试用例、断言、测试数据和执行脚本；
- 部署方案、服务器拓扑、备份和发布流程；
- 引入额外库、具体库版本或外部工具；
- 图片编辑、视频剪辑、视频转码和 AI 分析；
- 客户上传、评论、点赞和匿名分享；
- 长期 ZIP 存储；
- 访问日志；
- 性能调优方案；
- 大文件 ZIP 的最终具体数值。

其中，ZIP 最大文件数、最大总大小、超时、并发和内存阈值必须在实现前作为项目配置决策明确；如果该决策改变 SRS 的业务行为，应先修订 SRS。

---

## 附录 A：待确认项

| 编号 | 待确认内容 | 影响 |
|---|---|---|
| TDD-Q-001 | 空相册是否允许发布 | 影响发布前检查和 Portal 空状态 |
| TDD-Q-002 | 各来源模型标题/描述默认字段优先级 | 影响从记录创建 Page |
| TDD-Q-003 | 来源信息展示配置的具体归属 | 影响 Item/Portal 数据返回 |
| TDD-Q-004 | ZIP 资源配置：最大文件数量、最大总大小、内存、超时和并发阈值；须在 CC-05 开始前确定 | 影响 Controller 限制和资源策略；属于项目配置，除非改变 SRS 业务语义，否则不触发 SRS 修订 |
| TDD-Q-007 | 图片缩略图的 Odoo 原生实现方式 | 影响 Portal 网格资源成本 |
| TDD-Q-008 | 使用测试模型或真实上游模块完成来源字段的 Registry 加载和 `record[field_name]` 读取验证；须在 CC-01 结束前解决、CC-02 开始前确认 | 影响来源采集集成，不影响核心相册和直接上传开发 |

### 12.2 CC-04 决策补充（2026-09-28）

- **TDD-Q-003：本版本不展示来源信息。** CC-04 Portal 返回结构不包含来源字段，也不返回部分来源信息；后续配置确定后以可选的 `source_info` 结构扩展，未配置时保持字段缺失或 `null`，不得影响核心查看器渲染。
- **TDD-Q-007：采用 Odoo 运行环境已提供的 Pillow 生成图片缩略图。** 缩略图仅用于 Portal 网格展示，不保存新的附件、不修改原始二进制、不进行视频转码；视频继续使用原媒体并由前端显示播放控件。缩略图路由必须复用 CC-04 授权链，并在授权完成后才读取附件。
