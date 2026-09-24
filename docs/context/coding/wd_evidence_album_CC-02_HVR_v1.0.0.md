# WMS Evidence Album — CC-02 HVR
# Human Verification Record

## 0. 文档治理

| 项目 | 内容 |
|---|---|
| Intent ID | `wd-evidence-album-cc-02` |
| CC | [CC-02 Coding Contract](./wd_evidence_album_CC-02_Coding_Contract_v1.0.0.md) |
| IHR | [CC-02 IHR](./wd_evidence_album_CC-02_IHR_v1.0.0.md) |
| ATR | [CC-02 ATR](./wd_evidence_album_CC-02_ATR_v1.0.0.md) |
| 模块 | `wd_evidence_album` |
| 环境 | Odoo 18 Community Edition；数据库 `odoo18ce` |
| 当前状态 | Passed；六个场景均由用户确认通过 |
| 验证者 | 本会话用户 |

本 HVR 只记录真实用户在后台浏览器中的操作和观察。自动化脚本或 Agent 观察不能替代用户确认。

## 1. 验证总览

| 指标 | 当前值 |
|---|---:|
| Required scenarios | 6 |
| PASS | 6 |
| FAIL | 0 |
| BLOCKED | 0 |
| NOT RUN | 0 |

## 2. 用户需要验证的场景

### HVR-SCN-001 — Source Config 显式配置和校验

- **目的**：确认管理员可以维护来源配置，且无效配置被明确拒绝。
- **步骤**：
  1. 打开 Evidence Album → Configuration → Evidence Sources；
  2. 创建有效配置：选择 `mail.message`，字段填写 `attachment_ids`，配置标题字段 `subject`、描述字段 `body`，并填写面向用户的来源标签；
  3. 保存并确认配置可见；
  4. 尝试填写不存在字段或非 Many2many 附件字段；
  5. 停用配置后尝试使用它创建来源 Page。
- **通过标准**：有效配置可保存；无效模型/字段/关系显示明确错误；停用配置不能继续用于来源采集。
- **证据**：配置成功截图、错误提示截图、停用状态截图。

### HVR-SCN-002 — 从来源记录创建 Page

- **目的**：确认从一个有附件的来源记录创建 Page 和 Item。
- **步骤**：
  1. 准备一个可读取的 `mail.message` 记录，并确保其 `attachment_ids` 中有 JPG/PNG/MP4 附件；
  2. 打开目标 Album；
  3. 使用“从来源记录创建 Page”入口；
  4. 按来源标签选择已启用 Source Config；直接从该配置模型的可读记录显示名称列表中选择单一来源记录，不输入数据库 ID；
  5. 确认创建 Page。
- **通过标准**：创建一个 Page；只创建本次来源记录当前包含并通过校验的附件 Item；Item 的来源模型、记录 ID、字段名可追溯。
- **证据**：创建前来源记录截图、创建后 Page/Item 截图。

### HVR-SCN-003 — 标题/描述映射与用户覆盖

- **目的**：确认显式映射生效，且用户可以覆盖自动填充值。
- **步骤**：
  1. 使用 `subject`/`body` 映射创建 Page；
  2. 检查 Page 标题和描述；
  3. 修改标题和描述并保存；
  4. reload/reopen Page；
  5. 修改来源记录的标题或描述，重新打开已创建 Page。
- **通过标准**：Page 初始值来自显式映射；用户覆盖后持久化；来源记录后续变化不会自动修改既有 Page。
- **证据**：映射前后截图、reload 后截图。

### HVR-SCN-004 — 向既有 Page 添加来源媒体

- **目的**：确认只能从已配置来源字段选择附件，并遵守 Album 唯一性。
- **步骤**：
  1. 打开已有 Page；
  2. 使用“添加来源媒体”入口；
  3. 按来源标签选择 Source Config；直接按记录显示名称选择一个来源记录，再从该记录的配置附件字段中选择附件；
  4. 保存后再次选择同一附件；
  5. 尝试选择不属于该来源字段的附件。
- **通过标准**：合法附件创建来源型 Item；同 Album 重复附件被拒绝；不属于来源字段的附件被拒绝；原始附件不被修改或删除。
- **证据**：成功添加截图、重复错误截图、非法选择错误截图。

### HVR-SCN-005 — 直接上传

- **目的**：确认直接上传创建不绑定业务单据的 Upload 型 Item。
- **步骤**：
  1. 打开目标 Page；
  2. 使用标准附件上传入口上传 JPG、PNG 或 MP4；
  3. 保存 Page/Item 并 reload；
  4. 检查 Item 的 Source Type、来源字段和 Attachment；
  5. 删除 Item，检查附件是否仍存在。
- **通过标准**：Item 的 Source Type 为 Direct Upload；来源模型、来源记录 ID、来源字段为空；附件存在且可用；删除 Item 不删除附件。
- **证据**：上传前后截图、字段截图、删除 Item 后附件仍存在的截图。

### HVR-SCN-006 — 非法媒体和失败事务

- **目的**：确认非法文件不会创建 Item 或孤立附件。
- **步骤**：
  1. 尝试上传非 JPG/JPEG/PNG/MP4 文件；
  2. 尝试上传扩展名与 MIME 不一致的文件；
  3. 尝试上传空文件或损坏图片；
  4. 检查错误提示、Item 列表和附件列表。
- **通过标准**：每种非法输入均被明确拒绝；不创建 Item；不留下无法追踪的半成品附件。
- **证据**：每类错误提示截图、失败后 Item/附件列表截图。

## 3. 运行记录

| Run ID | 日期 | 验证者 | 场景 | 结果 | 证据 |
|---|---|---|---|---|---|
| HVR-RUN-20260924-01 | 2026-09-24 | 本会话用户 | HVR-SCN-001 | PASS | 用户确认 |
| HVR-RUN-20260924-01 | 2026-09-24 | 本会话用户 | HVR-SCN-002 | PASS | 用户确认 |
| HVR-RUN-20260924-01 | 2026-09-24 | 本会话用户 | HVR-SCN-003 | PASS | 用户确认 |
| HVR-RUN-20260924-01 | 2026-09-24 | 本会话用户 | HVR-SCN-004 | PASS | 用户确认 |
| HVR-RUN-20260924-01 | 2026-09-24 | 本会话用户 | HVR-SCN-005 | PASS | 用户确认 |
| HVR-RUN-20260924-01 | 2026-09-24 | 本会话用户 | HVR-SCN-006 | PASS | 用户确认 |

## 4. Agent/Tool 观察（不计入 HVR PASS）

以下记录由 Agent 通过 Playwright 执行，仅作为用户验证的辅助证据，不改变 §1 的 HVR 统计，也不替代用户确认：

| 观察 ID | 场景 | 观察结果 | 证据 |
|---|---|---|---|
| AGENT-OBS-001 | HVR-SCN-002 / HVR-SCN-003 | 使用已启用 Source Config `wd.evidence.album.source.config,1` 和来源记录 `156` 创建 Page 成功；Page 标题和描述自动填充为 `INB/00156`；生成 4 个 Image/Available Item。 | 浏览器页面 `wd.evidence.album.page,24` |
| AGENT-OBS-002 | HVR-SCN-004 | 添加来源附件向导的服务端校验拒绝了不属于配置来源字段的 `wizard-upload.png`，提示 `Only attachments from the configured source field may be selected.` | 浏览器错误对话框 |
| AGENT-OBS-003 | HVR-SCN-005 | 通过 Upload Media 上传 `gizeh.png` 成功；Page 新增 `gizeh.png / Image / Available` Item。 | 浏览器页面 `wd.evidence.album.page,24` |
| AGENT-OBS-004 | HVR-SCN-006 | 上传 `requirements.txt` 被拒绝，提示 `The attachment must have a matching JPG, PNG, or MP4 MIME type.`；未观察到新 Item。 | 浏览器错误对话框 |

## 5. 记录规则

- 用户必须报告实际观察结果，不要把“没有操作”记录为通过；本次六个场景已由用户明确确认通过；
- 每个场景分别记录 PASS、FAIL 或 BLOCKED；
- BLOCKED 必须说明具体阻塞原因；
- 保存、提交或上传后必须 reload/reopen 验证持久化；
- HVR 结果不能替代 ATR 的 ORM/集成验证；
- 所有结果完成后，补登记验证者、执行时间、代码基线和证据位置。
