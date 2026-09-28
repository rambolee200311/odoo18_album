# WMS Evidence Album — CC-04 HVR
# Human Verification Record

## 0. 文档治理

| 项目 | 内容 |
|---|---|
| Intent ID | `wd-evidence-album-cc-04` |
| CC | [CC-04 Coding Contract](./wd_evidence_album_CC-04_Coding_Contract_v1.0.0.md) |
| IHR | [CC-04 IHR](./wd_evidence_album_CC-04_IHR_v1.0.0.md) |
| ATR | [CC-04 ATR](./wd_evidence_album_CC-04_ATR_v1.0.0.md) |
| 环境 | Odoo 18 Community Edition；Portal 用户 `cc04.portal@example.com` |
| 日期 | 2026-09-28 |
| 当前状态 | Passed; six scenarios user-confirmed |

只有用户明确确认的场景才计入正式 HVR PASS；Agent 观察作为辅助证据。

## 1. 场景结果

| 场景 | 验证内容 | 结果 |
|---|---|---|
| HVR-SCN-001 | Portal 登录后进入 Album 列表 | PASS |
| HVR-SCN-002 | Portal 仅显示所属客户的已发布 Album | PASS |
| HVR-SCN-003 | 打开 Album 查看器并看到 Page、Item 和缩略图 | PASS |
| HVR-SCN-004 | Page 切换和 All/Images/Videos 筛选控件 | PASS |
| HVR-SCN-005 | 图片点击打开灯箱、全屏入口可用 | PASS |
| HVR-SCN-006 | 单文件下载、媒体访问和未授权边界 | PASS |

## 2. 证据来源

| 类型 | 说明 |
|---|---|
| `user-confirmed` | 用户于 2026-09-28 确认六个 Portal 场景全部通过 |
| `agent-observed` | Agent 在共享浏览器看到登录、列表、查看器、控制栏和灯箱 |
| `automated` | ATR 中记录的编译、升级、XML、JavaScript 和差异检查 |

## 3. 备注

- 本次测试数据为 Album `CC-03 HVR Published 20260928`，客户为 Acme Corporation。
- 未配置来源展示，因此 Portal 不显示 source_info；这是 TDD-Q-003 的已决议行为。
