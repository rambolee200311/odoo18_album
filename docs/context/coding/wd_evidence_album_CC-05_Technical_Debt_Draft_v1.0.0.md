# WMS Evidence Album — CC-05 Technical Debt Remediation
# Draft Change Contract

## 0. 文档治理

| 项目 | 内容 |
|---|---|
| 模块 | `wd_evidence_album` |
| CC | CC-05 |
| 文档版本 | v1.0.1 |
| 文档状态 | Frozen Change Contract |
| 起草日期 | 2026-09-28 |
| 上游技术债 | [Technical Debt Register](./wd_evidence_album_Technical_Debt_Register_v1.0.0.md) |
| 前置基线 | CC-04 已冻结并推送；Portal 和后台 Album/Page 基线已建立 |
| 关联实施计划 | [Implementation Plan](./wd_evidence_album_Implementation_Plan_v1.0.0.md) §6 |

本文档曾是 CC-05 的 **Draft Change Contract（变更契约草案）**，现已由项目负责人批准冻结为 **Frozen Change Contract（冻结变更契约）**。本文档定义 CC-05 的范围、任务和门禁，不等同于 CC-05 的 Coding Contract；对应 Coding Contract 见 [CC-05 Coding Contract](./wd_evidence_album_CC-05_Coding_Contract_v1.0.0.md)。

本草案将下一阶段定义为“技术债清理 + 批量下载”。它不表示任何技术债已经关闭，也不允许在审批冻结前进入实现。

## 1. 背景和问题

CC-04 冻结后，仍有三个待处理项：一个技术债和两个 TDD 待确认项。三者分别影响配置体验、来源采集验证和批量交付：

1. **TD-001：Source Config 字段选择器**
   - `field_name` 仍依赖手工文本输入；
   - 配置错误风险较高；
   - 目标是基于已选模型提供合法附件字段候选，同时保留显式保存和启用约束。

2. **TDD-Q-008：动态来源运行时验证（TDD 待确认项，不是技术债）**
   - 需要形成可审计证据，证明 Odoo Registry 中配置模型和 `record[field_name]` 动态读取成立；
   - 未形成证据时，来源 Resolver、来源 Page/Item 创建和来源附件选择不得宣称完整验收。

3. **TDD-Q-004：ZIP 资源边界（TDD 待确认项，不是技术债）**
   - CC-05 批量下载仍缺少最大文件数、总大小、内存、超时和并发配置；
   - 没有资源边界前不得实现无上限 ZIP 生成。

优先级如下：

- TDD-Q-008：High，阻塞来源采集完整验收；
- TDD-Q-004：High，阻塞 ZIP 实现；
- TD-001：Medium，不阻塞核心功能，但影响 Source Config 配置体验。

## 2. 目标

CC-05 目标是：

- 关闭 TD-001；
- 解决 TDD-Q-008，并将动态来源验证结果写入 ATR/IHR；
- 在不改变 Portal 授权模型的前提下实现多选 ZIP 下载；
- 在 ZIP 实现前冻结并落实 TDD-Q-004 的资源配置；
- 形成 CC-05 IHR、ATR、HVR 和 FR 关闭材料。

## 3. 范围

### 3.1 In Scope

- Source Config `field_name` 候选字段发现和选择的 UI 入口；服务端字段校验接口复用 CC-01 §3.4.2，不在 CC-05 中重新实现；
- Registry/动态字段读取的测试模型或真实上游模块验证；
- Portal 媒体多选、取消选择和选择数量提示；
- 只接受 Item ID 的批量下载请求；
- Album/客户/状态/有效期/Page/Item/媒体可用性统一授权；
- ZIP 文件数、总大小、内存、超时和并发限制；
- ZIP 文件名清洗、唯一化和路径穿越防护；
- CC-04 单文件预览、下载、Portal 授权、Item ID 媒体边界和 `sudo()` 边界的回归验证；
- 关闭材料和回归证据。

### 3.2 Out of Scope

- 匿名 Token 下载；
- Portal 客户编辑 Album、Page 或 Item；
- 重新定义来源允许列表、媒体类型校验或附件唯一性；
- 长期保存 ZIP 文件；
- 视频转码、图片编辑和在线压缩服务；
- 引入 `wd_qooling_app` 作为运行时依赖；
- 修改 CC-04 已冻结的单文件媒体授权语义。

## 4. 变更边界

### 4.1 允许修改

- Source Config 后台视图和字段候选入口；
- Source Config/Resolver 的验证辅助代码和测试模型；
- Portal OWL 选择栏和批量下载入口；
- Portal ZIP Controller、资源限制配置和文件名清洗；
- 相关 IHR/ATR/HVR/FR 文档。

### 4.2 禁止修改

- 不得通过附件 ID 绕过 Item 授权；
- 不得在附件读取前使用 `sudo()`；
- 不得把 ZIP 请求授权交给前端；
- 不得自动启用候选 Source Config 字段；
- 不得因来源验证方便而把具体业务模块加入 manifest 依赖；
- 不得删除或改变 CC-04 的单文件下载和未授权 404 语义；
- 不得把超限媒体静默跳过后生成“部分成功”的 ZIP。

## 5. 任务拆分

### CC-05-T01 Source Config 字段候选

- **输入**：TD-001、TDD §2.5、CC-01-T05；
- **工作范围**：基于 `model_id` 查询 `ir.model.fields`，只提供 `many2many` 且 relation 为 `ir.attachment` 的 UI 候选；复用 CC-01 §3.4.2 的服务端字段校验接口，不建立第二套校验；
- **完成条件**：
  - 合法候选可在后台选择；
  - 非法字段不会出现在候选中；
  - 保存和启用仍由服务端复核；
  - 不因出现候选而自动启用配置；
  - 现有文本配置可兼容迁移或明确给出升级策略。

### CC-05-T02 动态来源运行时验证

- **输入**：TDD-Q-008、CC-02-T01；
- **工作范围**：优先复用 Odoo 现有模型（如 `res.partner`）；现有模型无法满足验证需求时，在 `wd_evidence_album/tests/` 下建立仅测试环境加载的专用测试模型，不把测试模型加入生产 manifest 依赖；验证 Registry、模型访问、`record[field_name]`、附件 Recordset 和权限边界；
- **完成条件**：
  - 验证环境和模型明确记录；
  - 动态字段读取成功或失败均有可审计结果；
  - Resolver 不硬编码业务模型；
  - 失败时返回明确业务错误；
  - 结果写入 CC-05 IHR/ATR；
  - 来源采集 HVR 不得超出实际验证范围。

### CC-05-T03 Portal 多选交互

- **输入**：Implementation Plan §6.3、CC-04 Viewer；
- **工作范围**：增加媒体选择、取消选择、全选当前 Page、数量提示和批量下载触发；跨 Page 全选不属于 CC-05 V1，用户需要逐 Page 操作；
- **完成条件**：
  - 前端只提交 Item ID；
  - 不向后端提交 attachment ID；
  - 不可用 Item 不可选；
  - 选择状态在 Page 切换和筛选时不会越权扩散；
  - 上传、删除和单文件下载行为不受影响。

### CC-05-T04 ZIP 授权和资源边界

- **输入**：TDD §6.3、§8、TDD-Q-004；
- **工作范围**：实现统一授权、文件数量限制、总大小限制、内存/超时/并发保护和明确业务错误；
- **完成条件**：
  - 授权先于附件读取；
  - 请求只接收 Item ID；
  - Album、Commercial Partner、published、撤销、有效期、Page/Item 归属和可用性全部复核；
  - 超限请求不生成 ZIP；
  - 请求包含不可用 Item 时明确失败，不静默跳过；
  - ZIP 资源限制优先使用 Odoo `ir.config_parameter`；管理员可在后台修改，默认值在模块初始化时写入；具体参数名和默认值由 TDD-Q-004 决策确定；
  - 配置来源、默认值和错误信息有文档记录。

### CC-05-T05 ZIP 生成和文件名安全

- **输入**：TV-05、TDD §8.1、§8.3；
- **工作范围**：请求期间内存 ZIP、文件名清洗、同名唯一化和响应头；
- **完成条件**：
  - 不长期保存 ZIP；
  - 文件名不允许路径穿越、控制字符或绝对路径；
  - ZIP 内文件名稳定且唯一；
  - 下载响应使用安全的 `Content-Disposition`；
  - ZIP 生成过程中的内存流和临时文件在异常路径中释放，使用 `try/finally` 或 `with` 保证释放，不依赖垃圾回收。

### CC-05-T06 关闭材料

- **输出**：CC-05 IHR、ATR、HVR、FR；
- **完成条件**：
  - TD-001、TDD-Q-008、TDD-Q-004 的状态有明确结论；
  - 多选、授权、限制、清洗和错误路径均有证据；
  - 用户 HVR 与 Agent 观察严格区分；
  - 未完成项保留为 Open，不以文档描述替代实现。

## 6. 验收条件

| 验收条件 | 必需证据 |
|---|---|
| Source Config 可基于模型选择合法附件字段 | 后台截图 + 浏览器验证 |
| 非法字段无法保存或启用 | 服务端定向测试 + 浏览器错误记录 |
| 动态来源运行时验证有可审计证据 | ATR 日志 + IHR 记录 |
| Portal 用户可在当前 Page 内多选媒体 Item | 浏览器验证 |
| ZIP 请求只接受 Item ID | ATR + 浏览器网络请求截图 |
| 跨客户、未发布、撤销、过期、不可用和越权 Item 均被拒绝 | ATR + 浏览器错误记录 |
| 文件数、总大小、内存、超时和并发限制生效 | ATR + 浏览器验证 |
| 超限和不可用媒体返回明确错误，不生成部分 ZIP | 浏览器截图 + 错误消息记录 |
| ZIP 不长期保存 | ATR 资源清理检查 |
| ZIP 文件名经过清洗并在压缩包内唯一 | ATR + ZIP 内容检查 |
| CC-04 单文件预览和下载回归通过 | 重跑 CC-04 ATR |
| IHR、ATR、HVR、FR 形成并经项目审批 | 文档审查记录 |

## 7. 门禁和停止条件

在以下条件满足前，CC-05 不得进入 ZIP 编码：

- TDD-Q-004 已形成最大文件数、总大小、内存、超时和并发决策；
- TDD-Q-008 已完成动态来源验证，或已明确阻塞来源范围；
- Portal 授权链和 Item 资源边界没有被削弱；
- TD-001 的兼容迁移策略已确定；
- 变更范围已由项目负责人批准冻结。

门禁决策责任如下：

| 门禁 | 决策方 |
|---|---|
| TDD-Q-004 ZIP 资源配置 | 技术负责人 + 运维 |
| TDD-Q-008 动态来源验证 | 技术负责人 |
| Portal 授权链和 Item 资源边界 | 技术负责人 |
| TD-001 兼容迁移策略 | 技术负责人 + 产品 |
| CC-05 变更范围冻结 | 项目负责人 |

出现以下情况必须停止相关实现并回到上游文档：

- 需要通过 attachment ID 才能完成 ZIP 下载；
- 需要绕过 Portal 授权才能生成 ZIP；
- 资源限制无法满足正常业务下载；
- 动态来源验证要求引入具体业务模块依赖；
- 需要改变 SRS 中“不可用媒体不能下载”的语义。

## 8. 预期交付物

- `wd_evidence_album_CC-05_Coding_Contract_v1.0.0.md`（本文档冻结后起草）
- `wd_evidence_album_CC-05_IHR_v1.0.0.md`
- `wd_evidence_album_CC-05_ATR_v1.0.0.md`
- `wd_evidence_album_CC-05_HVR_v1.0.0.md`
- `wd_evidence_album_CC-05_FR_v1.0.0.md`
- 更新后的 [Technical Debt Register](./wd_evidence_album_Technical_Debt_Register_v1.0.0.md)
- 更新后的 [Implementation Plan](./wd_evidence_album_Implementation_Plan_v1.0.0.md)
- 更新后的 SRS/TDD（仅当 CC-05 决策改变业务语义或技术设计时）

## 9. 审批状态

| 项目 | 状态 |
|---|---|
| 业务范围 | Frozen |
| 技术范围 | Frozen |
| TDD-Q-004 | Open，阻塞 ZIP 实现 |
| TDD-Q-008 | Open，阻塞来源采集完整验收 |
| TD-001 | Open |
| CC-05 冻结 | 已冻结；本文档、CC-05 Coding Contract 和实施范围均已冻结 |

## 10. 变更记录

| 版本 | 日期 | 变更 | 审批人 | 审批日期 |
|---|---|---|---|---|
| v1.0.0 | 2026-09-28 | 起草 CC-05 Technical Debt Remediation Draft | 待审批 | 待审批 |
| v1.0.1 | 2026-09-28 | 按评审意见修订文档性质、待处理项分类、任务边界、决策责任、证据类型和冻结定义。 | 待审批 | 待审批 |
| v1.0.2 | 2026-09-28 | 项目负责人批准冻结 Change Contract，并关联 CC-05 Coding Contract。 | 项目负责人 | 2026-09-28 |
