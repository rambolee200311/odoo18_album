# WMS Evidence Album — Coding Contract CC-05
# 技术债清理与 Portal 批量 ZIP 下载

## 0. 文档信息

| 项目 | 内容 |
|---|---|
| 模块 | `wd_evidence_album` |
| CC | CC-05 — 技术债清理与 Portal 批量 ZIP 下载 |
| CC 版本 | v1.0.0 |
| 状态 | Frozen Coding Contract |
| Odoo | 18.0 Community Edition |
| 代码目录 | `/Users/lijianqiang/Documents/odoo18_album/mymodules/wd_evidence_album` |
| 上游业务基线 | SRS v1.0.0（Frozen） |
| 上游技术基线 | TDD v1.0.0（Frozen Implementation Baseline） |
| 实施规划基线 | Implementation Plan v1.0.0（Frozen Implementation Plan） |
| 变更契约 | [CC-05 Frozen Change Contract](./wd_evidence_album_CC-05_Technical_Debt_Draft_v1.0.0.md) |
| 前置编码基线 | CC-04 已冻结并推送；Portal 单文件查看、下载和授权边界已存在 |
| 关联技术债 | TD-001 Open；TDD-Q-008 Open；TDD-Q-004 Open |

本契约只允许在前置门禁满足后进入对应实现。冻结本契约不表示 TD-001、TDD-Q-008 或 TDD-Q-004 已关闭，也不允许跳过资源和动态来源验证。

## 1. 目标

CC-05 实现以下目标：

1. 为 Source Config 提供合法附件字段的后台候选选择入口，保留服务端复核和现有文本配置兼容性；
2. 形成动态来源 Registry、模型访问、`record[field_name]` 和附件 Recordset 的可审计运行时验证；
3. 在当前 Portal Page 内提供 Item 多选和批量 ZIP 下载；
4. 在授权先于附件读取的前提下，落实 ZIP 文件数、总大小、内存、超时和并发限制；
5. 形成 ZIP 文件名清洗、唯一化、错误处理和资源释放的完整边界；
6. 回归 CC-04 单文件预览、下载、Item ID 媒体边界和 Portal 授权。

## 2. 明确排除

CC-05 不实现：

- 匿名 Token 下载；
- Portal 客户编辑 Album、Page 或 Item；
- 跨 Page 全选；
- 长期保存 ZIP；
- 视频转码、图片编辑或在线压缩服务；
- 修改来源允许列表、媒体类型校验或附件唯一性语义；
- 引入 `wd_qooling_app` 或具体业务来源模块作为运行时依赖；
- 通过 attachment ID 替代 Item ID 作为授权边界；
- 改变 CC-04 已冻结的单文件下载和未授权 404 语义。

## 3. 编码前门禁

### 3.1 必须满足的条件

- TDD-Q-008 已完成动态来源验证，或已形成明确的阻塞来源范围和 ATR/IHR 记录；
- TDD-Q-004 已由技术负责人和运维确定最大文件数、总大小、内存、超时和并发参数；
- TD-001 的兼容迁移策略已由技术负责人和产品确认；
- Portal 授权链、Item ID 资源边界和“不可用媒体不能下载”语义保持不变；
- CC-04 单文件预览、下载和授权回归验证通过。

### 3.2 停止条件

出现以下情况时，必须停止相关编码并回到上游文档确认：

- 必须使用 attachment ID 才能完成批量下载；
- 必须在授权前读取或 `sudo()` 附件；
- 资源限制无法保护正常业务请求；
- 动态来源验证要求引入具体业务模块依赖；
- 需要静默跳过不可用媒体或生成部分成功 ZIP；
- 需要改变 SRS/TDD 中现有业务语义。

## 4. 访问与数据安全边界

### 4.1 Portal ZIP 授权顺序

每个批量下载请求必须：

1. 使用登录用户路由，并确认当前用户属于 `base.group_portal`；
2. 根据 Item ID 查询并确认 Item 存在；
3. 确认所有 Item 属于同一 Page、同一 Album；
4. 确认 Album 属于当前用户的 Commercial Partner；
5. 确认 Album 为 `published`、未撤销且未过期；
6. 确认每个 Item 可用且具有关联附件；
7. 完成上述检查后，才允许对附件使用 `sudo()` 读取二进制。

未授权、不存在、跨客户、跨 Album、撤销、过期或不可用 Item 必须明确失败，不得泄露资源存在性，也不得静默排除后生成部分 ZIP。

### 4.2 请求和响应边界

- 批量请求只接受 Item ID；
- 前端不得提交或依赖 attachment ID；
- 全选只作用于当前 Page；
- ZIP 不写入长期业务附件或持久化文件；
- ZIP 内文件名必须清洗路径穿越、绝对路径、控制字符和不安全分隔符，并通过稳定后缀或序号保证唯一；
- `Content-Disposition` 必须使用安全的下载文件名。

## 5. 任务拆分

### CC-05-T01 Source Config 字段候选

- **输入**：TD-001、TDD §2.5、CC-01 §3.4.2；
- **实现**：基于已选 `model_id` 查询 `ir.model.fields`，仅向 UI 提供 `many2many` 且 relation 为 `ir.attachment` 的候选；服务端复用 CC-01 字段校验接口；
- **完成条件**：
  - 合法候选可在后台选择；
  - 非法字段不会出现在候选中且无法通过保存/启用复核；
  - 候选不会自动启用配置；
  - 现有文本配置可兼容迁移，或升级策略有明确记录；
  - 不新增具体业务模块依赖。

### CC-05-T02 动态来源运行时验证

- **输入**：TDD-Q-008、CC-02-T01；
- **实现**：优先使用现有 Odoo 模型；无法满足验证时，在 `wd_evidence_album/tests/` 建立仅测试环境加载的模型，不加入生产 manifest；验证 Registry、模型访问、`record[field_name]`、附件 Recordset 和权限边界；
- **完成条件**：
  - 验证模型、环境和权限明确记录；
  - 动态读取成功和失败均有可审计结果；
  - Resolver 不硬编码业务模型；
  - 失败返回明确业务错误；
  - 结果写入 CC-05 IHR/ATR。

### CC-05-T03 Portal 当前 Page 多选

- **输入**：Implementation Plan §6.3、CC-04 Viewer；
- **实现**：增加选择、取消选择、全选当前 Page、数量提示和批量下载触发；
- **完成条件**：
  - 只提交当前 Page 的 Item ID；
  - 不提交 attachment ID；
  - 不可用 Item 不可选；
  - Page 切换或筛选不会造成选择状态越权扩散；
  - 上传、删除和单文件下载不受影响；
  - 跨 Page 全选不在 V1 范围内。

### CC-05-T04 ZIP 授权和资源限制

- **输入**：TDD §6.3、§8、TDD-Q-004；
- **实现**：实现统一授权、文件数/总大小/内存/超时/并发保护和明确业务错误；资源限制优先使用 `ir.config_parameter`，默认值在模块初始化时写入，具体参数名和默认值以 TDD-Q-004 决策为准；
- **完成条件**：
  - 授权先于附件读取；
  - 请求只接受 Item ID；
  - Album、Commercial Partner、状态、撤销、有效期、Page/Item 归属和可用性全部复核；
  - 超限或包含不可用 Item 时明确失败且不生成部分 ZIP；
  - 配置来源、默认值和错误信息有文档记录。

### CC-05-T05 ZIP 生成和文件名安全

- **输入**：TDD §8.1、§8.3、TV-05；
- **实现**：请求期间内存 ZIP、文件名清洗、同名唯一化和安全响应头；
- **完成条件**：
  - ZIP 不长期保存；
  - 文件名不能造成路径穿越、绝对路径或控制字符注入；
  - ZIP 内名称稳定且唯一；
  - 下载响应使用安全 `Content-Disposition`；
  - 内存流和临时文件在成功、失败和异常路径都通过 `with` 或 `try/finally` 释放。

### CC-05-T06 回归与关闭材料

- **输入**：CC-05-T01 至 T05；
- **输出**：CC-05 IHR、ATR、HVR、FR，以及必要的 Technical Debt Register/Implementation Plan 更新；
- **完成条件**：
  - 多选、授权、限制、清洗和错误路径均有证据；
  - CC-04 单文件预览、下载和授权回归通过；
  - 用户 HVR 与 Agent 观察严格区分；
  - 未完成项保留为 Open，不以文档描述替代实现；
  - 若业务语义或技术设计变化，同步更新 SRS/TDD。

## 6. 验收证据

| 验收条件 | 必需证据 |
|---|---|
| Source Config 可选择合法附件字段 | 后台截图 + 浏览器验证 |
| 非法字段无法保存或启用 | 服务端定向测试 + 浏览器错误记录 |
| 动态来源运行时验证可审计 | ATR 日志 + IHR 记录 |
| 当前 Page 内多选媒体 Item | 浏览器验证 |
| 请求只提交 Item ID | ATR + 浏览器网络请求截图 |
| 跨客户、未发布、撤销、过期、不可用和越权 Item 被拒绝 | ATR + 浏览器错误记录 |
| 文件数、总大小、内存、超时和并发限制生效 | ATR + 浏览器验证 |
| 超限或不可用媒体不生成部分 ZIP | 浏览器截图 + 错误消息记录 |
| ZIP 不长期保存 | ATR 资源清理检查 |
| ZIP 文件名清洗且唯一 | ATR + ZIP 内容检查 |
| CC-04 单文件预览和下载回归通过 | 重跑 CC-04 ATR |
| 关闭材料完成审批 | 文档审查记录 |

## 7. 变更控制

本契约冻结后：

- 新增功能、扩大跨 Page 选择、改变授权边界或改变 ZIP 资源策略，必须先更新并重新审批 Change Contract/Coding Contract；
- 实现中发现 SRS/TDD 语义缺口时，暂停受影响任务，不通过代码或测试结果自行推断；
- TD-001、TDD-Q-008、TDD-Q-004 的关闭状态必须由对应证据和登记册更新支持；
- 本契约不授权修改真实用户凭据、生产数据或非 CC-05 范围的模块。

## 8. 审批记录

| 版本 | 日期 | 变更 | 审批人 | 审批日期 |
|---|---|---|---|---|
| v1.0.0 | 2026-09-28 | 依据已冻结的 CC-05 Change Contract 起草并冻结 Coding Contract。 | 项目负责人 | 2026-09-28 |
