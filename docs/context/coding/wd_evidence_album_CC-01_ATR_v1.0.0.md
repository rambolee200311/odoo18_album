# WMS Evidence Album — CC-01 ATR
# Automated Test Record

## 0. 文档治理

| 项目 | 内容 |
|---|---|
| Intent ID | `wd-evidence-album-cc-01` |
| IHR | [CC-01 IHR](./wd_evidence_album_CC-01_IHR_v1.0.0.md) |
| CC | [CC-01 Coding Contract](./wd_evidence_album_CC-01_Coding_Contract_v1.0.0.md) |
| 模块 | `wd_evidence_album` |
| 环境 | Odoo 18 Community Edition；Python venv；数据库 `odoo18ce` |
| 当前代码基线 | `000424d` + 未提交 CC-01 工作树 |
| 执行主体 | AI assistant using Copilot SDK in VS Code |
| 当前状态 | Partial：已执行定向自动化/脚本验证；尚无模块测试套件 |

本 ATR 只记录实际执行的命令和结果，不把未执行的完整 Odoo 测试套件写成通过。

## 1. Test Contract Baseline

| 来源 | 验证范围 |
|---|---|
| CC-01 AC-01 | 模块可安装且无具体来源依赖 |
| CC-01 AC-02 | 四个模型、字段和关系 |
| CC-01 AC-03 | 删除策略和附件保留 |
| CC-01 AC-04 | `album_id` 派生及跨 Album 拒绝 |
| CC-01 AC-05 | 同 Album 附件唯一性 |
| CC-01 AC-07 | 后台安全文件可加载 |
| CC-01 AC-08 | Source Config 模型可加载 |

## 2. Current Automated Test Status

| 指标 | 值 |
|---|---:|
| Required automated verification groups | 6 |
| PASS | 6 |
| FAIL | 0 |
| BLOCKED | 0 |
| NOT RUN | 模块专用自动化测试文件、真实角色 ACL 测试 |
| Latest valid run | ATR-RUN-001 |
| Evidence baseline match | Yes；执行后未发生代码修改 |
| Overall status | Partial |

## 3. Coverage Matrix

| 验证项 | 执行内容 | Run | 结果 | 证据 |
|---|---|---|---|---|
| Python module syntax | `./venv/bin/python -m compileall -q mymodules/wd_evidence_album` | ATR-RUN-001 | PASS | 命令退出码 0 |
| XML syntax | `xmllint --noout security/security.xml views/*.xml` | ATR-RUN-001 | PASS | 命令退出码 0 |
| Module installation | `odoo-bin ... -i wd_evidence_album --stop-after-init --no-http` | ATR-RUN-001 | PASS | Odoo 命令退出码 0 |
| Module upgrade | `odoo-bin ... -u wd_evidence_album --stop-after-init --no-http` | ATR-RUN-001 | PASS | Odoo 命令退出码 0 |
| ORM lifecycle | Odoo Shell 创建 Album/Page/Item，删除附件并检查 Item 保留/不可用 | ATR-RUN-001 | PASS | Shell 输出 `CC-01 final ORM verification: PASS` |
| ORM constraints | Odoo Shell 验证重复附件和跨 Album Page 移动拒绝 | ATR-RUN-001 | PASS | Shell 输出 `CC-01 constraint verification: PASS` |
| Module-specific test suite | 无 CC-01 测试文件；仅保留 tests 占位 | — | NOT RUN | 后续测试任务 |
| Real role ACL/Record Rule | 未创建专用角色测试脚本 | — | NOT RUN | 需要后续自动化测试任务 |

## 4. Test Run History

### ATR-RUN-001

| 字段 | 内容 |
|---|---|
| Timestamp | 2026-09-24 |
| Code Baseline | `000424d` + CC-01 未提交工作树 |
| Environment | Odoo 18 Community Edition；数据库 `odoo18ce` |
| Scope | CC-01 定向静态检查、模块安装/升级、Odoo ORM 验证 |
| Invocation | 见 §3 命令和 Odoo Shell 验证脚本 |
| Executed | 6 个验证组 |
| PASS / FAIL / NOT RUN | 6 / 0 / 2 项补充覆盖未执行 |
| Result | PARTIAL |
| Evidence | 当前会话命令执行输出 |
| Follow-up | 补充模块测试和真实角色 ACL/Record Rule 自动化覆盖 |

## 5. Failure / Stop History

首次模块安装曾因 `ir.model` 字段的 `ondelete="restrict"` 与 Odoo 18 兼容性冲突而失败；修正后重新执行安装/升级并通过。该修正记录于 IHR-006，失败历史未删除。

## 6. Regression Verification

当前没有既有 `wd_evidence_album` 代码或测试可作为回归基线。Odoo 官方模块未被修改；本次只通过模块安装/升级验证未破坏 Registry 加载。

## 7. Issues and Follow-up

| Issue | 状态 | 影响 |
|---|---|---|
| 专用模块测试文件尚未编写 | Open | 不影响本次定向 ORM 验证；影响自动化覆盖完整性 |
| 真实后台角色访问验证尚未自动化 | Open | ACL/Record Rule 仍需 HVR 和后续自动化验证 |
| TDD-Q-008 | Open / CC-01 前置 | 未解决将阻塞 CC-02 来源采集 |

## 8. Handoff Summary

ATR 证明了本次执行范围内的静态检查、模块加载和核心 ORM 生命周期行为；它不证明人工 UI 验收，也不证明完整角色权限测试已经通过。下一步交由 HVR 执行人工场景。
