# WMS Evidence Album — CC-01 IHR
# Implementation History Record

## 0. 文档治理

| 项目 | 内容 |
|---|---|
| 文档 | CC-01 Implementation History Record |
| Intent ID | `wd-evidence-album-cc-01` |
| CC 引用 | [CC-01 Coding Contract](./wd_evidence_album_CC-01_Coding_Contract_v1.0.0.md)，v1.0.0，Frozen Coding Contract |
| 模块 | `wd_evidence_album` |
| 上游基线 | SRS v1.0.0、TDD v1.0.0、Implementation Plan v1.0.0 |
| 实施目录 | `/Users/lijianqiang/Documents/odoo18_album/mymodules/wd_evidence_album` |
| 当前状态 | Frozen Implementation History Record；实施完成；ATR/HVR/FR 状态独立记录 |
| 冻结日期 | 2026-09-24 |

IHR 只记录实际发生的实施事实，不替代 ATR 的自动化验证结论，也不替代 HVR 的人工验收结论。

## 1. 执行元数据

| 字段 | 值 |
|---|---|
| 实施负责人 | AI assistant using Copilot SDK in VS Code |
| Odoo | 18.0 Community Edition |
| Python | `/Users/lijianqiang/Documents/odoo18_album/venv/bin/python` |
| 数据库验证方式 | Odoo ORM / Odoo Shell；未使用裸 SQL 或数据库客户端 |
| 开始时间 | 2026-09-24 |
| 最后更新 | 2026-09-24 |
| Git 基线 | `9443848`；CC-01 代码和文档已提交并推送 |
| 当前工作树 | CC-01 implementation committed and pushed |

## 2. Coding Contract 基线引用

| 范围 | 引用 |
|---|---|
| 模块骨架 | CC-01 §2、CC-01-T01 |
| ORM 模型 | CC-01 §3、CC-01-T02 至 CC-01-T05 |
| ACL/Record Rule | CC-01 §4、CC-01-T06 |
| 后台视图 | CC-01 §5、CC-01-T07 |
| 关闭材料 | CC-01 §7、CC-01-T08 |

## 3. 当前实施状态摘要

| 项目 | 状态 |
|---|---|
| CC-01-T01 | 已完成 |
| CC-01-T02 | 已完成 |
| CC-01-T03 | 已完成 |
| CC-01-T04 | 已完成 |
| CC-01-T05 | 已完成 |
| CC-01-T06 | 已完成 |
| CC-01-T07 | 已完成 |
| 自动化/脚本验证 | 已执行；详见 ATR |
| 人工验证 | 未执行；详见 HVR |
| 偏差 | 无未经批准的范围偏差 |
| 待处理 | HVR、FR、CC-01 关闭评审 |

## 4. 实施历史条目

### IHR-001 — 创建模块骨架

| 字段 | 内容 |
|---|---|
| 时间 | 2026-09-24 |
| 阶段 | Implementation |
| Action | 创建模块入口、Manifest、models/views/security/data/tests 目录约定 |
| Files / Components | `__init__.py`、`__manifest__.py`、模型/视图/安全目录 |
| Contract Reference | CC-01-T01 |
| Result | Completed |
| Deviation | None |

Manifest 仅声明 `base`、`mail`、`portal`、`web`，未引入具体来源业务模块。

### IHR-002 — 实现 Album、Page、Item ORM 模型

| 字段 | 内容 |
|---|---|
| 时间 | 2026-09-24 |
| 阶段 | Implementation |
| Action | 实现四层核心关系中的 Album、Page、Item 模型、字段、删除策略和约束 |
| Files / Components | `models/album.py`、`models/page.py`、`models/item.py`、`models/__init__.py` |
| Contract Reference | CC-01-T02、T03、T04 |
| Upstream Reference | TDD §2.2—§2.4 |
| Result | Completed |
| Deviation | None |

实际实现包含：Commercial Partner 规范化、Page 跨 Album 拒绝、Item 存储型相关 `album_id`、同 Album 附件唯一性、`ondelete="set null"` 和附件删除后的可用性刷新。

### IHR-003 — 实现 Source Config 和 Resolver 校验接口

| 字段 | 内容 |
|---|---|
| 时间 | 2026-09-24 |
| 阶段 | Implementation |
| Action | 实现来源配置模型及稳定的模型级校验入口 `_validate_for_resolver` |
| Files / Components | `models/source_config.py` |
| Contract Reference | CC-01-T05 |
| Upstream Reference | TDD §2.5、§3 |
| Result | Completed |
| Deviation | None |

校验覆盖 Registry 模型、字段存在性、Many2many→`ir.attachment`、映射字段和读取权限。候选元数据不会自动成为启用配置。

### IHR-004 — 实现后台安全边界

| 字段 | 内容 |
|---|---|
| 时间 | 2026-09-24 |
| 阶段 | Implementation |
| Action | 创建三个后台组、ACL 和 Album/Page/Item Record Rule |
| Files / Components | `security/security.xml`、`security/ir.model.access.csv` |
| Contract Reference | CC-01-T06 |
| Upstream Reference | SRS §9、TDD §11 |
| Result | Completed |
| Deviation | None |

### IHR-005 — 实现后台视图和菜单

| 字段 | 内容 |
|---|---|
| 时间 | 2026-09-24 |
| 阶段 | Implementation |
| Action | 创建 Album/Page/Item/Source Config 的列表、表单、搜索视图、动作和菜单 |
| Files / Components | `views/*.xml` |
| Contract Reference | CC-01-T07 |
| Result | Completed |
| Deviation | None |

CC-03 动作方法仅建立稳定入口，当前实现会明确提示该动作由 CC-03 接管，未提前实现审核/发布业务规则。

### IHR-006 — 修正 Odoo 18 字段兼容性问题

| 字段 | 内容 |
|---|---|
| 时间 | 2026-09-24 |
| 阶段 | Fix |
| Action | Odoo Registry 首次加载发现 `ir.model` 不支持 `ondelete="restrict"`；改为 Odoo 18 可加载的 `cascade` |
| Files / Components | `models/source_config.py` |
| Contract Reference | CC-01-T05 |
| Result | Completed |
| Deviation | None |
| Follow-up | 已重新执行模块安装/升级并通过 |

这是 Odoo 18 技术兼容性修正，不改变 Source Config 的业务校验或停用/删除语义。

### IHR-007 — 补充附件生命周期可用性刷新

| 字段 | 内容 |
|---|---|
| 时间 | 2026-09-24 |
| 阶段 | Fix |
| Action | 继承 `ir.attachment` 的 ORM 生命周期，在附件创建、修改、删除后刷新关联 Item |
| Files / Components | `models/item.py` |
| Contract Reference | CC-01-T04 |
| Upstream Reference | TDD §2.4 |
| Result | Completed |
| Deviation | None |

该修正用于落实 `availability_state` 刷新触发方；Item 删除仍不会删除原始附件。

## 5. 实际变更清单

| 类别 | 实际内容 |
|---|---|
| 模型 | Album、Page、Item、Source Config |
| 安全 | 3 个后台组、ACL、Record Rule |
| 视图 | Album、Page、Item、Source Config |
| 菜单 | Evidence Album、Albums、Configuration、Evidence Sources |
| 生命周期 | Item 可用性刷新、附件删除后 Item 保留 |
| 未实现 | CC-02 Resolver 读取、CC-03 状态业务、CC-04 Portal/Controller、CC-05 ZIP |

## 6. 偏差与停止事件

首次安装尝试因 Odoo 18 拒绝 `ir.model` Many2one 的 `ondelete="restrict"` 而失败。该事件已记录为 IHR-006，并在不改变上游契约的前提下修正；修正后模块安装和升级均通过。没有发生未经批准的范围扩展、回滚或上游文档修改。

## 7. 当前未解决项

- HVR 尚未由可识别的人类验证主体执行；
- FR 尚未形成；
- TDD-Q-008 的动态来源真实 Registry/记录读取验证仍需在 CC-01 结束前形成证据，否则阻塞 CC-02 来源采集；
- CC-03 动作方法当前为接口占位，不属于 CC-01 未完成项。

## 8. Handoff Summary

本 IHR 已冻结，冻结只表示实施历史和实际变更清单已固化，不表示 ATR、HVR 或 FR 的所有工作均已通过。后续若发现事实性遗漏，必须通过版本化变更记录修订，不得静默改写。

代码已交接至 ATR/HVR 阶段。下一步应执行：

1. 按 [ATR](./wd_evidence_album_CC-01_ATR_v1.0.0.md) 记录自动化/脚本验证；
2. 由真实人类验证主体执行 [HVR](./wd_evidence_album_CC-01_HVR_v1.0.0.md)；
3. 再形成 FR 并进行 CC-01 关闭评审。
