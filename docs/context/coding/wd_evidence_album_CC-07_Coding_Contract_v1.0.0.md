# WMS Evidence Album — Coding Contract CC-07
# 技术债清理与 Portal 批量 ZIP 下载

## 0. 文档信息

| 项目 | 内容 |
|---|---|
| 模块 | `wd_evidence_album` |
| CC | CC-07 — 技术债清理与 Portal 批量 ZIP 下载 |
| CC 版本 | v1.0.0 |
| 状态 | Frozen Coding Contract |
| Odoo | 18.0 Community Edition |
| 代码目录 | `/Users/lijianqiang/Documents/odoo18_album/mymodules/wd_evidence_album` |
| 上游业务基线 | SRS v1.0.0（Frozen） |
| 上游技术基线 | TDD v1.0.0（Frozen Implementation Baseline） |
| 实施规划基线 | Implementation Plan v1.0.0（当前仍标记为 CC-05） |
| 前置编码基线 | CC-04 已冻结；Portal 单文件查看、下载和授权边界已存在 |
| 关联技术债 | TD-001 Open；TDD-Q-008 Open；TDD-Q-004 Open |

### 0.1 编号迁移声明

本契约承接 Implementation Plan §6 和原 [CC-05 Coding Contract](./wd_evidence_album_CC-05_Coding_Contract_v1.0.0.md) 的同一功能范围：

| 原编号 | 新编号 | 范围 |
|---|---|---|
| CC-05 | CC-07 | Source Config 字段候选、动态来源运行时验证、Portal 当前 Page 多选、批量 ZIP 下载、资源边界和关闭材料 |

Implementation Plan v1.0.0 当前仍使用 CC-05 编号。该计划必须在 CC-07 进入编码前修订，至少同步实施对象、实施顺序、跨 CC 依赖、§6 标题和关闭材料中的 CC 编号。本契约不将该上游修订默认为已完成。

## 1. 契约目标

CC-07 实现以下目标：

1. 为 Source Config 提供合法附件字段的后台候选选择入口，并保留服务端复核和现有文本配置兼容性；
2. 形成动态来源 Registry、模型访问、`record[field_name]` 和附件 Recordset 的可审计运行时验证；
3. 在当前 Portal Page 内提供 Item 多选和批量 ZIP 下载；
4. 在授权先于附件读取的前提下，落实 ZIP 文件数、总大小、内存、超时和并发限制；
5. 形成 ZIP 文件名清洗、唯一化、错误处理和资源释放的完整边界；
6. 回归 CC-04 单文件预览、下载、Item ID 媒体边界和 Portal 授权。

## 2. 范围与排除

### 2.1 覆盖范围

- Source Config 合法附件字段候选；
- 动态来源 Registry 和 `record[field_name]` 运行时验证；
- 当前 Page 内媒体 Item 多选、全选、取消选择和批量下载触发；
- Portal 批量 ZIP 授权、资源限制、文件名清洗和临时响应；
- CC-04 单文件预览、下载、媒体 Controller 和 Portal 授权回归；
- CC-07 IHR、ATR、HVR、FR 及必要的上游文档更新。

### 2.2 明确不覆盖

CC-07 不实现或不改变：

- 匿名 Token 下载；
- Portal 客户编辑 Album、Page 或 Item；
- 跨 Page 全选；
- 长期保存 ZIP；
- 视频转码、图片编辑或在线压缩服务；
- 来源允许列表、媒体类型校验或附件唯一性语义；
- `wd_qooling_app` 或任何具体业务来源模块的运行时依赖；
- 以 attachment ID 替代 Item ID 作为授权边界；
- CC-04 已冻结的单文件下载、媒体路由和未授权 404 语义；
- CC-06 发布前 Portal 预览。

## 3. 编码前门禁

### 3.1 必须满足

- Implementation Plan 已将原 CC-05 正式迁移为 CC-07，并完成交叉引用；
- TDD-Q-008 已完成动态来源验证，或已形成明确的阻塞来源范围和 ATR/IHR 记录；
- TDD-Q-004 已由技术负责人和运维确定最大文件数、总大小、内存、超时和并发参数；
- TD-001 的兼容迁移策略已由技术负责人和产品确认；
- CC-04 Portal 授权链、Item ID 资源边界和“不可用媒体不能下载”语义保持不变；
- CC-04 单文件预览、下载和授权回归验证通过。

### 3.2 停止条件

出现以下情况时，必须停止受影响任务并回到上游文档确认：

- 必须使用 attachment ID 才能完成批量下载；
- 必须在授权前读取或 `sudo()` 附件；
- 资源限制无法保护正常业务请求；
- 动态来源验证要求引入具体业务模块依赖；
- 需要静默跳过不可用媒体或生成部分成功 ZIP；
- 需要改变 SRS/TDD 中现有业务语义；
- 需要修改 CC-04 或 CC-06 的冻结契约。

## 4. 访问与数据安全契约

### 4.1 Portal ZIP 授权顺序

每个批量下载请求必须按以下顺序完成检查：

1. 确认登录用户属于 `base.group_portal`；
2. 根据 Item ID 查询并确认 Item 存在；
3. 确认所有 Item 属于同一 Page、同一 Album；
4. 确认 Album 属于当前用户的 Commercial Partner；
5. 确认 Album 为 `published`、未撤销且未过期；
6. 确认每个 Item 可用且具有关联附件；
7. 完成上述检查后，才允许对附件使用 `sudo()` 读取二进制。

未授权、不存在、跨客户、跨 Album、撤销、过期或不可用 Item 必须明确失败，不得泄露资源存在性，也不得静默排除后生成部分 ZIP。

### 4.2 请求与响应边界

- 批量请求只接受 Item ID；
- 前端不得提交或依赖 attachment ID；
- 全选只作用于当前 Page；
- ZIP 不写入长期业务附件或持久化文件；
- ZIP 内文件名必须清洗路径穿越、绝对路径、控制字符和不安全分隔符，并保证唯一；
- `Content-Disposition` 必须使用安全的下载文件名。

## 5. 任务契约

### CC-07-T01 Source Config 字段候选

- **输入**：TD-001、TDD §2.5、CC-01 §3.4.2；
- **范围**：基于已选 `model_id` 查询 `ir.model.fields`，仅提供 `many2many` 且 relation 为 `ir.attachment` 的候选；复用 CC-01 字段校验接口；
- **完成条件**：
  - 合法候选可在后台选择；
  - 非法字段不会出现在候选中且无法通过保存/启用复核；
  - 候选不会自动启用配置；
  - 现有文本配置可兼容迁移，或升级策略有明确记录；
  - 不新增具体业务模块依赖。

### CC-07-T02 动态来源运行时验证

- **输入**：TDD-Q-008、CC-02-T01；
- **范围**：优先使用现有 Odoo 模型；无法满足验证时，可在测试环境建立模型，但不得加入生产 manifest；验证 Registry、模型访问、`record[field_name]`、附件 Recordset 和权限边界；
- **完成条件**：
  - 验证模型、环境和权限明确记录；
  - 动态读取成功和失败均有可审计结果；
  - Resolver 不硬编码业务模型；
  - 失败返回明确业务错误；
  - 结果写入 CC-07 IHR/ATR。

### CC-07-T03 Portal 当前 Page 多选

- **输入**：原 Implementation Plan §6.3、CC-04 Viewer；
- **范围**：增加选择、取消选择、全选当前 Page、数量提示和批量下载触发；
- **完成条件**：
  - 只提交当前 Page 的 Item ID；
  - 不提交 attachment ID；
  - 不可用 Item 不可选；
  - Page 切换或筛选不会造成选择状态越权扩散；
  - 上传、删除和单文件下载不受影响；
  - 跨 Page 全选不在范围内。

### CC-07-T04 ZIP 授权和资源限制

- **输入**：TDD §6.3、§8、TDD-Q-004；
- **范围**：实现统一授权、文件数/总大小/内存/超时/并发保护和明确业务错误；资源限制优先使用 `ir.config_parameter`；
- **完成条件**：
  - 授权先于附件读取；
  - 请求只接受 Item ID；
  - Album、Commercial Partner、状态、撤销、有效期、Page/Item 归属和可用性全部复核；
  - 超限或包含不可用 Item 时明确失败且不生成部分 ZIP；
  - 配置来源、默认值和错误信息有文档记录。

### CC-07-T05 ZIP 生成和文件名安全

- **输入**：TDD §8.1、§8.3、TV-05；
- **范围**：请求期间内存 ZIP、文件名清洗、同名唯一化和安全响应头；
- **完成条件**：
  - ZIP 不长期保存；
  - 文件名不能造成路径穿越、绝对路径或控制字符注入；
  - ZIP 内名称稳定且唯一；
  - 下载响应使用安全 `Content-Disposition`；
  - 内存流和临时文件在成功、失败和异常路径都被释放。

### CC-07-T06 回归与关闭材料

- **输入**：CC-07-T01 至 T05；
- **输出**：CC-07 IHR、ATR、HVR、FR，以及必要的 Technical Debt Register/Implementation Plan 更新；
- **完成条件**：
  - 多选、授权、限制、清洗和错误路径均有证据；
  - CC-04 单文件预览、下载和授权回归通过；
  - 用户 HVR 与 Agent 观察严格区分；
  - 未完成项保留为 Open，不以文档描述替代实现；
  - 若业务语义或技术设计变化，同步更新 SRS/TDD。

## 6. 验收条件与证据

| 编号 | 验收条件 | 必需证据 |
|---|---|---|
| AC-01 | Source Config 可选择合法附件字段 | 后台截图 + 浏览器验证 |
| AC-02 | 非法字段无法保存或启用 | 服务端定向验证 + 浏览器错误记录 |
| AC-03 | 动态来源运行时验证可审计 | ATR 日志 + IHR 记录 |
| AC-04 | 客户可以在当前 Page 内多选媒体 Item | 浏览器 HVR |
| AC-05 | ZIP 请求只接收和授权 Item ID | ATR + 浏览器网络请求证据 |
| AC-06 | 跨客户、未发布、撤销、过期、不可用和越权 Item 被拒绝 | ATR + 浏览器错误记录 |
| AC-07 | 文件数、总大小、内存、超时和并发限制生效 | ATR + 浏览器验证 |
| AC-08 | 超限或不可用媒体不生成部分 ZIP | 浏览器错误记录 + 资源检查 |
| AC-09 | ZIP 不长期保存 | ATR 资源清理检查 |
| AC-10 | ZIP 文件名安全清洗且唯一 | ATR + ZIP 内容检查 |
| AC-11 | CC-04 单文件预览和下载回归通过 | 重跑 CC-04 ATR/HVR |
| AC-12 | CC-07 关闭材料完成并获审批 | IHR/ATR/HVR/FR 审查记录 |

## 7. 追溯矩阵

| CC-07 契约范围 | 上游依据 | 迁移说明 |
|---|---|---|
| Source Config 字段候选 | TDD §2.5；原 Implementation Plan §6.3；TD-001 | 原 CC-05-T01 改号为 CC-07-T01 |
| 动态来源运行时验证 | TDD-Q-008；CC-02-T01 | 原 CC-05-T02 改号为 CC-07-T02 |
| 当前 Page 多选 | TDD §9.2；TDD §9；CC-04 Viewer | 原 CC-05-T03 改号为 CC-07-T03 |
| ZIP 授权与限制 | SRS §8.8、§11、§14.2；TDD §6.3、§8；TDD-Q-004 | 原 CC-05-T04 改号为 CC-07-T04 |
| ZIP 生成与文件名安全 | TDD §8.1、§8.3；TV-05 | 原 CC-05-T05 改号为 CC-07-T05 |
| 关闭材料 | 原 Implementation Plan §8；原 CC-05-T06 | 原 CC-05-T06 改号为 CC-07-T06 |

矩阵中“原 Implementation Plan”表示当前冻结计划的历史编号。Implementation Plan 修订完成后，必须将这些引用回填为 CC-07 的正式章节。

## 8. 未解决项和升级规则

1. **Implementation Plan 编号迁移待补充**：当前计划仍写 CC-05，必须在 CC-07 编码前修订；否则本契约只能保持 Draft。
2. **TDD-Q-004 待确认**：必须形成正式资源配置决策；代码默认值不能替代决策。
3. **TDD-Q-008 待确认**：必须有动态 Registry 和 `record[field_name]` 的成功/失败验证证据。
4. **TD-001 待确认**：必须有兼容迁移策略及独立关闭证据。
5. 如果迁移过程中改变 SRS/TDD 业务语义，必须先更新上游文档，再重新评审 CC-07。
6. CC-07 不授权修改 CC-04、CC-06 或引入 CC-08 及后续范围。

## 9. 关闭材料契约

CC-07 关闭前必须形成：

- CC-07 IHR：接口、数据结构、授权边界、迁移偏差和遗留项；
- CC-07 ATR：自动化验证、模块升级、资源边界和 CC-04 回归；
- CC-07 HVR：Portal 用户人工验证，逐项区分 `user-confirmed`、`agent-observed` 和 `automated`；
- CC-07 FR：功能关闭声明、审批记录和剩余技术债；
- Implementation Plan 修订记录及追溯矩阵更新。

## 10. 审批记录

| 版本 | 日期 | 变更 | 审批人 | 审批日期 |
|---|---|---|---|---|
| v1.0.0 | 2026-09-29 | 依据 Implementation Plan 原 CC-05 范围和既有 CC-05 契约起草，完成 CC-05 → CC-07 编号迁移并冻结。 | 项目负责人 | 2026-09-29 |
