# WMS Evidence Album — CC-02 ATR
# Automated Test Record

## 0. 文档治理

| 项目 | 内容 |
|---|---|
| Intent ID | `wd-evidence-album-cc-02` |
| IHR | [CC-02 IHR](./wd_evidence_album_CC-02_IHR_v1.0.0.md) |
| CC | [CC-02 Coding Contract](./wd_evidence_album_CC-02_Coding_Contract_v1.0.0.md) |
| 环境 | Odoo 18 Community Edition；数据库 `odoo18ce` |
| 执行主体 | AI assistant using Copilot SDK in VS Code |
| 当前状态 | Partial |

本 ATR 记录实际执行的编译、模块升级和定向 ORM 验证，不把未执行的完整测试套件写成通过。

## 1. 验证运行

### ATR-RUN-001

| 项目 | 内容 |
|---|---|
| 时间 | 2026-09-24 |
| 代码范围 | CC-02 未提交工作树 |
| 执行内容 | Python 编译、模块升级、Resolver、来源 Page/Item、既有 Page 添加、非法媒体、直接上传 |
| 结果 | PASS（定向验证） |

已验证：

- `record[field_name]` 动态读取；
- `mail.message.attachment_ids` Many2many → `ir.attachment`；
- 来源型 Page/Item 创建；
- 标题/描述显式映射；
- 既有 Page 添加来源附件；
- 不支持映射字段拒绝；
- 非法图片内容拒绝；
- 直接上传生成 `source_type="upload"` Item；
- 上传 Item 删除后原始附件保留；
- Item 来源快照与上传型空来源字段约束。

## 2. 未执行和阻塞项

| 项目 | 状态 | 说明 |
|---|---|---|
| TDD-Q-002 默认映射 | PASS | 用户确认未配置标题/描述字段时拒绝创建，不做隐式默认推导；首次定向运行已观察到缺少标题字段时返回明确 `UserError` |
| 多来源模型权限矩阵 | NOT RUN | 当前使用专用 `mail.message` 验证模型 |
| 模块专用测试套件 | NOT RUN | 尚未编写/执行 CC-02 专用测试文件 |
| 浏览器 HVR | NOT RUN | 待后续人工验证 |
| CC-02 FR | NOT RUN | 待所有关闭材料完成 |

ATR 不要求在此文档中写具体测试代码；测试代码和后续执行证据应通过版本化 ATR 更新。
