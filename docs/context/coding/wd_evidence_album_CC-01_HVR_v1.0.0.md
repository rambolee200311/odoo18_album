# WMS Evidence Album — CC-01 HVR
# Human Verification Record

## 0. 文档治理

| 项目 | 内容 |
|---|---|
| Intent ID | `wd-evidence-album-cc-01` |
| IHR | [CC-01 IHR](./wd_evidence_album_CC-01_IHR_v1.0.0.md) |
| ATR | [CC-01 ATR](./wd_evidence_album_CC-01_ATR_v1.0.0.md) |
| CC | [CC-01 Coding Contract](./wd_evidence_album_CC-01_Coding_Contract_v1.0.0.md) |
| 模块 | `wd_evidence_album` |
| 环境 | Odoo 18 Community Edition；数据库 `odoo18ce` |
| 当前代码基线 | `000424d` + 未提交 CC-01 工作树 |
| Human Verifier | 当前会话用户提供验证结果；姓名/账号未登记 |
| 当前状态 | Partial；6 项场景均已通过（5 项用户报告，1 项用户确认并有 Agent/Tool-assisted 浏览器证据）；正式人类 HVR 身份尚未登记 |

本记录不把代码检查或自动化命令结果等同于人工验证。根据 HVR 标准，在没有真实人类执行和观察前，不记录 PASS。

## 1. Human Verification Status

| 指标 | 值 |
|---|---:|
| Required scenarios | 6 |
| PASS | 6（5 项用户报告；附件生命周期场景为用户确认并有 Agent/Tool-assisted 浏览器证据） |
| FAIL | 0 |
| BLOCKED | 0 |
| NOT RUN | 0 |
| Agent-assisted observations | 4 个场景已观察，1 个场景部分观察；另有 1 个生命周期场景已完整观察 |
| Evidence baseline status | Partial；HVR 身份信息待补登记 |

## 2. Verification Coverage Matrix

| 验证要求 | Scenario | 上游依据 | 当前证据 | 结果 |
|---|---|---|---|---|
| 模块可安装并进入后台菜单 | HVR-SCN-001 | CC-01 AC-01、AC-09 | HVR-EVD-005 | PASS（用户报告） |
| Album 表单字段、只读状态和动作按钮 | HVR-SCN-002 | CC-01 §5.1、§5.7 | HVR-EVD-006 | PASS（用户报告） |
| Page/Item 排序及跨 Album 移动拒绝 | HVR-SCN-003 | CC-01 AC-04、AC-06 | HVR-EVD-007 | PASS（用户报告） |
| 业务用户、审核人、管理员后台边界 | HVR-SCN-004 | SRS §9、CC-01 §4 | HVR-EVD-008 | PASS（用户报告） |
| Source Config 配置校验和显式启用 | HVR-SCN-005 | CC-01 AC-08、§5.5 | HVR-EVD-009 | PASS（用户报告）；字段非下拉选择为技术债 |
| 附件删除后 Item 保留且显示不可用 | HVR-SCN-006 | CC-01 AC-03、TDD §2.4 | HVR-EVD-010 | PASS（用户确认；有 Agent/Tool-assisted 浏览器证据） |

## 3. Verification Scenarios

### HVR-SCN-001 — 安装和菜单

- **Purpose**：确认模块可从 Odoo 后台安装并进入 Evidence Album 菜单。
- **Preconditions**：使用具有模块安装权限的后台账号；模块已位于 `mymodules`。
- **Steps**：更新应用列表；安装/升级模块；打开 Evidence Album 菜单和 Albums 菜单。
- **Expected**：安装完成无错误；菜单可见；列表和表单动作可打开。
- **Evidence Required**：安装日志截图、菜单截图、手工步骤记录。
- **Result**：正式人类 HVR NOT RUN；Agent/Tool 已观察菜单、列表和表单入口可用。

### HVR-SCN-002 — Album 表单

- **Purpose**：确认字段分组、只读字段和 CC-03 动作入口符合契约。
- **Preconditions**：进入 Albums；具有创建 Album 权限。
- **Steps**：创建 Album；检查基础信息、状态信息、Token 和 Pages 区域；尝试直接编辑 `state`、Token 和审核字段。
- **Expected**：契约规定的只读字段不可普通编辑；动作按钮按状态显示；按钮隐藏不被视为权限证明。
- **Evidence Required**：表单截图、操作记录。
- **Result**：用户报告 PASS；Agent/Tool 已创建 Album，保存后 reload 仍显示名称、客户和 Draft 状态；截图见 HVR-EVD-002。

### HVR-SCN-003 — 排序和跨 Album 边界

- **Purpose**：确认 Page/Item 顺序编辑位于所属边界内，UI 不提供跨 Album 移动。
- **Preconditions**：至少两个 Album、两个 Page 和多个 Item。
- **Steps**：调整 Page 和 Item 的 `sequence`；检查内嵌列表；尝试通过表单移动 Page 到另一个 Album。
- **Expected**：同一 Album/Page 内排序可用；不存在跨 Album 移动入口；跨 Album 写入被拒绝。
- **Evidence Required**：排序前后截图、错误提示截图。
- **Result**：用户报告 PASS；Agent/Tool 已通过 UI 创建 Page 并保存，用户确认排序及跨 Album 移动拒绝。

### HVR-SCN-004 — 后台角色权限

- **Purpose**：确认业务用户、审核人和管理员的可见/可编辑范围。
- **Preconditions**：准备三个可识别的测试账号，并准备不同 `create_uid` 的 Album。
- **Steps**：分别登录三个账号；访问自己/他人 Album；尝试创建、编辑、删除 Album/Page/Item 和 Source Config。
- **Expected**：业务用户受自己 Album 归属边界限制；审核人可访问审核范围；管理员可管理全部；Portal 用户不因后台组获得权限。
- **Evidence Required**：每个角色的账号标识、操作步骤、页面/错误截图。
- **Result**：用户报告 PASS；Agent/Tool 观察到业务用户可以创建并重新打开自己的 Album，访问经理创建的 Album 时收到 Access Error；审核人可以打开经理创建的 Album。用户确认管理员边界通过。

### HVR-SCN-005 — Source Config

- **Purpose**：确认候选配置不会自动暴露，且无效字段配置会显示明确错误。
- **Preconditions**：管理员账号；一个已加载且具有 Many2many→`ir.attachment` 字段的模型。
- **Steps**：创建有效配置；尝试填写不存在字段、非 Many2many 字段和无权限映射字段；停用配置。
- **Expected**：有效配置可保存；无效配置被明确拒绝；停用不删除已有 Item；候选字段不会自动启用。
- **Evidence Required**：配置表单截图、错误提示截图、停用状态截图。
- **Result**：用户报告 PASS；用户确认配置校验和显式启用通过。Source Config 的 `field_name` 当前为文本输入而非候选字段下拉，登记为技术债；真实 Registry 来源验证仍受 TDD-Q-008 约束。

### HVR-SCN-006 — 附件删除生命周期

- **Purpose**：确认删除原始附件不会删除 Item，Item 显示不可用。
- **Preconditions**：创建包含附件引用的 Item；具有附件删除权限。
- **Steps**：记录 Item 和附件；删除附件；重新打开 Page/Item。
- **Expected**：Item 仍存在；附件引用为空；`availability_state` 为 unavailable；Item 删除不删除其他附件。
- **Evidence Required**：删除前后页面截图、附件和 Item 标识、日志。
- **Result**：用户确认 PASS；已完成 Agent/Tool-assisted 浏览器观察：通过后台附件列表打开并删除受控附件 `CC01 browser delete demo.txt`，返回 Item 列表后确认 Item 仍存在、Attachment 为空、`Availability State` 为 `Unavailable`。

## 4. Verification Run History

### Agent-assisted pre-verification（非正式人类 HVR）

本次浏览器操作由 Playwright 执行，验证主体不是人类，因此以下记录只作为预验证观察，不构成正式 HVR PASS。

| 字段 | 内容 |
|---|---|
| Run ID | HVR-AGENT-RUN-001 |
| 时间 | 2026-09-24 |
| Human Verifier | None；Agent/Tool execution |
| Environment | `http://127.0.0.1:8091`，Odoo 18，数据库 `odoo18ce` |
| Browser | Integrated Playwright browser |
| Code Baseline | `000424d` + 未提交 CC-01 工作树 |
| Test users | 临时隔离的 CC-01 manager、reviewer、user 账号 |
| Scenarios | HVR-SCN-001 至 HVR-SCN-004（部分） |
| Execution Assistance | Playwright |
| Result Summary | PARTIAL |
| Evidence | HVR-EVD-001 至 HVR-EVD-004 |
| Follow-up | 由人类验证主体重新执行并形成正式 HVR Run |

### Agent-assisted browser lifecycle run

| 字段 | 内容 |
|---|---|
| Run ID | HVR-AGENT-RUN-002 |
| 时间 | 2026-09-24 |
| Human Verifier | None；Agent/Tool execution |
| Environment | `http://127.0.0.1:8091`，Odoo 18，数据库 `odoo18ce` |
| Browser | Integrated Playwright browser |
| Code Baseline | `000424d` + 未提交 CC-01 工作树 |
| Controlled fixture | Album 14 / Page 13 / Item 14 / Attachment 1404 |
| Scenario | HVR-SCN-006 |
| Execution | 在后台附件列表打开并删除受控附件，随后回到 Item 列表并观察状态 |
| Result Summary | PASS（Agent/Tool-assisted observation；不构成正式人类 HVR PASS） |
| Evidence | HVR-EVD-010 |
| Observation | Item 保留；Attachment 为空；Availability State 为 `Unavailable` |

### Agent-assisted observations

| Evidence ID | 实际观察 |
|---|---|
| HVR-EVD-001 | Manager 登录后可看到 Evidence Album、Albums 菜单和 Album 列表；模块页面打开成功。 |
| HVR-EVD-002 | Manager 通过 UI 创建 `CC-01 E2E Album 20260924`，选择客户并保存；reload 后名称、客户和 Draft 状态仍存在。Album 表单截图已在本次浏览器会话中生成。 |
| HVR-EVD-003 | 通过 UI 添加 `First Page` 并保存；页面列表中可见。Page sequence 调整和跨 Album UI 拒绝尚未执行。 |
| HVR-EVD-004 | 业务用户可创建并 reload 自己的 `CC-01 User Album 20260924`；访问经理 Album 时收到 Odoo Access Error；审核人可以打开经理 Album。 |
| HVR-EVD-005 | 用户确认模块可安装并进入后台菜单。 |
| HVR-EVD-006 | 用户确认 Album 表单字段、只读状态和动作按钮通过。 |
| HVR-EVD-007 | 用户确认 Page/Item 排序及跨 Album 移动拒绝通过。 |
| HVR-EVD-008 | 用户确认业务用户、审核人、管理员后台边界通过。 |
| HVR-EVD-009 | 用户确认 Source Config 配置校验和显式启用通过；`field_name` 非下拉选择登记为技术债。 |
| HVR-EVD-010 | 受控浏览器演示：删除 `CC01 browser delete demo.txt` 后，Item 列表仍保留对应 Item，附件列为空，`Availability State` 显示 `Unavailable`。 |

正式 HVR Run 仍为空。不得将 `HVR-AGENT-RUN-001` 或 `HVR-AGENT-RUN-002` 视为人类验收记录。

| Run ID | 时间 | Human Verifier | Scenarios | Result | Evidence |
|---|---|---|---|---|---|
| — | — | — | — | NOT RUN | — |

## 5. Handoff Summary

HVR 已准备好六个可执行场景，并完成两次非正式 Agent/Tool 预验证；用户已报告前五项通过，附件生命周期场景已由 Agent/Tool 完成浏览器观察，但尚未形成带身份登记的正式人工 HVR Run。需要可识别的人类验证主体按场景执行，并追加：

- `Human Verifier`；
- 实际执行时间和代码基线；
- 实际观察；
- 截图/日志/手工步骤证据；
- PASS、FAIL 或 BLOCKED 结果。
