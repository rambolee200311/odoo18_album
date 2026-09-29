# WMS Evidence Album — CC-07 ATR
# Automated Test Record

## 0. 文档治理

| 项目 | 内容 |
|---|---|
| Intent ID | `wd-evidence-album-cc-07` |
| CC | [CC-07 Coding Contract](./wd_evidence_album_CC-07_Coding_Contract_v1.0.0.md) |
| 环境 | Odoo 18 Community Edition；数据库 `odoo18ce`；Python venv `venv` |
| 当前状态 | PASS；定向自动化、模块升级和 Portal HVR 均通过 |
| 日期 | 2026-09-29 |

自动化记录不替代 Portal 用户 HVR。

## 1. 自动化运行记录

| 运行 | 命令/范围 | 结果 |
|---|---|---|
| CC07-ATR-001 | `py_compile`：Source Config、Settings、Portal Controller 和测试 | PASS |
| CC07-ATR-002 | `node --check evidence_album_viewer.js` | PASS |
| CC07-ATR-003 | Source Config、Settings XML 解析 | PASS |
| CC07-ATR-004 | `git diff --check` | PASS |
| CC07-ATR-005 | Odoo 定向测试：Source Config、Portal Range/ZIP name、Preview | PASS；备用端口 `8092` |
| CC07-ATR-006 | Odoo 模块升级并加载测试注册 | PASS |
| CC07-ATR-007 | 项目负责人确认 CC-07 Portal 人工验证 | PASS；证据来源 `user-confirmed` |

## 2. 已覆盖的自动检查

- 合法 Source Config 字段候选可同步到 `field_name`；
- 非 Many2many `ir.attachment` 字段被 Resolver 校验拒绝；
- 动态来源读取使用普通权限入口；
- Item ID-only 批量请求和同一 Page 边界存在；
- ZIP 文件名会清洗控制字符、路径分隔符并保证唯一；
- ZIP 资源参数从 `ir.config_parameter` 读取并具备正值校验；
- CC-04 Range 边界测试继续通过；
- CC-06 Preview 定向测试继续通过，未破坏既有预览功能。

## 3. 尚未覆盖的验证

| 项目 | 状态 | 所需证据 |
|---|---|---|
| Portal 用户当前 Page 多选和全选 | 已由 HVR 通过 | 浏览器人工验证 |
| ZIP 实际下载、内容和响应头 | 已由 HVR 通过 | 浏览器下载与 ZIP 检查 |
| 跨客户/跨 Page/未发布/撤销/过期/不可用拒绝 | 已由 HVR 通过 | Portal 会话验证 |
| 文件数、总大小、内存、超时、并发边界 | 已由 HVR 通过 | 资源边界 HVR/ATR |
| CC-04 单文件预览、下载和授权回归 | 已由 HVR 通过 | CC-04 HVR/ATR 引用 |
| TDD-Q-008 动态来源运行时矩阵 | 部分完成 | 独立 TDD 证据 |

## 4. 证据限制

- 未完成的浏览器场景不能标记为 PASS；
- `agent-observed` 和 `automated` 不能替代 `user-confirmed`；
- Implementation Plan 的 CC-05 → CC-07 编号迁移、TDD-Q-004、TDD-Q-008 和 TD-001 仍需独立治理。
