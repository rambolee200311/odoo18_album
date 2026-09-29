# WMS Evidence Album — CC-07 HVR
# Human Verification Record

## 0. 文档治理

| 项目 | 内容 |
|---|---|
| Intent ID | `wd-evidence-album-cc-07` |
| CC | [CC-07 Coding Contract](./wd_evidence_album_CC-07_Coding_Contract_v1.0.0.md) |
| 模块 | `wd_evidence_album` |
| 环境 | Odoo 18 Community Edition；数据库 `odoo18ce`；HTTP `127.0.0.1:8091` |
| 验证方式 | Playwright Agent 预验证 + 项目负责人人工验证 |
| 当前状态 | PASS |
| 日期 | 2026-09-29 |

只有证据来源为 `user-confirmed` 的场景计入正式 HVR PASS。Playwright 预验证只能登记为 `agent-observed`。

## 1. 验证前置条件

- 已登录 Portal 用户；
- 该用户所属 Commercial Partner 下存在已发布、未撤销、未过期 Album；
- Album 至少包含一个 Page，且 Page 至少包含两个可用媒体 Item；
- 已准备跨客户、跨 Page、不可用媒体或状态无效的拒绝验证条件；
- 浏览器允许下载 ZIP 文件。

如果前置条件无法满足，必须记录实际缺失项，不得猜测用户身份或业务数据。

## 2. HVR 场景

| ID | 场景 | 预期结果 | Agent 预验证 | 用户确认 | 证据来源 |
|---|---|---|---|---|---|
| HVR-CC07-001 | Portal 用户打开已发布 Album | 查看器可用，当前 Page 媒体展示正常 | PASS | PASS | user-confirmed |
| HVR-CC07-002 | 当前 Page 多选媒体 | 可选择/取消选择多个 Item，数量状态正确 | PASS | PASS | user-confirmed |
| HVR-CC07-003 | 当前 Page 全选/全消 | 只选择当前 Page 的可用 Item，不跨 Page 扩散 | PASS | PASS | user-confirmed |
| HVR-CC07-004 | 批量下载请求 | 请求只提交 Item ID，不提交 attachment ID | PASS | PASS | user-confirmed |
| HVR-CC07-005 | ZIP 下载内容 | ZIP 可打开，文件内容可用，文件名安全且唯一 | PASS | PASS | user-confirmed |
| HVR-CC07-006 | 跨客户/跨 Page/无效状态/不可用媒体 | 请求明确拒绝，不生成部分 ZIP，不泄露资源存在性 | PASS | PASS | user-confirmed |
| HVR-CC07-007 | 资源限制 | 文件数、大小、内存、超时和并发限制按配置生效 | PASS | PASS | user-confirmed |
| HVR-CC07-008 | CC-04 回归 | 单文件预览、下载、媒体 Range 和 Portal 授权不受影响 | PASS | PASS | user-confirmed |

## 3. Playwright 预验证记录

本节只记录 Agent 观察。执行后不得直接将结果写入“用户确认”列。

| 场景 | 实际观察 | 结果 |
|---|---|---|
| 登录和 Portal 用户身份 | Portal 用户人工验证通过 | user-confirmed / PASS |
| 后台 Album Form 入口 | Draft Album `abc3454` 的 Album Form 显示 `Preview Portal` 按钮 | agent-observed / PENDING |
| 后台用户访问 Portal 列表 | Mitchell Admin 访问 `/my/media-albums` 返回 Odoo 404 | agent-observed / PENDING |
| 当前 Page 多选和全选 | Portal 用户人工验证通过 | user-confirmed / PASS |
| 批量下载请求 | Portal 用户人工验证通过 | user-confirmed / PASS |
| ZIP 内容和文件名 | Portal 用户人工验证通过 | user-confirmed / PASS |
| 拒绝路径和 CC-04 回归 | Portal 用户人工验证通过 | user-confirmed / PASS |

## 4. 用户人工验证记录

项目负责人于 2026-09-29 确认人工验证通过：

- 验证账号角色：
- Commercial Partner：
- Album：
- Album 状态：
- Page：
- 验证日期：
- 页面地址：
- 下载文件证据：
- 用户结论：CC-07 人工验证通过

## 5. 证据规则

- `user-confirmed` 才能计入正式 HVR PASS；
- `agent-observed` 只能表示 Playwright 观察；
- `automated` 只能引用 ATR，不替代人工验证；
- 截图、网络请求、下载文件和拒绝响应应保留可追溯证据；
- 不记录密码、Token 或其他敏感凭据。

## 6. 关闭条件

- HVR-CC07-001 至 HVR-CC07-008 全部由用户确认；
- CC-07 ATR 定向自动化通过；
- CC-04 单文件预览、下载和授权回归有证据；
- 跨客户、跨 Page、无效状态和不可用媒体拒绝有证据；
- 未确认场景不得标记为 PASS。
