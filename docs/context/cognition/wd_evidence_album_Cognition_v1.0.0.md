# WMS 客户证据相册 — 项目认知基线

## 0. 文档信息

| 项目 | 内容 |
|---|---|
| 模块 | `wd_evidence_album` |
| 中文名 | WMS 客户证据相册 |
| Cognition 版本 | v1.0.0 |
| 状态 | Project Cognition Baseline |
| Odoo | 18.0 Community Edition |
| Python 环境 | `/Users/lijianqiang/Documents/odoo18_album/venv` |
| 业务基线 | `wd_evidence_album_SRS_v1.0.0.md` |
| 技术验证基线 | `wd_evidence_album_TV_v1.0.0.md` |
| 上游 | Media Widget：产生业务记录附件 |
| 下游 | Odoo Customer Portal：登录客户查看证据 |

本文档记录团队和 Agent 对本项目的共同理解。它是认知导航和决策约束，不替代 SRS、DDD 或 TDD。发生冲突时，SRS 是业务语义的唯一权威；技术实现以批准的 TDD 为准。

---

## 1. 项目一句话定义

`wd_evidence_album` 不是媒体生产工具，也不是附件存储系统。

它是一个**独立的客户证据集合整理、审核、发布和交付模块**：用户从已有业务附件中选择媒体，或直接上传媒体，组织为相册和相页，经过审核后，通过受保护的 Portal 提供给客户查看和下载。

---

## 2. 业务边界

### 2.1 本模块负责

- 创建和维护相册；
- 在相册内组织相页；
- 从已配置的业务来源字段选择媒体；
- 直接上传图片和视频；
- 对相页及相册项排序、说明和整理；
- 审核、发布、撤销和有效期控制；
- Portal 相册列表、查看、预览和下载；
- 临时生成受限制的 ZIP 下载。

### 2.2 本模块不负责

- 产生、编辑、转码或分析图片和视频；
- 修改业务单据上的附件；
- 替代 `ir.attachment`；
- 客户上传、评论、点赞或匿名分享；
- 通过实时业务记录视图自动同步媒体；
- 长期保存 ZIP；
- 直接依赖或继承 `wd_qooling.*` 模型；
- 访问日志（V1）。

---

## 3. 核心领域语言

| 术语 | 项目中的准确含义 |
|---|---|
| 相册 Album | 一次客户证据交付的独立集合及其审核/发布边界 |
| 相页 Page | 相册内的展示和组织分组，不保存来源语义 |
| 相册项 Item | 相页中的单个图片或视频，引用一个 `ir.attachment` |
| 来源记录 | 相册项创建时所选择的业务记录 |
| 来源字段 | 管理员明确配置为证据来源的附件字段 |
| 直接上传 | 不来自业务记录的相册媒体 |
| 商业实体 | `res.partner.commercial_partner_id` 归一后的客户主体 |
| 媒体可用性 | 原始附件是否仍然存在并可供相册读取 |
| Portal 用户 | 已登录且属于客户商业实体的 Odoo 用户 |
| 分享 Token | 发布后的 URL 标识，不是独立授权凭证 |

---

## 4. 最重要的业务心智模型

### 4.1 相册是快照集合，不是实时业务视图

用户明确选择或上传媒体后，相册项形成独立引用关系：

- 来源记录后来新增附件，不自动进入相册；
- 来源记录发生变化，不改变既有相册项；
- 删除相册项，不删除来源附件；
- 相页创建完成后，不再持续绑定来源记录。

### 4.2 相册项引用附件，不复制附件

相册项只引用 `ir.attachment`：

- 不创建附件副本；
- 删除相册项不得删除原始附件；
- 原始附件被删除后，相册项保留并显示“媒体不可用”；
- 不可用媒体不能被 Portal 预览或下载。

### 4.3 来源信息用于追溯，不用于 Portal 授权

来源模型、来源记录 ID 和来源字段用于审计与追溯。

Portal 是否能访问相册，只根据相册本身的发布状态、客户商业实体、撤销状态和有效期判断，不重新检查来源业务记录权限。

---

## 5. 不变量与不可违反的规则

1. 同一附件在同一相册中只能出现一次。
2. 相页只能属于一个相册，不允许跨相册移动。
3. 相册不能跳过审核直接发布。
4. 发布后的相册必须生成密码学随机 Token。
5. Token 不提供匿名访问或独立授权。
6. Portal 用户必须登录。
7. Portal 客户匹配必须基于 Commercial Partner，而不是联系人直接 ID。
8. 媒体 Controller 必须先完成相册授权，再使用 `sudo()` 读取附件。
9. 仅知道 `attachment_id` 不构成访问权限。
10. 只有已配置的 `Many2many` → `ir.attachment` 字段才是合法来源字段。
11. 只能接受 JPG/JPEG/PNG 图片和 MP4 视频。
12. ZIP 必须临时生成，不得长期保存。
13. ZIP 必须限制文件数量和总文件大小。
14. 原始附件的生命周期不由相册项控制。

---

## 6. 状态和访问理解

### 6.1 相册状态

```text
草稿 → 待审核 → 已审核 → 已发布 → 已撤销
             ↘ 草稿
```

- 待审核可以被拒绝回到草稿；
- 只有已审核可以发布；
- 已发布可以撤销；
- 过期不是状态，而是访问时的判断条件。

### 6.2 Portal 访问必须同时满足

```text
已登录
AND 是 Portal 用户
AND album.customer_id.commercial_partner_id
    == user.partner_id.commercial_partner_id
AND 状态为已发布
AND 未撤销
AND 未过期
```

推荐未授权返回 404，降低相册或附件存在性泄露风险。

---

## 7. Odoo 18 技术认知

### 7.1 附件访问

- Odoo 默认 `/web/content` 不是本模块的授权边界；
- 自定义媒体路由应使用 `auth="user"`；
- 路由中显式检查 Portal 角色和 Album 权限；
- 只有授权完成后，才允许 `sudo()` 读取 `ir.attachment`；
- 图片和视频可通过自定义 URL 配合 `<img>` 与 `<video>` 使用；
-真实浏览器 Range 播放行为仍需集成/E2E 验证。

### 7.2 Commercial Partner

标准判断应归一化双方：

```python
album.customer_id.commercial_partner_id \
    == request.env.user.partner_id.commercial_partner_id
```

不能只比较：

```python
album.customer_id == request.env.user.partner_id
```

否则同一客户公司的不同 Portal 联系人可能被错误拒绝。

### 7.3 动态证据来源字段

管理员配置通过 `ir.model` 和 `ir.model.fields` 解析：

```python
[
    ("model_id.model", "=", model_name),
    ("ttype", "=", "many2many"),
    ("relation", "=", "ir.attachment"),
]
```

字段名解析后才允许使用：

```python
attachments = record[field_name]
```

必须同时验证模型、字段、字段类型、relation、来源记录权限和字段可读性。

技术验证数据库中已发现 `wd.qooling.inbound.form.photo_ids` 元数据，但该业务模型当前未加载到 Registry。因此元数据发现已验证，真实记录动态读取仍未验证。

### 7.4 OWL 和 Portal

- Portal 前端可以通过 `web.assets_frontend` 承载 OWL；
- OWL 适合处理媒体网格、当前相页、筛选和多选状态；
- 简单媒体展示不需要额外 RPC，`src` 可直接指向自定义媒体路由；
- 真实 QWeb 挂载点、浏览器图片预览和视频播放必须通过集成/E2E 验证。

### 7.5 临时 ZIP

优先使用 Python 标准库：

```python
io.BytesIO
zipfile.ZipFile
```

生成前必须完成：

1. Portal 和相册授权；
2. 相册项归属校验；
3. 媒体可用性校验；
4. 数量限制；
5. 总大小限制；
6. 文件名清洗和去重。

V1 不强制依赖 OCA ZIP 模块。大文件内存、超时和并发策略必须在 TDD 中明确。

---

## 8. 当前技术验证状态

### 已验证

- 项目 venv 可加载 Odoo 18；
- Odoo 默认附件访问检查路径；
- 自定义 Controller 中“先授权、后 `sudo()`”策略；
- Commercial Partner 的 Odoo 18 归一化逻辑；
- `ir.model.fields` 的动态附件字段发现；
- Portal 前端承载 OWL；
- 内存 ZIP 和 HTTP 下载响应原语；
- 项目数据库可通过 Odoo Shell 进行只读 ORM 验证。

### 尚未验证

- 真实相册 ORM 模型、ACL 和 Record Rule；
- 真实自定义媒体 Controller 请求；
- 未登录、跨客户、已撤销和过期场景的 HTTP 响应；
- 真实业务模型记录的动态字段读取；
- 浏览器图片灯箱、视频播放和 Range 请求；
- 大文件 ZIP 的资源占用和并发行为；
- 完整 Portal E2E 流程。

### 数据库验证纪律

数据库相关验证必须使用 Odoo 应用层，例如：

```bash
./venv/bin/python odoo-bin shell -c odoo.conf -d odoo18ce --no-http
```

禁止使用 `psql`、裸 SQL、数据库客户端或数据库驱动直接读写。

---

## 9. 文档与开发顺序

项目权威链：

```text
SRS → DDD（按需）→ TDD → Coding Contract
   → Implementation / IHR / ATR / HVR → FR
   → PVR / PCR
```

当前基线：

1. SRS v1.0.0 已冻结；
2. TV v1.0.0 已完成风险驱动技术验证；
3. 尚未开始完整业务模块实现；
4. 下一步应编写 TDD；
5. TDD 冻结后才能进入 Coding Contract 和实现。

简单实现问题优先直接使用 Odoo 原生能力，不为了抽象而建立额外框架。

---

## 10. 设计决策倾向

本项目默认遵循：

```text
Odoo Native
→ Simple Models
→ Simple Views
→ Explicit Business Logic
→ Robust Before Clever
→ Testable
→ Maintainable
```

因此：

- 使用标准 Odoo ORM、权限、视图和 Controller；
- 不引入不必要的 Repository、DAO、DTO 或独立存储层；
- 不复制附件；
- 不把核心授权逻辑放在前端；
- 不用 Token 替代 Portal 授权；
- 不把动态配置做成默认暴露所有附件字段；
- 不用静态分析或内存模拟冒充关键运行时集成验证。

---

## 11. Cognition 使用规则

1. 新成员或 Agent 开始工作前，应先阅读本文件、SRS 和最新 TDD。
2. 发现业务语义冲突时，回到 SRS，不在代码中自行解释。
3. 发现领域边界冲突时，回到 DDD（如果项目建立了 DDD）。
4. 发现技术实现缺口时，更新 TDD，不直接扩大 Coding Contract。
5. 没有实际证据时，必须写“未验证”，不得写“通过”。
6. 不得因为实现方便而改变相册快照、附件引用、Commercial Partner 或审核发布语义。
7. 不得修改 Odoo 官方核心代码或官方模块。
8. 删除文件、清理已有资料或改变冻结文档前，必须取得明确授权。

---

## 12. Cognition 与正式文档的边界

| 内容 | 唯一权威 |
|---|---|
| 业务范围、状态、验收标准 | SRS |
| 聚合、领域不变量和领域边界 | DDD（如建立） |
| ORM、Controller、前端、ZIP 技术实现 | TDD |
| 单轮实现范围 | Coding Contract |
| 实施和测试证据 | IHR / ATR / HVR |
| 单轮关闭结论 | FR |
| 项目级验证和收口 | PVR / PCR |
| 项目共同理解和导航 | 本 Cognition |

本文件可以补充认知、提示风险和链接权威文档，但不得悄悄改变上游冻结语义。
