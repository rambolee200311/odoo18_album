# WMS Evidence Album — CC-05 ATR
# Automated Test Record

## 0. 文档治理

| 项目 | 内容 |
|---|---|
| Intent ID | `wd-evidence-album-cc-05` |
| 环境 | Odoo 18 Community Edition；数据库 `odoo18ce`；Python venv `venv` |
| 执行主体 | AI assistant using Copilot SDK in VS Code |
| 当前状态 | PASS；自动化检查通过，Portal HVR-CC05-001 至 HVR-CC05-008 全部通过；独立 TDD 证据仍单独治理 |
| 日期 | 2026-09-29 |

浏览器人工确认详见 [CC-05 HVR](./wd_evidence_album_CC-05_HVR_v1.0.0.md)。自动化记录不替代用户 HVR。

## 1. 自动化运行记录

| 运行 | 命令/范围 | 结果 |
|---|---|---|
| CC05-ATR-001 | `./venv/bin/python odoo-bin -c odoo.conf -d odoo18ce -u wd_evidence_album --test-enable --test-tags /wd_evidence_album:TestEvidenceAlbumSourceConfig,/wd_evidence_album:TestEvidenceAlbumPortalRanges --stop-after-init` | PASS |
| CC05-ATR-002 | `python -m py_compile`：Source Config、Portal Controller、Source Config tests | PASS |
| CC05-ATR-003 | `node --check mymodules/wd_evidence_album/static/src/js/evidence_album_viewer.js` | PASS |
| CC05-ATR-004 | Source Config 和 Portal template XML 解析 | PASS |
| CC05-ATR-005 | `git diff --check` | PASS |
| CC05-ATR-006 | Odoo 服务重启后 `GET /web/login` | PASS，HTTP 200 |

## 2. 已覆盖的自动检查

- `_range_bounds()` 原有 Range 处理回归通过；
- Source Config 候选字段同步测试已注册；
- 文本字段仍由 Resolver 服务端校验拒绝；
- Python、JavaScript 和 XML 无语法错误；
- Odoo 模块升级完成；
- 新增 ZIP 资源参数初始化代码已加载；
- Portal 批量下载 Controller 已纳入模块路由代码。

## 3. 尚未覆盖的验证

以下项目必须在 Portal 用户会话和后续测试中完成，当前不标记为 PASS：

| 项目 | 状态 | 所需证据 |
|---|---|---|
| Portal 当前 Page 多选 | 已由 HVR 通过 | HVR + 浏览器验证 |
| ZIP 下载内容 | 已由 HVR 通过 | 浏览器下载 + ZIP 内容检查 |
| Item ID 请求边界 | 已由 HVR 通过 | 网络请求记录 |
| 跨客户/跨 Page/未发布/撤销/过期拒绝 | 已由 HVR 通过 | 浏览器错误记录 |
| 文件数、总大小、内存、超时、并发限制 | 已由 HVR 通过 | 资源边界记录 |
| 文件名清洗和 ZIP 内唯一化 | 已由 HVR 通过 | ZIP 内容检查 |
| CC-04 单文件预览和下载回归 | 已由 HVR 通过 | CC-04 回归验证 |
| TDD-Q-008 动态来源运行时矩阵 | 部分完成 | 动态来源 ATR/IHR |

## 4. 证据限制

- 当前测试覆盖的是定向语法、模块升级和基础模型/Controller 辅助逻辑，不是完整 CC-05 验收套件。
- 未执行的浏览器场景不能被描述为通过。
- TDD-Q-004、TDD-Q-008 和 TD-001 的登记状态不因本 ATR 建立而自动关闭。
