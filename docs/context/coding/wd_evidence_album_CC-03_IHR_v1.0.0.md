# WMS Evidence Album — CC-03 IHR
# Implementation History Record

## 0. 文档治理

| 项目 | 内容 |
|---|---|
| Intent ID | `wd-evidence-album-cc-03` |
| CC | [CC-03 Coding Contract](./wd_evidence_album_CC-03_Coding_Contract_v1.0.0.md) |
| 模块 | `wd_evidence_album` |
| 前置基线 | CC-02 implementation committed at `ff9a18f` |
| 环境 | Odoo 18 Community Edition；数据库 `odoo18ce` |
| 当前状态 | Implementation complete；ATR complete；HVR passed |

本 IHR 记录 CC-03 实际实施事实，不将 Agent 观察替代用户 HVR，也不将定向 Shell 验证描述为完整测试套件。

## 1. 任务实施状态

| 任务 | 实际状态 | 实现位置 |
|---|---|---|
| CC-03-T01 状态动作 | 已实现 | `models/album.py` |
| CC-03-T02 审核/发布权限 | 已实现 | `models/album.py`、`views/album_views.xml` |
| CC-03-T03 发布前一致性检查 | 已实现 | `models/album.py`，复用 Item 可用性和媒体校验 |
| CC-03-T04 Token、撤销和有效期 | 已实现 | `models/album.py`、`models/wizards.py` |
| CC-03-T05 关闭材料 | IHR/ATR 已建立；HVR 待用户确认 | 本组 CC-03 材料 |

## 2. 实际变更

### 2.1 状态机和服务端边界

- 创建 Album 时强制初始状态为 `draft`；
- 实现 `draft → pending_review → approved → published → revoked` 合法路径；
- 非法状态动作抛出明确 `UserError`；
- 所有动作要求单记录调用，多记录调用显式拒绝；
- `state`、`token`、`published_at`、`revoked_at`、`reviewed_by` 禁止通过普通 `write()` 修改；
- 状态动作内部使用受控写入上下文，避免外部调用绕过状态机。

### 2.2 空 Album 和发布前检查

- Album 无 Page 或 Page 无 Item 时不能审核通过；
- 发布前刷新 Item 可用性；
- 发布前复用 `wd.evidence.album.media.validate_attachment()`；
- 检查附件存在、可用状态和 Item 声明的媒体类型一致；
- 未新增第二套 MIME、扩展名或文件头校验。

### 2.3 Token、撤销和有效期

- Token 使用 `secrets.token_urlsafe(32)` 生成；
- 生成后检查唯一性，数据库唯一约束作为最终兜底；
- 发布失败不会写入 Token；
- Token 重置后旧 Token 立即失效，不修改 `published_at`；
- 撤销不删除 Page、Item 或附件；
- `is_expired()` 使用服务器时间判断，过期不改变 Album 状态；
- 新增管理员专用 `action_extend_validity()` 和有效期向导；
- 已发布 Album 的 `valid_until` 不能普通编辑；
- 已撤销 Album 不能通过延长有效期恢复。

### 2.4 后台界面与权限

- 审核、发布、撤销和 Token 重置按钮仅审核人/管理员可见；
- Extend Validity 按钮仅管理员可见；
- 有效期延长通过专用向导执行；
- 新增 `wd.evidence.album.extend.validity.wizard` 管理员 ACL。

## 3. 实施偏差和决策

| 项目 | 记录 |
|---|---|
| 审核人重置 Token | 按冻结 CC-03 决策实现；作为发布权限的运营延伸 |
| 管理员延长有效期 | 按冻结 CC-03 决策实现；不改变状态、Token、发布时间或审核人 |
| CC-02 Item/Page | 未修改其核心生命周期逻辑，仅从 Album 发布检查复用既有入口 |
| TD-002 Gallery Widget | 未纳入 CC-03，仍保持 Open |

## 4. 变更文件

- `mymodules/wd_evidence_album/models/album.py`
- `mymodules/wd_evidence_album/models/wizards.py`
- `mymodules/wd_evidence_album/views/album_views.xml`
- `mymodules/wd_evidence_album/views/wizard_views.xml`
- `mymodules/wd_evidence_album/security/ir.model.access.csv`

## 5. 当前限制

- CC-03 HVR 已由用户于 2026-09-28 确认六个场景全部 PASS；
- CC-03 尚未创建专用 Odoo `TransactionCase` 测试文件；ATR 记录的是已执行的定向编译、升级、Shell 和浏览器 Agent 观察；
- SRS/TDD 中“管理员可延长已发布过期 Album”仍需后续正式补登，当前依据为冻结 CC-03 审批记录。
