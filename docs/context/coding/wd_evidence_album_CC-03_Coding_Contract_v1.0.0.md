# WMS Evidence Album — Coding Contract CC-03
# 审核与发布

## 0. 文档信息

| 项目 | 内容 |
|---|---|
| 模块 | `wd_evidence_album` |
| CC | CC-03 — 审核与发布 |
| CC 版本 | v1.0.3 |
| 状态 | Frozen Coding Contract |
| Odoo | 18.0 Community Edition |
| 代码目录 | `/Users/lijianqiang/Documents/odoo18_album/mymodules/wd_evidence_album` |
| 上游业务基线 | SRS v1.0.0（Frozen） |
| 上游技术基线 | TDD v1.0.0（Frozen Implementation Baseline） |
| 实施规划基线 | Implementation Plan v1.0.0（Frozen Implementation Plan） |
| 前置编码基线 | CC-01、CC-02 已完成的模型、权限、媒体和 Item 契约 |
| 关联技术债 | TD-001 Open；TD-002 Open，是否纳入 CC-03 需单独确认 |

### 0.1 输入材料

- SRS §7.7—§7.10：审核、发布、撤销和有效期；
- SRS §9：后台角色权限矩阵；
- SRS §10：状态机；
- SRS §15：发布前业务和附件约束；
- TDD §5：状态动作、发布检查、Token 和有效期；
- TDD §6、§11：Portal 访问前置条件和后台权限边界；
- Implementation Plan §4：CC-03 目标、任务、验收条件和门禁；
- CC-01 已建立的 Album 状态字段、角色、Record Rule 和模型边界；
- CC-02 已建立的 Page/Item、媒体合法性校验、附件唯一性和可用性接口；
- Technical Debt Register v1.1.0：TD-001、TD-002 的当前状态和处理边界。

### 0.2 对应实施任务

| 任务 | 范围 | 依赖 |
|---|---|---|
| CC-03-T01 | 状态动作 | CC-01 Album 模型 |
| CC-03-T02 | 审核和发布权限 | CC-01 ACL/Record Rule、CC-03-T01 |
| CC-03-T03 | 发布前一致性检查 | CC-02 Page/Item 和媒体校验；TDD-Q-001 |
| CC-03-T04 | Token、有效期和撤销生命周期 | CC-03-T01、CC-03-T03 |
| CC-03-T05 | CC-03 关闭材料 | CC-03-T01 至 T04 |

## 1. 契约范围声明

### 1.1 本 CC 覆盖

本 CC 授权实现：

- Album 的提交审核、审核通过、审核拒绝、发布和撤销动作；
- 状态机的合法路径和非法状态拒绝；
- 业务用户、审核人和管理员的服务端动作权限；
- 发布前的统一一致性检查入口；
- 发布时 Token 生成、发布时间记录和 Token 重置；
- 撤销时间记录；
- 有效期判断所需的稳定业务方法；
- 管理员专用的已发布 Album 有效期延长动作；
- 审核、发布、撤销和有效期的后台表单交互；
- CC-03 的 IHR、ATR、HVR 输入和 FR 草稿。

### 1.2 本 CC 不覆盖

以下内容不属于 CC-03：

- Portal 相册列表、Portal 查看器、媒体预览页面和 OWL 组件（CC-04）；
- 媒体 Controller、图片/视频流、HTTP Range 和单文件下载（CC-04）；
- 多选、ZIP 生成、ZIP 限制和下载资源边界（CC-05）；
- Portal 用户授权 Controller 的完整实现（CC-04）；
- Source Config Resolver、来源记录读取和媒体采集（CC-02）；
- 自动同步来源记录的新附件；
- 修改 `wd_qooling_app` 或引入具体来源业务模块依赖；
- 以 Token 实现匿名访问或绕过 Portal 授权；
- TD-002 Gallery Widget，除非项目明确将其单独纳入本 CC。

### 1.3 前置门禁

TDD-Q-001 已由业务方确认：

> 空 Album 审核失败，不允许发布。

CC-03 V1 将“空 Album”定义为没有任何 Page/Item 可供客户交付的 Album。该规则同时适用于批准动作和发布前检查：

- 空 Album 不得从 `pending_review` 进入 `approved`；
- 空 Album 不得从 `approved` 进入 `published`；
- 审核或发布失败时不得写入对应的时间、审核人或 Token；
- 具体错误消息必须明确提示 Album 为空，需要先添加 Page 和媒体。

TDD-Q-001 的决策记录在本 CC 审批记录中，CC-03-T03 的发布前检查门禁已解除。

## 2. 状态机契约

### 2.1 合法状态路径

CC-03 V1 冻结以下状态路径：

```text
draft
  └─ submit_review → pending_review
       ├─ approve → approved
       └─ reject  → draft
approved
  └─ publish → published
published
  └─ revoke → revoked
```

不允许：

- `draft → approved`；
- `draft → published`；
- `pending_review → published`；
- `pending_review → revoked`；
- `published → draft`；
- `revoked → published`；
- 通过普通 `write({"state": ...})` 绕过状态动作。

### 2.2 状态动作

每个动作必须是明确的模型业务方法，并在服务端执行：

| 动作 | 当前状态 | 目标状态 | 必要副作用 | 非法状态错误 |
|---|---|---|---|---|
| Submit Review | `draft` | `pending_review` | 不生成 Token | `UserError`：仅草稿可提交审核 |
| Approve | `pending_review` | `approved` | 写入当前审核人 | `UserError`：仅待审核可批准 |
| Reject | `pending_review` | `draft` | 写入当前审核人；保留拒绝后的可编辑性 | `UserError`：仅待审核可拒绝 |
| Publish | `approved` | `published` | 发布前检查、生成 Token、写入 `published_at` | `UserError`：仅已审核可发布 |
| Revoke | `published` | `revoked` | 写入 `revoked_at`；后续访问条件立即失效 | `UserError`：仅已发布可撤销 |

动作必须：

- 对多记录调用显式拒绝或逐条处理，不得静默只处理第一条；
- 对非法当前状态返回明确 `UserError`；
- 不通过 UI 隐藏替代服务端状态检查；
- 在同一个 Odoo ORM 事务中完成状态和相关字段写入；
- 不手动 `commit()`。

批准动作必须在写入 `approved` 前检查 Album 是否为空；空 Album 审核失败并保持 `pending_review`。

状态动作对多记录调用必须采用冻结的单记录语义：调用方传入多条记录时显式抛出 `UserError`，不得静默只处理第一条，也不得在一次调用中部分成功。

### 2.3 状态字段写入边界

- `state` 只能由 CC-03 状态动作或明确的内部辅助方法写入；
- 外部调用方不能通过普通 `create`/`write` 任意指定状态；
- `published_at` 只由发布动作写入；
- `revoked_at` 只由撤销动作写入；
- 审核人字段只由批准或拒绝动作写入；
- 已发布 Album 不允许通过普通编辑动作修改为其他状态；
- 撤销后的 Album 不得重新发布，除非上游 SRS/TDD 明确修订状态机。

## 3. 审核和发布权限契约

### 3.1 角色边界

按 SRS §9，CC-03 V1 采用以下权限：

| 角色 | 提交审核 | 审核通过/拒绝 | 发布 | 撤销 | 重置 Token | 延长已发布有效期 |
|---|---:|---:|---:|---:|---:|---:|
| Album 业务用户 | 是 | 否 | 否 | 否 | 否 | 否 |
| Album 审核人 | 是 | 是 | 是 | 是 | 是 | 否 |
| Album 管理员 | 是 | 是 | 是 | 是 | 是 | 是 |
| Portal 客户 | 否 | 否 | 否 | 否 | 否 | 否 |

“按钮不可见”不是完整权限控制。每个模型动作必须在服务端重新执行角色和记录权限检查。

“重置 Token”权限是 CC-03 基于运营需要作出的实现级判断：审核人已经拥有发布权限，重置 Token 是撤销已泄露分享链接的发布操作延伸，因此授予审核人。如果 SRS 后续规定重置 Token 仅限管理员，必须回到 SRS 修订并同步本契约。

### 3.2 审核责任

- 批准和拒绝动作必须记录 `reviewed_by = env.user`；
- 审核人必须对目标 Album 具有写权限和相应审核组权限；
- 普通业务用户不能通过 RPC、URL、导入或直接 ORM 调用完成批准、拒绝、发布或撤销；
- Portal 用户不能访问后台审核动作；
- 审核动作不得读取或修改来源业务记录。

### 3.3 Album 归属

- 继续复用 CC-01 的 Album Record Rule；
- `customer_id` 的 Commercial Partner 规范化规则不得在 CC-03 中重写；
- `customer_id` 不是审核权限替代条件；
- Portal 授权不在 CC-03 中实现，但 CC-03 不能产生“Token 即授权”的语义。

### 3.4 有效期延长权限

- 仅 Album 管理员可以修改已发布 Album 的 `valid_until` 以延长有效期；
- 审核人不能仅因审核权限而延长已发布 Album 的有效期；
- 有效期延长不改变 `state="published"`；
- 有效期延长不要求重新审核；
- 有效期延长后，后续 Portal 授权判断立即恢复；
- 已撤销 Album 不得通过延长有效期恢复，必须遵守明确的重新发布流程。

“管理员可以延长已发布过期 Album 的有效期”是 CC-03 基于业务方确认作出的正式实现级业务规则，记录在 §13 v1.0.2 审批记录中。该规则应在后续 SRS/TDD 修订时补登；若上游语义发生变化，必须同步更新本 CC。

## 4. 发布前一致性检查

### 4.1 统一入口

CC-03 必须提供一个由 `publish` 业务动作调用的统一发布前检查入口。

该入口负责检查，不负责：

- 不负责修改来源记录；
- 不负责重新解析 Source Config；
- 不负责创建 Page/Item；
- 不负责实现 Portal Controller；
- 不负责生成 ZIP；
- 不负责通过 `sudo()` 绕过附件或业务权限。

### 4.2 必须检查的内容

发布动作开始时必须重新检查：

- Album 当前状态为 `approved`；
- Album 存在有效客户；
- 审核人已记录；
- Album 至少包含一个可交付 Page/Item；空 Album 必须拒绝；
- Page 的 `album_id` 与当前 Album 一致；
- Page 标题满足当前模型约束；
- Item 的 `page_id`、`album_id` 关系一致；
- Item 的 `attachment_id` 存在且仍可用；
- Item 的 `availability_state` 与附件实际存在性一致；
- Album 内附件没有重复；
- Item 的 `media_type` 仍属于允许值；
- 不存在违反 CC-01/CC-02 约束的孤立或半成品关系；
- 空 Album 必须拒绝发布；该规则已由业务方确认并记录在 §1.3。

### 4.3 检查失败语义

- 任一检查失败，发布动作整体失败；
- 不得写入 `state="published"`；
- 不得写入 `published_at`；
- 不得生成或替换 Token；
- 错误必须是可定位的业务错误；
- 失败不能返回成功形状的结果；
- 检查失败不删除 Page、Item 或附件；
- 事务失败不得留下部分状态更新。

### 4.4 既有校验入口

发布前检查必须复用 CC-01/CC-02 已建立的：

- Item 可用性刷新方法；
- 媒体合法性校验入口；
- Album 内附件唯一性约束；
- Page/Item Album 一致性校验。

CC-03 不得复制第二套 MIME、扩展名、文件头或动态来源校验逻辑。

## 5. Token 和有效期契约

### 5.1 Token 生成

发布成功时：

- 生成密码学随机、不可预测的 Token；
- Token 在 Album 层面唯一；
- Token 不得使用递增 ID、Album Number、时间戳或可猜测字符串；
- Token 写入必须与 `state`、`published_at` 在同一事务中完成；
- 草稿和待审核 Album 不要求 Token；
- 发布失败不得留下新 Token。

Token 生成后必须验证唯一性；如果发生唯一性冲突，必须重新生成并再次检查。数据库唯一约束作为最终兜底，不能把“碰撞概率极低”当作跳过唯一性检查的理由。

Token 只作为 URL 标识或资源定位输入，不能单独构成授权。

### 5.2 Token 重置

审核人或管理员可以显式重置已存在的 Token：

- 生成新的密码学随机 Token；
- 旧 Token 立即失效；
- Album 状态不因重置改变；
- 不修改 `published_at`；
- 重置动作必须记录在 IHR/ATR 中；
- 重置 Token 不提供匿名访问能力。

### 5.3 有效期判断

统一有效期方法遵守：

```text
valid_until 为空              => 未设置有效期
now < valid_until              => 未过期
now >= valid_until             => 已过期
```

- 过期不是新的 `state`；
- 过期不自动把 Album 改为 `revoked`；
- CC-03 负责提供稳定的有效期判断入口；
- CC-04 后续必须复用该入口，不得自行实现不同的边界判断；
- 服务器时间作为唯一判断基准，不使用浏览器时间。

已发布但已过期的 Album 必须通过专门的管理员动作（建议方法名 `action_extend_validity`）延长 `valid_until`，不允许通过普通 `write({"valid_until": ...})` 修改已发布 Album 的有效期。该动作必须：

- 检查当前用户属于 Album 管理员；
- 检查 Album 当前状态为 `published` 且未撤销；
- 检查新的 `valid_until` 晚于当前服务器时间；
- 不修改 `state`、`token`、`published_at` 或 `reviewed_by`；
- 在 IHR/ATR 中登记操作入口和权限证据。

延长后 Album 仍保持 `published`，不重新生成 Token，不重新审核；Portal 后续请求按新的有效期立即判断为可访问。`revoked` Album 不适用该恢复规则。

### 5.4 撤销

撤销已发布 Album 时：

- `state` 变为 `revoked`；
- 写入 `revoked_at`；
- 后续 Portal 访问必须被拒绝；
- 不删除 Page、Item 或附件；
- 不把 Token 当作仍然有效的授权凭证。

## 6. 后台界面契约

CC-03 可以修改 `wd_evidence_album` 的 Album 表单和列表，但必须保持：

- 状态栏与按钮状态和服务端动作一致；
- 业务用户只能看到其有权限执行的动作；
- 审核人和管理员能看到审核、发布、撤销和 Token 操作；
- Token 不在普通业务用户界面暴露；
- 发布前检查失败显示明确错误；
- 已发布和已撤销 Album 的不可编辑边界符合 SRS/TDD；
- 不提前加入 Portal 查看器、媒体 Controller 或 ZIP 控件。

## 7. 既有行为保留

以下行为属于 CC-03 的回归边界：

- Album Number 自动编号和左上角标题不改变；
- Album `name`、客户、描述和有效期字段语义不改变；
- CC-01 的 Commercial Partner 规范化不改变；
- Page 不能跨 Album 移动；
- 删除 Page/Item 不删除底层 `ir.attachment`；
- Item `availability_state` 刷新规则不改变；
- CC-02 来源型 Item 和上传型 Item 的创建、追溯和媒体校验不改变；
- 同一 Album 内附件不能重复；
- Source Config 的字段校验和显式启用原则不改变；
- CC-02 已通过的 HVR 场景不能被发布流程改写为未通过；
- Portal 尚未实现时，不得把后台 Token 显示误描述为可访问链接。

## 8. 允许修改和禁止修改

### 8.1 允许修改

- `mymodules/wd_evidence_album/models/album.py`
  - 状态动作；
  - 发布前一致性检查；
  - Token 生成、重置、有效期判断和 `action_extend_validity`；
  - 审核人、发布时间和撤销时间的动作写入。
- `mymodules/wd_evidence_album/views/album_views.xml`
  - 审核、发布、撤销和 Token 操作按钮；
  - 状态和字段可见性；
  - 发布相关错误的标准 Odoo 交互。
- `mymodules/wd_evidence_album/security/`
  - 仅限 CC-03 审核/发布权限所需的最小 ACL 或组规则调整。
- CC-03 对应的 IHR、ATR、HVR 和 FR 文档。

### 8.2 禁止修改

- 禁止修改 SRS/TDD 的状态语义；
- 禁止新增 Portal 路由或媒体 Controller；
- 禁止实现 OWL Portal 查看器；
- 禁止实现 ZIP 下载；
- 禁止让 Token 绕过登录、Portal 组或 Commercial Partner 授权；
- 禁止以 `sudo()` 替代后台角色检查；
- 禁止在 CC-03 中重新实现 Source Resolver 或媒体校验；
- 禁止修改 `mymodules/wd_evidence_album/models/item.py` 和 `page.py` 的核心逻辑，包括附件引用、附件唯一性、可用性刷新和 Page 归属；如确需调整，必须回到 CC-01/CC-02 契约并形成变更记录；
- 禁止修改 `wd_qooling_app`；
- 禁止将 TD-001 或 TD-002 静默标记为已关闭；
- 禁止绕过已确认的 TDD-Q-001 空 Album 审核门禁。

## 9. 测试和验证契约

### 9.1 自动化验证

至少覆盖：

- 合法状态路径；
- 所有非法状态跳转；
- 普通用户调用审核/发布/撤销方法被拒绝；
- 审核人和管理员权限正确；
- 多记录调用状态动作时显式拒绝，且不发生部分成功；
- 拒绝回到草稿并记录审核人；
- 发布前检查失败时不改变状态、时间和 Token；
- 发布成功生成唯一不可预测 Token；
- Token 重置使旧 Token 失效；
- Token 生成冲突时重新生成并由数据库唯一约束兜底；
- 有效期边界 `now < valid_until` 和 `now >= valid_until`；
- 仅管理员可以通过专门动作延长已发布过期 Album 的有效期；
- 延长有效期不改变状态、Token、发布时间或审核人；已撤销 Album 延长失败；
- 撤销写入时间并改变状态；
- 发布过程中的事务回滚；
- 既有 CC-01/CC-02 回归测试继续通过。

### 9.2 浏览器人工验证

HVR 至少覆盖：

1. 业务用户提交审核；
2. 审核人批准和拒绝；
3. 拒绝后 Album 回到草稿；
4. 未审核 Album 不能发布；
5. 审核后发布成功并生成 Token；
6. Token 重置后旧值失效；
7. 已发布 Album 撤销；
8. 已过期 Album 的有效期判断；
9. 发布前媒体/Item 不一致时明确拒绝；
10. 普通用户、审核人和管理员看到的按钮及实际权限一致。

浏览器观察不能替代用户人工确认。HVR 中每个场景必须标注证据来源：

- `user-confirmed`：用户亲自执行并确认；
- `agent-observed`：Agent 执行、用户观察结果；
- `automated`：自动化测试证据。

只有 `user-confirmed` 构成正式 HVR PASS。

### 9.3 关闭材料

CC-03 关闭前必须形成：

- CC-03 IHR：记录状态动作、权限、发布检查和 Token 实现入口；
- CC-03 ATR：记录自动化测试、结果、证据位置和失败项；
- CC-03 HVR：记录人工操作步骤、运行日期、验证者和每个场景结果；
- CC-03 FR：明确已通过、阻塞、未运行、技术债和后续 CC 边界。

## 10. 验收条件

### AC-01 状态路径

状态只能按 SRS/TDD 允许的路径流转，非法状态动作被服务端拒绝。

### AC-02 审核权限

普通业务用户不能批准、拒绝、发布或撤销；审核人和管理员权限符合 SRS §9。

### AC-03 拒绝回退

审核拒绝后 Album 回到 `draft`，记录审核人，并允许业务用户继续修订。

### AC-04 发布前检查

发布动作复用统一检查入口；任何 Page、Item、附件、客户或空 Album 规则不满足时均不得发布。

### AC-05 发布和 Token

审核通过且发布前检查通过后，Album 进入 `published`，记录 `published_at`，并生成密码学随机 Token。

### AC-06 Token 授权边界

Token 不能单独授权访问，不实现匿名访问，不绕过后续 CC-04 的登录、Portal 组和 Commercial Partner 检查。

### AC-07a 撤销

撤销立即写入 `revoked_at`，并使后续访问条件失效；不删除 Page、Item 或附件。

### AC-07b 过期判断

过期不改变 Album 状态；统一有效期判断在 `now >= valid_until` 时返回已过期。

### AC-07c 过期恢复

管理员通过专门动作延长已发布 Album 的 `valid_until` 后，Album 保持 `published`，后续访问立即恢复，且不重新审核、不重新生成 Token。

### AC-07d 撤销不可恢复

已撤销 Album 不能通过延长有效期恢复。

### AC-08 回归

CC-01 和 CC-02 已验证的模型关系、媒体校验、Item 生命周期、附件唯一性和来源追溯不受影响。

### AC-09 关闭材料

CC-03 的 IHR、ATR、HVR 和 FR 均已形成，并明确 TDD-Q-001、TD-001、TD-002 的状态。

## 11. 未解决项和升级规则

| 项目 | 当前状态 | 对 CC-03 的影响 |
|---|---|---|
| TDD-Q-001 空 Album 发布规则 | 已解决：空 Album 审核失败，不允许发布 | 不再阻塞 CC-03；批准动作和发布前检查必须落实该规则 |
| 已发布 Album 过期恢复 | 已解决：管理员可延长有效期；已撤销 Album 不适用 | 需落实管理员权限和新的有效期即时生效 |
| TD-001 Source Config 字段选择器 | Open | 不阻塞 CC-03；不得在 CC-03 中伪装关闭 |
| TD-002 Item 附件 Gallery Widget | Open | 是否纳入 CC-03 前需确认；默认不阻塞审核发布核心流程 |
| CC-02 ATR | Partial：已覆盖 CC-02 核心测试类型，但 TDD-Q-008 相关的来源采集部分仍待验证 | CC-03 核心审核/发布流程不依赖 TDD-Q-008；进入 CC-03 HVR 前，CC-02 关闭材料必须区分已验证和被阻塞范围，且发布前检查必须复用 CC-02 的媒体合法性校验入口 |

如果实现中发现：

- SRS 与 TDD 的状态路径冲突；
- 审核角色无法由现有 ACL/Record Rule 表达；
- 已确认的空 Album 审核门禁无法由现有模型或权限可靠实现；
- 发布前检查需要新增未定义业务语义；

必须停止相关实现并升级，不得由实现者静默决定。

## 12. 追溯矩阵

| CC-03 契约 | SRS | TDD | Implementation Plan |
|---|---|---|---|
| 状态动作 | §7.7、§10 | §5.1、§5.2 | §4.3 CC-03-T01 |
| 审核和发布权限 | §9 | §11 | §4.3 CC-03-T02 |
| 发布前一致性检查 | §7.7、§15 | §5.3 | §4.3 CC-03-T03 |
| Token 生命周期 | §7.8 | §5.4 | §4.3 CC-03-T04 |
| 撤销 | §7.9 | §5.4 | §4.3 CC-03-T04 |
| 有效期判断 | §7.10、§8.2 | §5.5、§6.3 | §4.3 CC-03-T04 |
| 空 Album 审核/发布门禁 | §7.7、§7.8 | §5.3 | §4.3 CC-03-T01、T03 |
| 过期 Album 恢复 | §7.10、§8.2 | §5.5、§6.3 | §4.3 CC-03-T04 |
| 审批记录和业务决策 | §7.7、§7.8、§7.10 | §5.3、§5.5 | CC-03 §13 |
| 关闭材料 | — | 测试和证据要求 | §4.3 CC-03-T05、§8 |

## 13. 审批记录

| 版本 | 日期 | 变更 | 审批人 | 审批日期 |
|---|---|---|---|---|
| v1.0.0 | 2026-09-24 | 起草 CC-03 审核与发布契约 | 本会话用户 | 2026-09-24 |
| v1.0.1 | 2026-09-24 | 记录业务决策：空 Album 审核失败，不允许发布；解除 TDD-Q-001 门禁 | 本会话用户 | 2026-09-24 |
| v1.0.2 | 2026-09-24 | 记录业务决策：管理员可延长已发布过期 Album 的有效期；已撤销 Album 不适用 | 本会话用户 | 2026-09-24 |
| v1.0.3 | 2026-09-24 | 根据审批意见补充 Token/有效期权限依据、专门延长动作、多记录验证、ATR Partial 边界和冻结条件；批准进入编码 | 本会话用户 | 2026-09-24 |
| v1.0.4 | 2026-09-24 | 批准冻结 CC-03，允许进入编码实施 | 本会话用户 | 2026-09-24 |
| v1.0.5 | 2026-09-28 | CC-03 编码、ATR 和 HVR 完成；六个 HVR 场景全部用户确认通过，正式冻结交付基线 | 本会话用户 | 2026-09-28 |
