# WMS Evidence Album — CC-04 IHR
# Implementation History Record

## 0. 文档治理

| 项目 | 内容 |
|---|---|
| Intent ID | `wd-evidence-album-cc-04` |
| CC | [CC-04 Coding Contract](./wd_evidence_album_CC-04_Coding_Contract_v1.0.0.md) |
| 模块 | `wd_evidence_album` |
| 环境 | Odoo 18 Community Edition；数据库 `odoo18ce`；Python venv `venv` |
| 当前状态 | Implementation complete; ATR complete; HVR user-confirmed |
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
