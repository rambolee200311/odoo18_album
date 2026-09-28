# WMS Evidence Album — CC-04 ATR
# Automated Test Record

## 0. 文档治理

| 项目 | 内容 |
|---|---|
| Intent ID | `wd-evidence-album-cc-04` |
| 环境 | Odoo 18 Community Edition；数据库 `odoo18ce` |
| 执行主体 | AI assistant using Copilot SDK in VS Code |
| 当前状态 | PASS |
| 日期 | 2026-09-28 |

浏览器人工确认另见 [CC-04 HVR](./wd_evidence_album_CC-04_HVR_v1.0.0.md)。

## 1. 自动化运行记录

| 运行 | 命令/范围 | 结果 |
|---|---|---|
| ATR-RUN-001 | `./venv/bin/python -m compileall -q mymodules/wd_evidence_album` | PASS |
| ATR-RUN-002 | Odoo 模块升级：`-u wd_evidence_album --stop-after-init --no-http` | PASS |
| ATR-RUN-003 | `node --check mymodules/wd_evidence_album/static/src/js/evidence_album_viewer.js` | PASS |
| ATR-RUN-004 | Portal XML、OWL XML、security XML 解析 | PASS |
| ATR-RUN-005 | `git diff --check` | PASS |
| ATR-RUN-006 | `tests/test_portal.py` 定向测试命令 | PASS |

## 2. 浏览器辅助自动观察

- Portal 未登录访问 `/my/evidence-albums` 重定向到 `/web/login`。
- Portal 用户登录后仅看到其 Commercial Partner 的已发布 Album。
- 直接访问 Album 查看器成功渲染 Page 1、媒体缩略图和下载链接。
- OWL 控制栏渲染 Page、All、Images、Videos 四个按钮。
- 图片点击打开灯箱；资源 URL 使用 Item ID，不暴露 attachment_id。
- 跨客户、未发布、撤销或过期资源应由统一策略返回 404。

## 3. 未覆盖项

- 完整数据库级 Portal TransactionCase 尚未建立；本记录不将基础 Range 单测扩展描述为完整权限套件。
- 用户确认场景记录在 HVR，不由 Agent 观察替代。
