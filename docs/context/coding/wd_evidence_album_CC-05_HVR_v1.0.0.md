# WMS Evidence Album — CC-05 HVR
# Human Verification Record

## 0. 文档治理

| 项目 | 内容 |
|---|---|
| Intent ID | `wd-evidence-album-cc-05` |
| CC | [CC-05 Coding Contract](./wd_evidence_album_CC-05_Coding_Contract_v1.0.0.md) |
| 模块 | `wd_evidence_album` |
| 环境 | Odoo 18 Community Edition；数据库 `odoo18ce`；地址 `http://127.0.0.1:8091` |
| 验证方式 | Playwright 模拟人工操作 |
| 验证日期 | 2026-09-29 |
| 当前状态 | PASS：HVR-CC05-001 至 HVR-CC05-008 全部通过 |

本记录严格区分 Agent/Playwright 观察和项目用户确认。没有 Portal 用户身份的场景不标记为 PASS。

## 1. 验证前置条件

CC-05 HVR 需要：

- 已登录 `base.group_portal` 的 Portal 用户；
- 该用户所属 Commercial Partner 下至少一个已发布、未撤销、未过期 Album；
- Album 中至少一个 Page 包含两个或以上可用 Item；
- 至少准备一个跨客户或不可用 Item 用于拒绝路径；
- 浏览器允许下载 ZIP 文件。

初始共享页面在 Odoo 重启后显示为后台用户 **Mitchell Admin**，Portal URL 访问结果为 404；没有在本次验证中猜测或修改任何用户凭据。

## 2. Playwright 已执行场景

### HVR-CC05-001 Portal-only 访问边界

| 项目 | 内容 |
|---|---|
| 操作 | 使用共享浏览器后台 Admin 会话访问 `/my/evidence-albums` |
| 预期 | 非 Portal 用户不能访问 Portal Album 页面 |
| 实际观察 | 页面显示 Odoo Error 404；页面导航会话显示后台用户 Mitchell Admin |
| 结果 | PASS（Agent/Playwright 观察） |
| 证据 | 浏览器页面快照：`/my/evidence-albums`，HTTP 页面结果为 Error 404 |

该结果只证明 Portal-only 拒绝边界，不证明 Portal 用户能够成功访问。

### HVR-CC05-001A 登录页前端回归修复

| 项目 | 内容 |
|---|---|
| 操作 | Playwright 重载 `/web/login?redirect=%2Fodoo%3F`，监听页面错误并检查登录表单 |
| 初始观察 | 页面抛出 `SyntaxError: Unexpected token '{'`；登录表单保持 `oe_login_form d-none`，没有可见登录框 |
| 根因 | `evidence_album_viewer.js` 中 `clearSelection()` 和 `selectCurrentPage()` 被错误嵌入 `onSelectionChange` 箭头函数 |
| 修复 | 将两个方法移到组件类方法区域；重新执行 `node --check` 并确认前端资源包含修复后的方法 |
| 修复后观察 | Playwright 页面错误为空；用户选择器和 Email/Password 登录表单正常显示 |
| 结果 | PASS（Agent/Playwright 观察） |

该修复属于 CC-05 Portal 前端编码缺陷修复，不等同于 Portal 用户登录或 ZIP HVR 通过。

## 3. 尚未完成的 Portal 用户场景

### HVR-CC05-002 当前 Page 多选

| 项目 | 内容 |
|---|---|
| 操作 | Portal 用户打开已发布 Album，进入包含多个媒体的 Page，选择两个 Item |
| 预期 | 选择框可用，数量提示为 2，只保留当前 Page 的 Item ID |
| 实际结果 | Portal 用户验证通过 |
| 结果 | PASS（用户 HVR） |

### HVR-CC05-003 当前 Page 全选

| 项目 | 内容 |
|---|---|
| 操作 | 使用 “Select all on current Page” 复选框切换当前 Page 的全选/全消状态 |
| 预期 | 当前 Page 的可用 Item 全部选中；不跨 Page 扩散 |
| 实际结果 | 单个复选框支持全选、全消和部分选中状态；操作不跨 Page |
| 结果 | PASS（用户 HVR） |

### HVR-CC05-004 ZIP 下载和内容检查

| 项目 | 内容 |
|---|---|
| 操作 | 选择当前 Page 的多个 Item，点击 “Download selected” |
| 预期 | 下载 `evidence-media.zip`；ZIP 可打开；文件名安全且唯一 |
| 实际结果 | Portal 用户完成选中媒体的 ZIP 下载，下载成功 |
| 结果 | PASS（用户 HVR） |
| 修复 | 增加 Evidence Album → Configuration → ZIP Settings；缺失或非正参数自动恢复为已文档化默认值并写入 `ir.config_parameter` |

### HVR-CC05-005 Item ID 请求边界

| 项目 | 内容 |
|---|---|
| 操作 | 观察批量下载网络请求 |
| 预期 | 请求只包含 Item ID，不包含 attachment ID |
| 实际结果 | Portal 用户确认批量下载网络请求只包含 Item ID，不包含 attachment ID |
| 结果 | PASS（用户 HVR） |

### HVR-CC05-006 越权和状态拒绝

| 项目 | 内容 |
|---|---|
| 操作 | 使用跨客户、跨 Page、未发布、撤销、过期或不可用 Item |
| 预期 | 请求明确失败，不生成部分 ZIP，不泄露附件 |
| 实际结果 | 越权/状态拒绝场景通过 |
| 结果 | PASS（用户 HVR） |

### HVR-CC05-007 资源限制

| 项目 | 内容 |
|---|---|
| 操作 | 构造超过文件数、总大小和超时边界的请求 |
| 预期 | 明确错误，不生成部分 ZIP；并发超限时明确拒绝 |
| 实际结果 | Portal 用户确认文件数、总大小、超时和并发限制均按配置生效，超限请求明确失败 |
| 结果 | PASS（用户 HVR） |

### HVR-CC05-008 CC-04 回归

| 项目 | 内容 |
|---|---|
| 操作 | 在同一 Portal Album 中打开图片、视频并执行单文件下载 |
| 预期 | CC-04 单文件预览、Range/下载和授权行为不受影响 |
| 实际结果 | CC-04 单文件预览和下载回归通过 |
| 结果 | PASS（用户 HVR） |

## 4. 结果汇总

| 场景 | 结果 |
|---|---|
| Portal-only 非 Portal 拒绝 | PASS（Agent/Playwright 观察） |
| 登录页修复 | PASS（Agent/Playwright 观察） |
| 当前 Page 多选 | PASS（用户 HVR） |
| 当前 Page 全选 | PASS：单个全选复选框支持全选、全消和半选 |
| ZIP 下载和 ZIP 内容 | PASS（用户 HVR） |
| Item ID 请求边界 | PASS（用户 HVR） |
| 越权/状态拒绝 | PASS（用户 HVR） |
| 文件数/大小/超时/并发限制 | PASS（用户 HVR） |
| CC-04 单文件回归 | PASS（用户 HVR） |

## 5. 用户 HVR 待办

已由 Portal 用户完成全部人工验证；密码不记录在本文档中。HVR-CC05-001 至 HVR-CC05-008 全部通过。

本轮修复后：

- HVR-CC05-003 使用单个 “Select all” 复选框，支持全选、全消和半选；
- HVR-CC05-004 使用 Media Album → Configuration → ZIP Settings，Portal 用户复测通过；
- HVR-CC05-005 已确认批量请求只提交 Item ID；
- HVR-CC05-007 已确认资源限制按配置生效；
- Media Album Portal 页面已完成重新登录和全部 HVR 复测。

HVR-CC05 全部通过后：

- CC-05 HVR 状态可标记为 PASS；
- TDD-Q-004 不得因代码存在而关闭；
- TDD-Q-008 不得因字段候选测试而关闭；
- Technical Debt Register 中的相关技术债仍需依据独立证据关闭。
