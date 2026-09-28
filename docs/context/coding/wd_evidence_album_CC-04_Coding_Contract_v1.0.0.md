# WMS Evidence Album — Coding Contract CC-04
# Portal 查看器

## 0. 文档信息

| 项目 | 内容 |
|---|---|
| 模块 | `wd_evidence_album` |
| CC | CC-04 — Portal 查看器 |
| CC 版本 | v1.0.0 |
| 状态 | Frozen Coding Contract |
| Odoo | 18.0 Community Edition |
| 代码目录 | `/Users/lijianqiang/Documents/odoo18_album/mymodules/wd_evidence_album` |
| 上游业务基线 | SRS v1.0.0（Frozen） |
| 上游技术基线 | TDD v1.0.0（Frozen Implementation Baseline） |
| 实施规划基线 | Implementation Plan v1.0.0（Frozen Implementation Plan） |
| 前置编码基线 | CC-03 已冻结并推送；发布、撤销和有效期入口已存在 |
| 关联技术债 | TD-001 Open；TD-002 Open |

本契约只允许在审批冻结后进入 CC-04 编码。它不替代 SRS/TDD，不提前实现 CC-05 ZIP 下载。

## 1. 范围和目标

CC-04 实现登录 Portal 客户访问自己有效 Album 的完整查看器：

1. Portal Album 分页列表；
2. Album 查看器页面；
3. Page 切换和媒体类型筛选；
4. 图片缩略图、灯箱和视频内联播放；
5. 单个媒体文件下载；
6. 统一 Portal 授权策略；
7. 使用 Item ID 的自定义媒体/下载 Controller；
8. 低成本图片预览或缩略图；
9. OWL 前端交互。

## 2. 明确排除

CC-04 不实现：

- 多选媒体状态栏；
- ZIP 生成、ZIP 限制、ZIP 文件名清洗；
- 长期保存 ZIP；
- 匿名分享或 Token 独立授权；
- Portal 客户编辑 Album、Page、Item；
- 客户上传、评论、点赞；
- 图片编辑、视频转码；
- `wd_qooling_app` 依赖或 Widget；
- CC-05 的任何批量下载行为。

单文件下载属于 CC-04，但必须复用与媒体预览相同的授权入口；多文件 ZIP 明确属于 CC-05。

## 3. 前置门禁和未解决项

### 3.1 前置门禁

- CC-03 已冻结，存在 `published`、`revoked_at`、`valid_until` 和 `is_expired()`；
- Album 客户在写入时已规范化为 Commercial Partner；
- Item 的附件、媒体类型和 `availability_state` 已由 CC-02 建立；
- Portal Controller 必须在附件 `sudo()` 读取前完成全部 Album/Item 授权；
- 不得使用 Odoo 默认 `/web/content` 作为 CC-04 媒体授权路由。

### 3.2 TDD-Q-003：来源信息展示配置

TDD-Q-003 尚未在 CC-03 关闭。CC-04 必须在实现来源信息展示前明确：

- Portal 默认不展示来源信息；
- 如果展示，展示哪些来源字段；
- 配置归属和读取权限；
- 未配置时的稳定返回结构。

在 TDD-Q-003 决策完成前，CC-04 可以先实现不展示来源信息的核心列表、查看器、媒体和单文件下载；不得自行推断来源展示规则。

### 3.3 TDD-Q-007：缩略图策略

TDD-Q-007 必须在 CC-04-T05 开始前确定：

- 优先使用 Odoo 原生图像处理能力；
- 原生能力不足时，使用 Controller 内存生成的短生命周期缩略图；
- 不创建长期业务附件副本；
- 视频不转码，可使用媒体类型占位或 poster 策略。

缩略图策略不改变 Portal 授权链；缩略图路由必须同样先授权、后读取附件。

## 4. 角色和访问边界

### 4.1 角色

| 角色 | Portal 列表 | 查看 Album | 查看媒体 | 单文件下载 |
|---|---:|---:|---:|---:|
| 未登录用户 | 否，进入登录 | 否 | 否 | 否 |
| 已登录非 Portal 用户 | 否 | 否 | 否 | 否 |
| Portal 客户 | 仅自己的有效 Album | 仅自己的有效 Album | 仅其中有效 Item | 仅其中有效 Item |
| WMS 业务用户 | 不通过 Portal | 不通过 Portal | 不通过 Portal | 不通过 Portal |
| WMS 审核人 | 不通过 Portal | 不通过 Portal | 不通过 Portal | 不通过 Portal |
| 管理员 | 不通过 Portal | 不通过 Portal | 不通过 Portal | 不通过 Portal |

后台组不能替代 Portal 组；后台用户即使具有 Album 管理权限，也不能因此通过 Portal 路由访问客户页面。

### 4.2 统一授权条件

每个列表、页面、媒体和下载请求必须按以下顺序检查：

1. 路由使用 `auth="user"`；
2. 当前用户属于 `base.group_portal`；
3. Album 存在；
4. Album `customer_id.commercial_partner_id` 等于当前用户 partner 的 Commercial Partner；
5. Album 状态为 `published`；
6. Album 未撤销；
7. Album 未过期：`valid_until` 为空，或服务器时间 `< valid_until`；
8. Item/Page 属于该 Album；
9. Item 有附件且 `availability_state == "available"`；
10. 以上检查完成后，才允许对附件使用 `sudo()` 读取二进制。

未授权、跨客户、不存在、撤销、过期和不可用 Item 的媒体请求统一返回 404，不泄露资源是否存在。

### 4.3 Token 边界

- Token 不作为 Portal 登录凭证；
- Token 不绕过 `base.group_portal`；
- Token 不绕过 Commercial Partner 校验；
- Token 不作为媒体或附件路由的唯一授权条件；
- CC-04 不新增 Token 访问路径。

## 5. 数据返回边界

### 5.1 Album 列表

列表只返回当前 Portal 用户所属 Commercial Partner 的：

- `published` Album；
- 未撤销 Album；
- 未过期 Album。

列表必须分页，不返回不属于当前用户的 Album 数量、名称或 ID。

### 5.2 查看器数据

查看器返回：

- Album 名称；
- 客户名称；
- Page 标题、描述和媒体数量；
- 当前 Album 内 Page 顺序；
- Item ID、媒体类型、说明和受控媒体 URL；
- 受 TDD-Q-003 决策控制的来源信息。

不得返回：

- 原始 `attachment_id` 作为授权资源；
- `attachment_id` 或任何可直接构造 `/web/content/<id>` 的信息不得出现在返回的 HTML、JSON、OWL props 或其他前端可见数据中；媒体 URL 必须以 Item ID 为唯一边界；
- 来源业务记录的敏感字段；
- 未授权 Album/Page/Item；
- Token 作为可点击访问凭证。

### 5.3 媒体 URL

媒体 URL 必须以 Item 为边界：

```text
/my/evidence-albums/items/<int:item_id>/media
/my/evidence-albums/items/<int:item_id>/download
```

不实现仅以 `attachment_id` 为资源边界的公开路由。

## 6. 任务拆分

### CC-04-T01 Portal 访问策略

- **输入**：TDD §6、SRS §8.2、TV-02；
- **工作范围**：统一实现 Portal 组、Commercial Partner、Album 状态、撤销、有效期、Page/Item 归属和媒体可用性检查；
- **输出**：所有 Portal 路由可复用的授权入口；
- **依赖**：CC-03；
- **完成条件**：任何附件 `sudo()` 读取前，授权链已经完成；未授权资源按 404 处理；不使用 `sudo()` 替代授权。

### CC-04-T02 Portal 列表和查看器页面

- **输入**：TDD §9、§12、TDD-Q-003；
- **工作范围**：Portal Album 分页列表、Album 详情、Page Tabs、媒体数量和受控数据结构；
- **输出**：Portal QWeb 页面和 OWL 挂载数据；
- **依赖**：CC-04-T01；
- **完成条件**：只显示当前 Commercial Partner 的有效 Album；Page 不跨 Album；来源信息在 TDD-Q-003 未决时默认不展示。

TDD-Q-003 未决时，查看器数据不包含来源信息字段，或明确返回 `source_info: null`；不得返回部分来源字段，前端必须能在字段缺失时正常渲染。

### CC-04-T03 媒体 Controller

- **输入**：TDD §7、§12、TV-01；
- **工作范围**：Item 媒体流、单文件下载、准确 MIME、响应头、不可用处理和 HTTP Range；
- **输出**：自定义媒体和单文件下载路由；
- **依赖**：CC-04-T01、CC-03；
- **完成条件**：
  - 不使用 `/web/content`；
  - 授权后才 `sudo()` 读取附件；
  - 图片/视频响应 MIME 正确；
  - 预览使用 inline，下载使用 attachment；
  - 视频支持 `Range`、`206`、`Content-Range` 和无效范围 `416`；
  - `HEAD` 必须复用同一授权链，只返回响应头、不返回 body；HEAD 授权失败与 GET 一致，返回 404；
  - 不区分不存在与未授权资源。

### CC-04-T04 OWL 查看器交互

- **输入**：TDD §9、TV-04；
- **工作范围**：PageTabs、MediaFilter、MediaGrid、图片灯箱、视频播放和媒体加载错误状态；
- **输出**：`web.assets_frontend` 中的 OWL 组件；
- **依赖**：CC-04-T02、CC-04-T03；
- **完成条件**：
  - 图片支持放大、全屏、上一张/下一张；
  - 视频使用受保护媒体 URL 和原生 controls；
  - 选择状态只服务于查看器展示，不实现 ZIP；
  - 媒体网格不无条件加载原始大文件；
  - 前端隐藏不能替代 Controller 授权。

### CC-04-T05 缩略图和低成本预览

- **输入**：TDD §9.3、TDD-Q-007；
- **工作范围**：受授权保护的图片缩略图或等效低成本预览、视频占位/poster；
- **输出**：缩略图变体或短生命周期内存预览；
- **依赖**：CC-04-T03；
- **完成条件**：列表使用低成本资源；不创建长期附件副本；缩略图与原图共享授权链；不实现视频转码。

在 TDD-Q-007 决策完成前，T05 使用 Odoo 原生图像处理能力作为默认方案，并在 IHR 中登记为“待 TDD-Q-007 确认”；如最终决策改为内存生成，切换不得改变授权链和资源边界。

### CC-04-T06 CC-04 关闭材料

- **输入**：CC-04 所有任务输出；
- **工作范围**：整理实施、自动化验证、浏览器人工验证和遗留问题；
- **输出**：CC-04 IHR、ATR、HVR 和 FR；
- **依赖**：CC-04-T01 至 CC-04-T05；
- **完成条件**：Portal 访问、跨客户拒绝、过期/撤销拒绝、媒体预览、灯箱、视频、单文件下载和低成本资源均有证据。

## 7. 路由契约

| 路由 | 方法 | 认证 | 成功 | 未授权/不存在 | 业务错误 |
|---|---|---|---|---|---|
| `/my/evidence-albums` | GET | `user` | Portal HTML，分页列表 | 登录重定向或空/受控列表 | 500 |
| `/my/evidence-albums/<int:album_id>` | GET | `user` | Portal HTML，查看器 | 404 | 500 |
| `/my/evidence-albums/items/<int:item_id>/media` | GET/HEAD | `user` | 图片/视频流 | 404 | 404 |
| `/my/evidence-albums/items/<int:item_id>/download` | GET | `user` | 单文件下载 | 404 | 404 |

共同要求：

- 所有路由显式使用 `auth="user"`；
- 所有路由显式检查 `base.group_portal`；
- 所有路由调用同一 Portal Access Policy；
- `/my/evidence-albums` 未登录时按 Odoo Portal 标准重定向到登录页；已登录但非 Portal 用户返回 404；其他路由未登录请求按 Odoo Portal 标准重定向，登录后仍按统一授权链拒绝；
- 媒体/下载路由不使用 `/web/content`；
- 不在响应中泄露附件内部路径、来源 ACL 或资源存在性；
- 不新增 ZIP 路由，ZIP 留给 CC-05。

## 8. 安全和资源要求

### 8.1 `sudo()` 边界

固定流程：

```text
普通 env 查询 Item
→ 普通 env 校验 Item/Page/Album 关系
→ 普通 env 校验 Portal/Commercial Partner/状态/有效期
→ 普通 env 校验附件存在和可用性
→ 取得已授权 attachment_id
→ 仅对该 attachment_id 使用 sudo() 读取二进制
→ 返回响应
```

禁止先 `sudo()` 查询附件，再补做业务授权。

### 8.2 媒体响应

- 图片返回准确的图片 MIME；
- 视频返回 `video/mp4`；
- 设置 `Content-Length`、`Content-Disposition` 和安全缓存策略；
- 预览 inline，下载 attachment；
- Range 请求符合 RFC 7233：格式不合法、范围超出文件长度或起点大于终点均返回 `416`，并设置 `Content-Range: bytes */<total_length>`；有效部分响应返回 `206` 和准确 `Content-Range`；
- 不可用附件返回 404；
- 不返回异常堆栈、文件路径或业务模型权限细节。

### 8.3 性能

- Album 列表分页；
- 媒体网格使用缩略图或等效低成本预览；
- 图片原图在用户打开预览后再请求；
- 视频列表不自动加载完整媒体；
- 缩略图不创建长期 `ir.attachment` 副本；
- CC-04 不定义 ZIP 的文件数、总大小、内存或并发限制，这些属于 CC-05/TDD-Q-004。

## 9. 验证契约

### 9.1 自动化验证

至少覆盖：

- 未登录请求进入登录流程；
- 非 Portal 后台用户被拒绝；
- 同 Commercial Partner 的多个 Portal 联系人可访问；
- 跨 Commercial Partner Album 返回 404；
- draft、pending_review、approved Album 不出现在 Portal；
- revoked Album 不出现在列表且媒体返回 404；
- 过期 Album 不出现在列表且媒体返回 404；
- Page/Item 不属于请求 Album 时返回 404；
- 不可用 Item 返回 404；
- 授权完成前不发生附件 `sudo()` 读取；验证方式是使用 mock、测试钩子或 ORM 日志记录调用顺序，确认 `base.group_portal`、Commercial Partner、Album 状态、撤销、有效期和 Item 归属均检查完成后才发生 `sudo()`；
- 缩略图路由复用同一 Portal Access Policy；未授权缩略图请求返回 404，不因缩略图不是原图而放宽授权；
- 图片媒体 MIME 和 inline 响应正确；
- 单文件下载 Content-Disposition 正确；
- 视频 Range 返回 `206`、`Content-Range` 和无效范围 `416`；
- 不使用 `/web/content`；
- CC-03 `is_expired()` 作为统一有效期入口；
- CC-01/CC-02 媒体和 Item 回归验证继续通过。

### 9.2 浏览器人工验证

HVR 至少覆盖：

1. Portal 用户登录后看到自己的有效 Album 列表；
2. 同公司其他 Portal 联系人可以看到同一 Album；
3. 跨客户 Album 不可见；使用两个不同 Commercial Partner 的 Portal 账号分别登录，确认彼此看不到对方 Album，并直接构造对方 Album URL 确认返回 404；
4. 过期和撤销 Album 不可见；
5. Album 查看器显示 Page、媒体数量和 Item；
6. Page 切换和全部/图片/视频筛选可用；
7. 图片缩略图、灯箱、全屏和前后切换可用；
8. 视频可内联播放和全屏；
9. 单文件下载成功；
10. 不可用媒体显示受控错误，不泄露附件细节。

每个 HVR 场景必须标注证据来源：

- `user-confirmed`：用户亲自执行并确认；
- `agent-observed`：Agent 执行、用户观察结果；
- `automated`：自动化测试证据。

只有 `user-confirmed` 计入正式 HVR PASS。

### 9.3 关闭材料

CC-04 关闭前必须形成：

- CC-04 IHR；
- CC-04 ATR；
- CC-04 HVR；
- CC-04 FR；
- TDD-Q-003 和 TDD-Q-007 的决策/阻塞记录；
- 明确 CC-05 ZIP 尚未实现。

## 10. 验收条件

| 编号 | 验收条件 |
|---|---|
| AC-01 | Portal 用户只能看到其 Commercial Partner 的已发布、未撤销、未过期 Album |
| AC-02 | 未登录、非 Portal、跨客户、未发布、撤销和过期访问均被拒绝 |
| AC-03 | Album 列表分页，查看器显示 Page、媒体数量和媒体类型 |
| AC-04 | Page 切换和全部/图片/视频筛选可用 |
| AC-05 | 图片灯箱和视频内联播放使用自定义媒体 Controller |
| AC-06 | 单文件下载使用自定义路由；不使用 `/web/content` |
| AC-07a | 媒体授权先于 `sudo()`，完整授权链通过后才读取附件 |
| AC-07b | 媒体资源以 Item ID 为边界，不以 attachment_id 为边界；不实现仅以 attachment_id 为资源边界的公开路由 |
| AC-08 | 图片网格不无条件加载原始大文件，视频支持 Range 设计 |
| AC-09 | TDD-Q-003/TDD-Q-007 未决范围不被隐式实现 |
| AC-10 | CC-04 IHR、ATR、HVR 和 FR 形成；ZIP 保持 CC-05 边界 |
| AC-11 | CC-04 代码、前端组件及验证材料不包含 ZIP 路由、ZIP 生成逻辑、多选下载状态栏、ZIP 按钮或 ZIP 场景 |

## 11. 追溯矩阵

| CC-04 契约 | SRS | TDD | Implementation Plan |
|---|---|---|---|
| Portal Album 列表 | §8.1、§9 | §6、§9 | CC-04-T01、T02 |
| Portal 授权 | §8.2、§9 | §6 | CC-04-T01 |
| Token 不作为 Portal 授权 | §8.2、§11 | §6.4、§7.6 | CC-04-T01 |
| Album 查看器 | §8.3、§8.5 | §9、§12 | CC-04-T02、T04 |
| 图片/视频预览 | §8.4、§12 | §7、§9 | CC-04-T03、T04、T05 |
| 单文件下载 | §8.7、§11 | §7、§12 | CC-04-T03 |
| Range 和低成本资源 | §12、§14.1 | §7.4、§9.3 | CC-04-T03、T05 |
| 来源信息边界 | §8.6 | TDD-Q-003 | CC-04-T02 |
| 多选 ZIP | §8.8、§11 | §8、§12 | CC-05，不属于 CC-04 |
| 关闭材料 | — | 测试和证据要求 | CC-04-T06 |

## 12. 未解决项和升级规则

| 项目 | 当前状态 | 对 CC-04 的影响 |
|---|---|---|
| TDD-Q-003 来源信息展示配置 | 未解决 | 不阻塞 CC-04-T01、T03、T04、T05 及 T02 的基础列表/查看器；阻塞 T02 的来源信息展示部分 |
| TDD-Q-007 图片缩略图实现方式 | 未解决 | 不阻塞授权和基础页面；阻塞 T05 的最终实现选择 |
| TDD-Q-004 ZIP 资源配置 | 未解决 | 不阻塞 CC-04；必须在 CC-05 开始前解决 |
| TD-001 Source Config field_name | Open | CC-04 不修改 |
| TD-002 Gallery Widget | Open | CC-04 不引入 `wd_qooling_app` 依赖 |

### 12.1 CC-04 与 CC-05 接口

CC-04 为 CC-05 提供：

- 已授权的 Item 查询入口；
- 以 Item ID 为边界的媒体 URL 模式；
- 可复用的 Portal Access Policy；
- OWL 查看器的选择状态扩展点。

CC-05 不得重新实现 Portal 授权、媒体 URL 或 Item 查询。

如果 TDD-Q-003 或 TDD-Q-007 的决策改变 SRS 业务语义，必须暂停受影响任务并回到 SRS/TDD 修订；不得通过实现细节自行改变契约。

## 13. 审批记录

| 版本 | 日期 | 变更 | 审批人 | 审批日期 |
|---|---|---|---|---|
| v1.0.0 | 2026-09-28 | 起草 CC-04 Portal 查看器 Coding Contract | 待审批 | 待审批 |
| v1.0.1 | 2026-09-28 | 根据评审意见补充 attachment_id 泄露边界、HEAD/Range 语义、授权顺序验证、AC-07 拆分、TDD-Q-003 范围和 CC-05 接口；评审结论 Approved with revisions | 本会话用户 | 2026-09-28 |
| v1.0.2 | 2026-09-28 | 批准冻结 CC-04，允许进入编码实施 | 本会话用户 | 2026-09-28 |
| v1.0.3 | 2026-09-28 | 批准 CC-04 开始编码实施 | 本会话用户 | 2026-09-28 |
