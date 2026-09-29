# WMS Evidence Album — Coding Contract CC-06
# 发布前 Portal 效果预览

## 0. 文档信息

| 项目 | 内容 |
|---|---|
| 模块 | `wd_evidence_album` |
| CC | CC-06 |
| 文档版本 | v1.0.0 |
| 文档状态 | Frozen Coding Contract；待上游补充 SRS、Implementation Plan 和技术债登记后方可进入编码 |
| 起草日期 | 2026-09-29 |
| 前置基线 | SRS v1.0.0 Frozen；TDD v1.0.0 Frozen Implementation Baseline；CC-01 至 CC-05 已冻结/完成各自范围 |
| 对应 Implementation Plan 任务 | **待补充项**：当前 Implementation Plan 仅定义 CC-01 至 CC-05，未定义 CC-06 |
| 关联技术债 | **待登记项**：Technical Debt Register 当前没有发布前 Portal 预览条目；建议登记为“发布前 Portal 效果预览缺口”，编号由技术债登记流程分配 |
| 现有相关债务 | TD-002 已关闭；其关闭范围是后台 Page Gallery 的媒体预览和删除关系，不等同于 Portal 效果预览 |

输入材料：

- [SRS v1.0.0](../../designing/wd_evidence_album_SRS_v1.0.0.md)
- [TDD v1.0.0](../../designing/wd_evidence_album_TDD_v1.0.0.md)
- [Implementation Plan v1.0.0](wd_evidence_album_Implementation_Plan_v1.0.0.md)
- CC-01、CC-02、CC-03、CC-04、CC-05 Coding Contract、IHR、ATR、HVR 和 FR 材料
- [Technical Debt Register v1.1.0](wd_evidence_album_Technical_Debt_Register_v1.0.0.md)
- [TV v1.0.0](../../designing/wd_evidence_album_TV_v1.0.0.md)
- [项目认知文档](../../cognition/wd_evidence_album_Cognition_v1.0.0.md)

## 1. 契约范围声明

### 1.1 覆盖范围

CC-06 将“审核人在发布前查看客户 Portal 实际展示效果”翻译为可编码、可验收的契约，覆盖：

- Album Form、审核页面和可选审核列表的预览入口；
- 后台用户认证和 Album 记录授权；
- 预览路由及返回 Album Form 的行为；
- 复用 CC-04 Portal Viewer 展示逻辑；
- 预览与 Published Portal 在授权、Token、有效期、批量下载等方面的差异；
- 预览的不可分享、不可发布、不可越权和不可变更限制；
- CC-06 IHR、ATR、HVR、FR 关闭材料。

### 1.2 不覆盖范围

CC-06 不修改或重新定义：

- CC-03 的审核、批准、发布、撤销状态机；
- CC-04 的 Published Portal Access Policy；
- CC-04 已冻结的媒体 Controller、单文件媒体授权和响应语义；
- CC-05 的 ZIP 下载、资源限制和 Item ID 请求边界；
- 匿名访问、Token 生成、客户上传、评论、点赞；
- 视频转码、图片编辑；
- CC-07 或后续 CC 的功能。

如复用 Portal Viewer 需要拆分公共展示组件，该拆分仅限于保持 CC-04 行为不变所需的重构，不得借机扩大 CC-06 范围。

### 1.3 前置条件

- CC-03 状态机、后台权限和发布前一致性检查已可用；
- CC-04 Portal Viewer、媒体预览和媒体 Controller 已可用；
- CC-04 的 Published Portal 授权链仍由其既有入口统一执行；
- Album、Page、Item 和媒体数据使用当前数据库记录，不创建模拟 Album 或复制媒体数据。

**上游文档门禁：** CC-06 进入编码前必须同时满足以下条件：

- SRS 已补充 `BR-XX Portal Preview`，至少覆盖 AC-01 至 AC-10 的业务验收条款；具体编号由 SRS 维护流程分配；
- Implementation Plan 已补充 CC-06 的任务、依赖和关闭材料；
- Technical Debt Register 已登记“发布前 Portal 效果预览缺口”，并明确编号、严重度和责任范围；
- §13 追溯矩阵中的“待补充”条目已替换为上游文档的具体章节引用。

以上条件未完成前，本文件只能作为 Frozen Draft，不得进入编码。

### 1.4 后续依赖

- SRS 必须补充正式 BR 编号和验收条款；
- Implementation Plan 必须补充 CC-06 任务、依赖和关闭材料；
- Technical Debt Register 必须通过版本化变更登记预览缺口；
- 任何跨 CC-04 Viewer 或媒体 Controller 的接口调整，必须先完成影响评审。

## 2. 预览入口契约

### 2.1 入口 A：Album Form 按钮

| 项目 | 契约 |
|---|---|
| 位置 | Album Form 顶部业务按钮区域，与审核/发布状态按钮同一操作区 |
| 文案 | `Preview Portal` |
| 可见状态 | `draft`、`pending_review`、`approved` |
| 不可见状态 | `published`、`revoked` |
| 可见角色 | 对当前 Album 具有后台读取权限的 WMS 业务用户、审核人、管理员；记录规则仍必须生效 |
| 行为 | 打开当前 Album 的预览页面，不改变当前表单状态 |

业务用户只能预览其现有后台权限允许读取的 Album；按钮隐藏不得替代服务端授权检查。

### 2.2 入口 B：审核页面按钮

当前模块没有独立的审核页面契约；审核动作在 Album Form 的状态/按钮区域完成。因此 CC-06 不新增独立审核页面：

- 审核动作继续在 Album Form 完成；
- Album Form 复用入口 A；
- 如果未来新增独立审核页面，Preview Portal 按钮的位置和授权由该上游变更处理，不由 CC-06 预先设计。

### 2.3 入口 C：审核列表按钮（可选）

审核列表入口不属于当前 SRS/TDD 的既有要求。CC-06 不强制新增列表按钮。

如项目负责人批准新增：

- 文案必须为 `Preview Portal`；
- 仅对 `draft`、`pending_review`、`approved` 行显示；
- 必须使用与入口 A 相同的 Album Form 读取权限和预览路由；
- 不得通过列表按钮绕过记录规则或状态检查。

## 3. 预览路由契约

### 3.1 主路由

预览使用后台用户路由：

```text
/odoo/evidence-albums/<int:album_id>/preview
```

方法为 `GET`，认证方式为后台用户登录（Odoo `auth="user"` 语义）。路由不接受 Portal Token，不接受匿名请求，不接受附件 ID 作为授权输入。

### 3.2 授权检查

路由进入后必须按顺序完成：

1. 确认当前请求用户是已认证后台用户；
2. 确认当前用户属于允许访问 Album 的后台角色；
3. 按现有 Album、Page、Item 记录规则读取当前 Album；
4. 确认 Album 记录存在且当前用户对其有后台读取权限；
5. 通过后返回预览页面。

未认证请求重定向到 `/web/login`，并在登录后返回原预览 URL；已认证但无权访问或记录不存在时返回 404，不泄露 Album 是否存在。该行为必须与后台现有记录权限约定一致；如果现有约定无法复用，需在实现前由上游确认。

Published/Revoked 状态的 Album 同样由服务端拒绝预览请求，返回 404 或项目统一的明确业务错误；不能仅隐藏按钮而保留可直接访问的 URL。

### 3.3 返回类型

- 返回后台认证上下文中的 HTML 页面或后台容器页面；
- 页面数据来自当前 Album、Page、Item 和媒体记录；
- 不生成发布 Token，不创建临时 Album，不复制媒体附件；
- 预览页面可以加载 CC-04 Viewer 所需的受保护媒体 URL，但媒体访问必须继续经过授权 Controller。

### 3.4 与 Portal 路由的区别

- Published Portal 路由继续使用 `/my/media-albums...` 及其兼容入口和 CC-04 Portal Access Policy；
- 预览路由不属于 `/my/...` Portal 访问面；
- 预览使用后台用户权限和 Album 后台记录规则；
- 预览不使用 Portal `base.group_portal` 授权规则，改用后台用户授权；
- Commercial Partner 授权规则不适用于预览；
- 预览不检查 `published` 状态、Token 或有效期；
- 预览不改变 CC-04 已冻结的 Portal 路由和媒体 Controller 契约。

## 4. 预览授权链契约

### 4.1 后台用户识别

- 请求必须来自已登录 Odoo 后台用户；
- 公共/匿名请求不得访问预览；
- Portal 客户登录身份不得直接转换为后台预览身份；
- 预览不使用共享密码、Token、Album Number 或可猜测 URL 作为认证。

### 4.2 角色和记录权限

预览权限以现有后台 Album 读取权限为基础：

- WMS 业务用户：仅可预览其后台记录规则允许读取的 Album；
- WMS 审核人：可预览其审核权限允许读取的 Album；
- 管理员：可预览其管理员权限允许读取的 Album；
- 具体记录规则、组继承和多公司边界不得在 CC-06 中重新定义；
- 按钮可见性不是安全边界，路由必须再次执行服务端检查。

多公司场景下，预览权限沿用 Odoo 标准多公司记录规则，不引入额外隔离逻辑；后台用户属于多个公司时，按当前公司上下文判断，管理员同样按其当前多公司权限判断。

### 4.3 与 Album 归属检查

- 必须检查 Album 记录属于当前后台用户可访问的业务范围；
- 必须沿用现有 Album/客户/公司记录规则；
- 不得把“审核人角色”解释为可以读取所有客户 Album；
- 不得以 Portal Commercial Partner 规则替代后台 Album 记录规则。

### 4.4 与 Portal 授权链的差异

预览明确不执行下列 Published Portal 条件：

- 不检查 `base.group_portal`；
- 不检查 Commercial Partner；
- 不检查 `published` 状态；
- 不检查撤销状态作为 Portal 访问条件；
- 不检查 `valid_until`；
- 不使用正式 Portal Token。

预览仍必须执行后台用户身份、角色/ACL、记录规则和 Album/Item 当前记录可读性检查。

## 5. 预览与 Portal Viewer 的复用契约

### 5.1 必须复用的展示逻辑

预览必须复用 CC-04 Portal Viewer 已冻结的展示语义，包括：

- Album 标题、客户信息、Page Tabs 和当前 Page 展示；
- Page/媒体数量和媒体类型筛选；
- 图片缩略图、图片灯箱和视频播放；
- Page 切换、媒体网格和媒体加载行为；
- 媒体不可用时的显示/错误语义；
- 低成本预览资源和受保护媒体 URL 的使用方式。

预览不得复制一套仅供后台使用的“近似 Portal”模板，导致两套展示逻辑长期漂移。

复用的技术形态由 CC-06 实现确定，但必须满足：

- 展示层（QWeb 模板和 OWL 组件）复用；
- 从 Album/Page/Item 组装 Viewer 数据结构的逻辑复用；
- 媒体 URL 模式复用；
- 授权层不复用：Preview 使用后台授权链，Published Portal 使用 CC-04 Portal 授权链。

### 5.2 允许的重构范围

如果现有 Viewer 绑定 `/my/...` Portal 页面，CC-06 可以将其展示部分重构为可接收受控 Album/Page 数据的公共 Viewer 组件或模板。重构必须满足：

- Published Portal 使用重构后的组件后，行为与 CC-04 冻结契约一致；
- 不改变 CC-04 Portal Access Policy；
- 不改变 CC-04 媒体访问路由、Item ID 边界和 `sudo()` 时序；
- 重构只涉及展示层拆解，不改变 CC-04 路由、媒体 Controller 或 OWL 组件对外接口；
- 重构完成后 CC-04 Portal 授权、媒体 Controller、缩略图路由、GET/HEAD、Range、MIME、404 和 OWL 渲染/交互回归必须继续通过；
- 不把后台预览授权逻辑塞入 Published Portal 授权链；
- 不将预览模式作为前端可篡改的安全开关；
- 预览模式由服务端授权后的页面上下文确定。

### 5.3 预览专属 UI 提示

预览页面必须明确显示当前为预览，例如 `Portal Preview — Not Published`。该提示：

- 只用于防止审核人误认为已经发布；
- 不得改变 Viewer 的媒体展示逻辑；
- 不得生成对客户可分享的外部链接。

## 6. 预览与 Published Portal 的行为差异契约

| 行为 | Preview | Published Portal |
|---|---|---|
| 展示 Page、媒体 | ✅ 使用同一展示逻辑 | ✅ 使用 CC-04 展示逻辑 |
| 媒体灯箱 | ✅ 相同 | ✅ 相同 |
| 视频播放 | ✅ 相同 | ✅ 相同 |
| 单文件下载 | ⚠️ 仅在复用既有后台授权且不扩大范围时允许；默认不作为 CC-06 必需能力 | ✅ 按 CC-04 契约 |
| 多选批量下载 | ❌ 不提供 | ✅ 按 CC-05，限当前 Page |
| 后台用户授权 | ✅ 检查后台身份、角色、ACL 和记录规则 | ❌ 不使用后台授权链 |
| Portal 客户授权 | ❌ 不检查 | ✅ 检查 Portal 用户和 Commercial Partner |
| Token | ❌ 不使用、不生成 | ✅ 发布时生成并按既有规则使用 |
| 有效期 | ❌ 不检查 | ✅ 检查 |
| `published` 状态 | ❌ Draft/Pending Review/Approved 可预览；Published 入口隐藏且服务端拒绝 | ✅ 必须为已发布 |
| 撤销状态 | ❌ Revoked 入口隐藏且服务端拒绝 | ✅ 撤销后拒绝 |
| 预览提示 | ✅ 显示未发布提示 | ❌ 不显示 |
| 返回行为 | ✅ 返回当前 Album Form | ✅ 返回 Portal 相册列表/查看器导航 |
| 媒体不可用 | ✅ 按 CC-04 语义显示不可用 | ✅ 按 CC-04 语义显示不可用 |

Published/Revoked Album 不属于“发布前预览”范围；其既有 Portal 访问行为不因 CC-06 改变。入口按钮隐藏且服务端拒绝直接 URL 访问；若需要支持已发布 Album 的后台复看，必须另行提出上游变更，不在 CC-06 默认范围内。

## 7. 预览限制契约

- 预览 URL 只对已认证且有后台 Album 权限的用户有效；
- 不提供匿名访问、Token 访问或客户 Portal 访问；
- 不生成可分享的正式 Portal URL；
- 不生成或重置 Token；
- 不执行发布、审核、批准、拒绝、撤销或恢复动作；
- 不改变 `state`、`token`、`published_at`、`revoked_at`、`reviewed_by` 或有效期；
- 不允许访问当前后台用户无权访问的其他客户 Album；
- 不提供多选批量下载；
- 不通过预览路由直接读取附件 ID 或 `/web/content` 绕过媒体授权；
- 不将预览结果缓存为可脱离后台会话访问的公共资源；
- 预览页面不得提供会改变 Album/Item 数据的编辑操作；编辑仍返回 Album Form 或使用既有后台编辑入口。
- 预览页面不提供添加/删除 Page、添加/删除 Item、修改 Page/Item 字段、修改 Album 字段或修改媒体说明；
- 如需编辑，用户必须返回 Album Form，使用既有后台编辑入口。

## 8. 预览返回契约

- 预览页面必须提供 `Back to Album` 按钮；
- 返回目标为当前 Album Form；
- 返回不得改变 Album 状态、审核人、Token、发布时间、撤销时间或有效期；
- 浏览器后退和显式返回均不得触发发布/审核动作；
- 如果打开预览前 Album Form 存在未保存修改，优先保留未保存状态；若实现无法保留，返回时必须明确提示“未保存修改已丢失”，具体行为必须记录在 IHR 中；
- 预览失败时返回明确的后台错误，不显示 Portal 成功页面，不产生成功形状的空数据；
- 若媒体记录在打开预览后变为不可用，页面必须遵守 CC-04 媒体不可用语义，不得静默显示不存在的媒体。

## 9. 后台界面契约

### 9.1 Album Form

- 顶部操作区提供 `Preview Portal`；
- 与状态按钮并列但视觉上明确为查看动作，不得让用户误解为 `Publish`；
- 预览模式页面显示 `Portal Preview — Not Published`；
- 返回按钮回到当前 Album Form。

### 9.2 审核页面

- CC-06 不新增独立审核页面，审核动作继续在 Album Form 完成；
- 如果未来由独立上游变更新增审核页面，Preview Portal 按钮的位置和授权由该变更处理；
- 审核页面不得复制 Portal Viewer 逻辑，必须复用 CC-04 Viewer 展示部分。

### 9.3 审核列表

- 当前不强制提供列表预览按钮；
- 若增加，必须沿用入口 A 的状态、权限和路由契约；
- 列表入口不能在没有读取权限时暴露 Album 标题或预览 URL。

### 9.4 页面布局

默认使用独立后台页面或后台容器页面，不要求把 Viewer 嵌入 Album Form。若实现选择嵌入，必须保持：

- 预览上下文不会改变 Album Form 的保存状态；
- Viewer 的媒体加载和授权仍走同一受保护逻辑；
- 返回 Album Form 不丢失未保存的表单状态；否则必须在上游确认返回策略。

## 10. 权限契约

| 角色 | Draft | Pending Review | Approved | Published | Revoked |
|---|---:|---:|---:|---:|---:|
| WMS 业务用户（有记录读取权限） | ✅ | ✅ | ✅ | ❌（默认不属于发布前预览） | ❌ |
| WMS 审核人（有记录读取权限） | ✅ | ✅ | ✅ | ❌（默认不属于发布前预览） | ❌ |
| 管理员 | ✅ | ✅ | ✅ | ❌（默认不属于发布前预览） | ❌ |
| Portal 客户 | ❌ | ❌ | ❌ | 仅按 CC-04 Published Portal 访问 | ❌ |

说明：

- “业务用户可预览”不扩大其审核、批准或发布权限；
- 审核人可预览不代表自动获得所有 Album 的读取权限；
- Portal 客户不使用后台预览入口；
- Published/Revoked 行为如需改变，必须通过独立上游变更确认。

## 11. 测试和验证契约

CC-06 不在本文件编写测试用例；以下是必须覆盖的验证主题和证据要求。

### 11.1 自动化验证

至少验证：

- Draft、Pending Review、Approved 入口可见且路由可访问；
- Published、Revoked 入口行为符合本契约；
- 路由要求后台登录并执行角色、ACL、记录规则检查；
- 预览不使用或生成 Token；
- 预览不使用 Portal Commercial Partner 授权规则，改用后台记录规则；
- 预览不检查 `valid_until`；有效期是 Published Portal 的客户访问条件，不适用于后台预览；
- 预览不要求 `published`；
- 预览不改变 Album 状态、Token、`published_at`、`revoked_at`；
- 预览不能访问其他客户或当前用户无权读取的 Album；
- 预览不生成公开/匿名可分享资源；
- 预览不提供批量下载；
- Portal Viewer 和 Preview 使用同一展示组件/模板逻辑；
- Published Portal 的授权链和媒体 Controller 回归不受影响；
- CC-04 的 Portal 授权链、媒体 Controller（GET/HEAD、Range、MIME、404）、缩略图路由和 OWL 组件渲染/交互回归继续通过；如因 CC-06 重构失败，CC-06 不得关闭。

### 11.2 浏览器人工验证

至少覆盖：

- 业务用户打开 Draft Album 预览；
- 审核人在 Pending Review Album 预览；
- 审核人在 Approved Album 预览；
- 审核页面（若存在独立页面）打开预览；
- 预览与 Published Portal 的 Page、媒体网格、图片灯箱和视频展示视觉一致；
- 预览页面显示未发布提示；
- 预览不提供批量下载；
- 预览返回当前 Album Form；
- 不同后台角色的预览权限；
- Portal 客户无法使用后台预览入口；
- 跨客户或无记录权限 Album 被拒绝。

每个 HVR 场景必须标注证据来源：

- `user-confirmed`
- `agent-observed`
- `automated`

只有 `user-confirmed` 可计入正式 HVR PASS。

### 11.3 关闭材料

CC-06 关闭前必须形成：

- `wd_evidence_album_CC-06_IHR_v1.0.0.md`
- `wd_evidence_album_CC-06_ATR_v1.0.0.md`
- `wd_evidence_album_CC-06_HVR_v1.0.0.md`
- `wd_evidence_album_CC-06_FR_v1.0.0.md`

关闭材料必须区分“预览功能通过”和“上游 SRS/技术债/Implementation Plan 文档已补齐”，不得只用浏览器观察替代契约治理。

## 12. 验收条件

| ID | 验收条件 | 必需证据 |
|---|---|---|
| AC-01 | Draft、Pending Review、Approved Album 提供可用的 `Preview Portal` 入口 | 自动化验证 + HVR |
| AC-02 | 预览使用后台用户身份、角色、ACL 和记录规则，不依赖 Portal 授权 | 自动化授权验证 + HVR |
| AC-03 | 预览复用 CC-04 Portal Viewer 的展示逻辑 | 组件/模板追踪 + 视觉 HVR |
| AC-04 | 预览不改变 Album 状态、Token、`published_at`、`revoked_at`、`reviewed_by` 或有效期 | 自动化前后状态断言 |
| AC-05 | 预览不生成可分享的正式 Portal URL、Token 或匿名访问能力 | 路由/响应验证 |
| AC-06 | 预览不提供多选批量下载 | HVR + 路由/页面验证 |
| AC-07 | 预览不能访问其他客户或当前后台用户无权读取的 Album | 授权自动化 + HVR |
| AC-08 | 预览提供返回当前 Album Form 的路径，返回不触发状态动作 | HVR + 浏览器网络/状态记录 |
| AC-09 | 业务用户、审核人、管理员和 Portal 客户的预览权限符合本契约 | 权限矩阵验证 + HVR |
| AC-10 | CC-06 IHR、ATR、HVR、FR 已形成，并区分用户确认与 Agent 观察 | 关闭材料审查 |

## 13. 追溯矩阵

由于 SRS 和 Implementation Plan 尚未包含 CC-06，相关条目标记为待补充。这里的“待补充”属于进入编码前的上游文档门禁，不是本契约的遗漏，也不将本契约新增内容伪装成既有冻结条款。

| CC-06 契约主题 | SRS | TDD | Implementation Plan | Technical Debt Register |
|---|---|---|---|---|
| 发布前预览业务需求 | **待补充 BR-XX**；现有 SRS 仅定义客户查看已发布相册（§8、§9、§10） | **待补充**；现有 §6/§7/§9/§12 仅定义 Published Portal | **待补充 CC-06 任务** | **待登记预览缺口** |
| 后台角色和 Album 读取权限 | §9 权限矩阵 | §11 权限设计 | CC-03 §4.3/§4.4 | 复用现有记录 |
| 状态允许范围 | §10.1 状态机 | §5 状态和动作 | CC-03 §4 | 无新增债务 |
| Published Portal 授权差异 | §9、§11 | §6、§7、§12 | CC-04 §5.3 | 无修改既有债务 |
| Viewer 展示复用 | §8、§11、§12、§13 | §9、§12 | CC-04 §5.2-§5.5 | TD-002 已关闭，但不覆盖此项 |
| 媒体低成本预览 | §8.6、相关性能验收 | §7、§9.3 | CC-04 §5.5 | TDD-Q-007 按原治理 |
| 不提供批量下载 | SRS §8.8 仅适用于 Published Portal ZIP | CC-05 ZIP 契约 | CC-05 §5.3-§5.5 | 不修改 CC-05 |
| 关闭材料 | §18 验收标准 | §14 验证设计 | CC-03/04/05 关闭材料模式 | 需新增变更记录 |

## 14. 未解决项和升级规则

### 14.1 SRS 待补充项

当前未检索到正式 `BR-XX Portal Preview`。在 CC-06 开始编码前，SRS 必须补充：

- 预览对象、允许状态和角色；
- 预览不等于发布；
- 预览不生成客户访问权限；
- 预览与 Published Portal 的授权和行为差异；
- 建议使用 `BR-XX Portal Preview` 作为业务需求标题，具体编号由 SRS 维护流程分配；
- 至少对应本契约 AC-01 至 AC-10 的业务验收条款。

### 14.2 Implementation Plan 待补充项

当前 Implementation Plan 只拆分至 CC-05。必须补充 CC-06 的：

- 输入基线和依赖；
- 预览入口、路由、授权和 Viewer 复用任务；
- 回归边界；
- IHR/ATR/HVR/FR 输出和完成条件。

### 14.3 Technical Debt Register 待登记项

当前登记册没有“发布前 Portal 效果预览”条目。建议通过版本化变更登记为新条目，而不是修改 TD-002：

- 当前现状：发布前只能使用后台视角，无法确认客户 Portal 实际效果；
- 目标状态：有后台权限的用户可在 Draft/Pending Review/Approved 状态预览；
- 关闭条件：本契约 AC-01 至 AC-10 通过并形成 CC-06 关闭材料；
- 责任范围：CC-06；
- 编号、严重度、最晚处理节点：由项目负责人按技术债流程确认。

### 14.4 路由和 Published/Revoked 行为确认

本契约采用 `/odoo/evidence-albums/<int:album_id>/preview` 作为后台预览路由，并默认隐藏 Published/Revoked 入口。若项目希望：

- 允许后台复看已发布相册；
- 允许撤销相册预览；
- 使用其他 URL；
- 允许预览单文件下载；

必须在编码前形成上游确认并更新本契约；不得由实现阶段自行扩大范围。

## 15. 审批记录

| 版本 | 日期 | 变更 | 审批人 | 审批日期 |
|---|---|---|---|---|
| v1.0.0 | 2026-09-29 | 按评审意见修订并冻结 CC-06 Coding Contract：加入上游文档硬门禁、明确未认证/已发布/已撤销请求行为、细化 Viewer 复用和 CC-04 回归边界；项目负责人批准冻结，保留上游文档补齐前不得进入编码的硬门禁。 | 本会话用户（项目负责人批准） | 2026-09-29 |

## 附录 A：与 Published Portal 的行为对比表

| 维度 | Preview | Published Portal |
|---|---|---|
| 访问主体 | 已登录后台用户 | 已登录 Portal 用户 |
| 数据来源 | 当前 Album/Page/Item | 当前已发布 Album/Page/Item |
| 允许状态 | Draft、Pending Review、Approved | Published，且未撤销、未过期 |
| 认证 | 后台会话 | Portal 会话 |
| 记录授权 | 后台角色、ACL、记录规则 | Portal Access Policy |
| Commercial Partner | 不适用；使用后台记录规则 | 检查 |
| Token | 不使用 | 按发布规则使用 |
| 有效期 | 不适用；不作为后台预览条件 | 检查 |
| Viewer | 复用 CC-04 展示逻辑 | CC-04 Viewer |
| 媒体访问 | 受保护媒体访问；不得绕过授权 | CC-04 媒体 Controller |
| 批量 ZIP | 不提供 | 按 CC-05，当前 Page 范围 |
| 状态变化 | 不允许 | 客户无状态操作 |
| 可分享性 | 不可分享 | 按正式 Portal 发布语义 |
| 返回 | Album Form | Portal 相册列表/查看器导航 |

## 附录 B：CC-06 不承诺的接口

CC-06 不承诺新增或修改以下接口：

- CC-04 Published Portal Access Policy；
- CC-04 `/my/media-albums...` 路由；
- CC-04 媒体、缩略图、单文件下载 Controller；
- CC-05 `/my/media-albums/batch-download`；
- Token 生成、重置或验证接口；
- 匿名或公开预览 URL；
- 客户上传、评论、点赞接口；
- 视频转码、图片编辑接口。

预览页面的媒体访问必须：

- 复用 CC-04 的媒体 Controller；
- 复用 CC-04 的媒体 URL 模式和 Item ID 边界；
- 不引入新的媒体路由；
- 继续由媒体 Controller 承担授权，后台预览不通过页面参数绕过该授权。

预览路由仅是后台会话下的预览入口；任何需要改变上述接口语义的需求，必须进入独立的上游变更评审。
