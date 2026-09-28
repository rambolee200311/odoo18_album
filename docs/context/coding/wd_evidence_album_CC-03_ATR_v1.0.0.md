# WMS Evidence Album — CC-03 ATR
# Automated Test Record

## 0. 文档治理

| 项目 | 内容 |
|---|---|
| Intent ID | `wd-evidence-album-cc-03` |
| CC | [CC-03 Coding Contract](./wd_evidence_album_CC-03_Coding_Contract_v1.0.0.md) |
| IHR | [CC-03 IHR](./wd_evidence_album_CC-03_IHR_v1.0.0.md) |
| 环境 | Odoo 18 Community Edition；数据库 `odoo18ce` |
| 执行主体 | AI assistant using Copilot SDK in VS Code |
| 当前状态 | PASS（定向自动化验证）；完整模块测试套件未建立 |

本 ATR 只记录实际执行的命令和结果。浏览器人工确认另见 [CC-03 HVR](./wd_evidence_album_CC-03_HVR_v1.0.0.md)。

## 1. 运行记录

### ATR-RUN-001 — 静态、视图和模块升级验证

| 项目 | 内容 |
|---|---|
| 日期 | 2026-09-28 |
| 命令 | `./venv/bin/python -m compileall -q mymodules/wd_evidence_album` |
| 命令 | `./venv/bin/python odoo-bin -c odoo.conf -d odoo18ce -u wd_evidence_album --stop-after-init --no-http` |
| 命令 | XML 解析、ACL CSV 校验、`git diff --check` |
| 结果 | PASS |

已验证 Python 可编译、Album/Wizard XML 可解析、ACL 每行字段完整、模块可升级。

### ATR-RUN-002 — Odoo Shell 状态机和权限验证

| 项目 | 内容 |
|---|---|
| 日期 | 2026-09-28 |
| 范围 | 临时测试 Album、Page、合法 JPG 附件 |
| 结果 | PASS |

已验证：

- 草稿 Album 不能直接批准；
- 空 Album 提交审核后不能批准；
- 添加 Page/Item 后可批准并发布；
- 发布生成 Token；
- 审核人可以重置 Token，且 Token 改变；
- 管理员可以延长有效期；
- 审核人不能延长有效期；
- 撤销后不能延长有效期；
- `is_expired()` 使用有效期判断；
- 普通 `write({"state": "published"})` 被拒绝；
- 多记录状态动作被拒绝；
- 发布前实际媒体签名不合法时被拒绝。

### ATR-RUN-003 — 浏览器 Agent 辅助观察

| 项目 | 内容 |
|---|---|
| 日期 | 2026-09-28 |
| 页面 | `http://127.0.0.1:8091/odoo/action-312/28`、`/odoo/action-312/29` |
| 结果 | PASS（Agent 观察，不计入正式 HVR PASS） |

已观察：

- 空 Album 提交审核后显示 `Approve`/`Reject`；
- 点击 `Approve` 显示 `An empty album cannot be approved or published. Add a page and media first.`；
- Published Album 显示 `Revoke`、`Reset Token`、`Extend Validity`；
- Extend Validity 打开专用 `Extend Album Validity` 向导；
- Published Album 的有效期字段不可直接编辑。

## 2. 未执行或未完成项

| 项目 | 状态 | 说明 |
|---|---|---|
| 专用 Odoo TransactionCase 测试文件 | NOT RUN | 当前模块尚未建立 CC-03 专用测试文件 |
| 多用户浏览器切换验证 | NOT RUN | 当前浏览器会话为管理员 Agent 观察 |
| 用户正式 HVR 确认 | PASS | 用户于 2026-09-28 确认六个场景全部通过 |
| CC-03 FR | NOT RUN | 不属于本次 IHR/ATR/HVR 请求 |
