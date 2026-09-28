# WMS Evidence Album — CC-04 IHR
# Implementation History Record

## 0. 文档治理

| 项目 | 内容 |
|---|---|
| Intent ID | `wd-evidence-album-cc-04` |
| CC | [CC-04 Coding Contract](./wd_evidence_album_CC-04_Coding_Contract_v1.0.0.md) |
| 模块 | `wd_evidence_album` |
| 环境 | Odoo 18 Community Edition；数据库 `odoo18ce`；Python venv `venv` |
| 当前状态 | Portal baseline complete；后台体验迭代已实现；后台 HVR 部分待用户确认 |
| 日期 | 2026-09-28 |

## 1. 实施结果

| 任务 | 状态 | 实现位置 |
|---|---|---|
| CC-04-T01 Portal Access Policy | 已实现 | `controllers/portal.py`、`security/security.xml` |
| CC-04-T02 列表和查看器 | 已实现 | `controllers/portal.py`、`views/portal_templates.xml` |
| CC-04-T03 媒体和下载 Controller | 已实现 | `controllers/portal.py` |
| CC-04-T04 OWL 查看器交互 | 已实现 | `static/src/js/evidence_album_viewer.js` |
| CC-04-T05 缩略图 | 已实现 | `controllers/portal.py`，Pillow |
| CC-04-T06 关闭材料 | 已建立 | 本组 IHR/ATR/HVR/FR |

## 2. 实施边界

- Portal 路由使用登录用户、Portal 组、Commercial Partner、Album 状态、撤销、有效期、Page/Item 归属和 Item 可用性组成统一授权链。
- 所有附件读取均在授权检查完成后使用 `sudo()`；公开 URL 仅以 Item ID 为资源边界。
- `/media` 支持 GET/HEAD、单 Range、206 和无效 Range 的 416；下载使用附件文件名生成安全 Content-Disposition。
- CC-04 不实现 ZIP、多选下载、匿名 Token、客户编辑/上传、评论、点赞或视频转码。
- TDD-Q-003 已决议本版本不返回来源信息；TDD-Q-007 已决议使用 Pillow 生成临时图片缩略图。

## 3. 偏差与修复

- Portal 查看器首次浏览器验证发现 Portal 读取附件元数据触发 403；已将附件元数据读取移动到授权后的 `sudo()` 范围。
- OWL 首次验证发现模板未加载和错误 mount 签名；已改用内联 Owl 模板、正确的 `mount(Component, target, options)` 调用及 `useRef` 生命周期访问。
- 筛选方法已绑定为实例箭头函数，避免 Portal 事件调用时丢失组件状态。

## 4. 关闭限制

- 来源信息展示仍由后续需求决定，本版本明确不展示。
- 视频缩略图不生成视频海报，使用原视频控件；不进行转码。

## 5. CC-04 后续后台实施迭代

CC-04 Portal 基线完成后，依据后台 Album/Page 实际使用反馈，继续完成了媒体采集、Gallery 和状态操作的连续迭代。本节记录这些实际变更，避免将其误认为新的 CC 范围或遗漏在原始 IHR 之外。

### 5.1 Page 创建和媒体采集流程

- Album 的 `Pages` 页签新增 `Add Page`、`Create Page from Source` 和 `Create Page & Upload Media` 入口，并统一传递 `default_album_id`。
- 未保存 Album 不允许创建 Page 或媒体；未保存 Page 不显示媒体操作，避免 `album_id` 必填错误。
- `Create Page & Upload Media` 支持一次选择多个照片和视频，每个附件创建一个 Item。
- 批量上传从单文件字段改为 `attachment_ids`，复用媒体校验和 Item 创建逻辑。
- 新增独立的 `evidence_media_upload` OWL Widget，参考 Qooling 的缩略图、文件名和移除交互，但不依赖 `wd_qooling_app`。
- 修复 Odoo 18 `ir.attachment.create()` 扩展的批量 ORM 签名，改为 `@api.model_create_multi`。

### 5.2 Page Gallery 和媒体生命周期

- Page `item_ids` 改为独立 Evidence Album Gallery，支持图片/视频缩略图、图片放大、视频控件、下载和删除。
- Gallery 主动读取 `ir.attachment` 的 `name`、`mimetype` 元数据；视频按 MIME 类型识别。
- 删除仅对 Draft Album 开放，只移除当前 Page 的 Item 关系。
- 来源业务附件不会被删除；直接上传附件仅在没有其他 Item 引用且未绑定业务模型时清理。
- 删除后刷新剩余 Item 的 `availability_state`，并更新 Gallery。
- 已发布、Confirmed 或其他非 Draft Album 从前端隐藏删除按钮，后端 `unlink()` 同样拒绝删除。
- TD-002 已关闭，关闭材料同步更新至 [Technical Debt Register](./wd_evidence_album_Technical_Debt_Register_v1.0.0.md)。

### 5.3 Open Page 上传流程收敛

- 移除 Page 表单顶部的 `Add Source Attachments` 和 `Upload Media` 按钮，避免同一页面出现多个上传入口。
- 移除 Gallery 下方会打开 Wizard 的 `Upload Files` 按钮。
- Open Page 的 Gallery 内嵌 Odoo `FileInput`，使用 Qooling 已验证的交互模式，按钮统一为 `Choose photos and videos`。
- 选中文件后通过 `/web/binary/upload_attachment` 创建附件，再由 Page 后端校验并创建当前 Page 的 Item；不再打开上传 Wizard。
- 后端新增 `create_item_from_attachment()`，校验附件属于当前 Page、媒体类型有效且未在 Album 中重复使用。
- Agent 已通过 Playwright 实际选择测试图片，确认附件创建、Item 创建、Gallery 刷新和删除清理链路成功；测试文件已清理。
- 用户仍反馈其本地浏览器点击后看不到原生文件选择窗口；该问题属于后台 HVR 待确认项，不能以 Agent 的 `fileChooser` 事件观察替代用户确认。

### 5.4 Source Record 选项过滤

- `Create Page from Source` 和 Page 的 `Add Source Attachments` 向导在生成 `Source Record` 选项时，先解析每条业务记录的附件。
- 没有附件的业务记录不再进入下拉选项，避免用户选择后才发现无法创建媒体 Page。
- 过滤在后端 onchange 中执行，不依赖前端隐藏，提交时仍由 `create_page_from_source()` 和 `add_source_attachments()` 做最终校验。

### 5.5 Album 工作流简化

- 将原有 `Draft → Pending Review → Approved → Published → Revoked` 合并为：

  ```text
  Draft ↔ Confirmed ↔ Published → Revoked
  ```

- `Pending Review` 和 `Approved` 历史状态在模型初始化时统一迁移为 `Confirmed`。
- 新增 `Confirm`、`Back to Draft`、`Back to Confirmed` 操作，保留 `Publish`、`Revoke`、`Reset Token` 和 `Extend Validity`。
- `Confirm` 要求 Album 非空；`Publish` 继续执行媒体可用性、媒体类型和附件有效性检查。
- 已发布 Album 返回 Confirmed 时清除访问 Token 和发布时间，但不删除 Page、Item 或附件。
- Portal 仍只展示已发布且未撤销、未过期并通过客户隔离授权的 Album。

## 6. 变更文件

### 6.1 后端和安全

- `mymodules/wd_evidence_album/models/album.py`
- `mymodules/wd_evidence_album/models/page.py`
- `mymodules/wd_evidence_album/models/item.py`
- `mymodules/wd_evidence_album/models/wizards.py`
- `mymodules/wd_evidence_album/security/ir.model.access.csv`

### 6.2 后台视图和前端资产

- `mymodules/wd_evidence_album/views/album_views.xml`
- `mymodules/wd_evidence_album/views/page_views.xml`
- `mymodules/wd_evidence_album/views/wizard_views.xml`
- `mymodules/wd_evidence_album/static/src/js/evidence_media_upload.js`
- `mymodules/wd_evidence_album/static/src/xml/evidence_media_upload.xml`
- `mymodules/wd_evidence_album/static/src/js/evidence_page_media_gallery.js`
- `mymodules/wd_evidence_album/static/src/xml/evidence_page_media_gallery.xml`
- `mymodules/wd_evidence_album/static/src/css/evidence_page_media_gallery.css`
- `mymodules/wd_evidence_album/static/src/css/evidence_media_upload.css`

## 7. 定向验证记录

以下为本轮已执行的定向验证，不等同于完整自动化测试套件：

- Python `compileall`；
- JavaScript `node --check`；
- 变更 XML 解析；
- `git diff --check`；
- Odoo 模块升级和服务重启；
- Add Page、Create Page & Upload Media、批量选择照片/视频；
- Page Gallery 图片放大、视频预览、下载和 Draft 删除；
- FileInput 真实文件选择、附件创建、Item 创建、Gallery 刷新；
- Source Record 无附件记录过滤；
- 简化后的 Album 状态按钮和状态条；
- Portal 原有 CC-04 六个 HVR 场景仍保持原记录，不因后台迭代重新宣称为用户确认。

## 8. 当前状态和后续确认

| 项目 | 状态 |
|---|---|
| Portal CC-04 基线 | 已完成；原 HVR 六个场景用户确认通过 |
| 后台 Page 创建和批量媒体采集 | 已实现；定向验证通过 |
| Gallery 预览、下载和 Draft 删除 | 已实现；定向验证通过 |
| Source Record 无附件过滤 | 已实现；模块升级通过 |
| 简化 Album 工作流 | 已实现；Draft/Published 页面观察通过 |
| 本地浏览器原生文件选择窗口体验 | 待用户确认 |
| 专用后台 HVR/ATR 更新 | 待补充正式证据 |
