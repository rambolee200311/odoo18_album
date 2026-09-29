# WMS Media Albums

基于 Odoo 18 Community Edition 的客户媒体相册模块，用于将图片、视频和
附件按相册和页面组织，并通过受控的 Portal Viewer 发布给客户。

典型流程是：

```text
后台创建相册
  → 上传媒体或从业务来源抓取媒体
  → 确认并发布
  → 客户通过 Portal 查看、筛选和批量下载
```

版本说明：

- 项目版本：`v1.0.0`（Git release tag）；
- Odoo 模块版本：`18.0.1.0.0`（Odoo 模块版本格式）；
- 模块技术名称：`wd_evidence_album`。

## 功能概览

- 创建和管理 Media Albums；
- 按页面组织图片、视频和附件；
- 从业务来源配置动态读取媒体附件；
- 直接上传图片和视频；
- Draft、Confirmed、Published、Revoked 状态流程；
- Published Portal 相册列表和 Viewer；
- 后台用户的发布前 Portal Preview；
- Portal 当前页面媒体筛选、多选和全选；
- 批量 ZIP 下载；
- ZIP 文件数、总大小、内存、超时和并发限制；
- 中文（`zh_CN`）和荷兰文（`nl_NL`）翻译；
- 页面媒体缩略图、预览、下载和删除；
- Odoo ACL、记录规则和 Portal 授权链。

## 技术栈

- Odoo 18 Community Edition；
- PostgreSQL；
- Odoo ORM 和 QWeb；
- OWL、JavaScript 和 Odoo Web Assets；
- Font Awesome 图标。

## 项目结构

在项目根目录 `odoo18_album/` 下：

```text
odoo18_album/
├── odoo-bin
├── odoo.conf
├── venv/                           Python 虚拟环境
├── mymodules/
│   └── wd_evidence_album/          Odoo 模块源码
│       ├── controllers/            Portal、Preview、媒体和 ZIP Controller
│       ├── models/                 Album、Page、Item、Source Config、Settings
│       ├── security/               ACL 和 Record Rules
│       ├── views/                  后台视图、菜单和 Portal QWeb 模板
│       ├── static/src/             OWL、JavaScript、XML 和 CSS 资源
│       ├── tests/                  Odoo 定向测试
│       └── i18n/                   zh_CN.po、nl_NL.po
└── docs/
    └── context/                    项目治理和验证文档
```

## 安装

### 前置条件

1. 已安装 Odoo 18 Community 源码；
2. 已安装并运行 PostgreSQL；
3. 已创建目标数据库；
4. 已准备 Python 虚拟环境；
5. `odoo.conf` 的 `addons_path` 已包含 `mymodules`；
6. 在项目根目录执行以下命令。

示例配置：

```ini
addons_path = addons,odoo/addons,mymodules
```

实际部署时请根据环境设置 `db_host`、`db_port`、`db_user`、`db_password`
和 `db_name`，不要将生产凭据提交到 Git。

### 安装模块

```bash
./venv/bin/python odoo-bin \
  -c odoo.conf \
  -d <数据库名> \
  -i wd_evidence_album \
  --stop-after-init
```

### 升级模块

```bash
./venv/bin/python odoo-bin \
  -c odoo.conf \
  -d <数据库名> \
  -u wd_evidence_album \
  --stop-after-init
```

### 加载翻译

```bash
./venv/bin/python odoo-bin \
  -c odoo.conf \
  -d <数据库名> \
  -u wd_evidence_album \
  --load-language=zh_CN,nl_NL \
  --stop-after-init
```

翻译或视图文件更新后，需要升级模块并刷新浏览器资源。用户语言在 Odoo
用户偏好中设置。

### 卸载模块

卸载前请先备份数据库。可以在 Odoo **Apps** 中打开模块并选择 **Uninstall**；
卸载完成后再停止 Odoo 服务。卸载会删除模块数据及其配置，不应直接在生产
数据库上执行而不经过备份和审批。

## 后台使用

安装并登录后，从 **Media Albums / 媒体相册** 菜单进入：

1. 创建 Draft 相册；
2. 设置相册名称、客户和描述；
3. 使用“从来源创建页面”或“创建页面并上传媒体”创建页面；
4. 在 Draft 状态编辑页面和媒体；
5. 确认相册后提交审核或发布；
6. Published 状态下可设置有效期、重置 Token 或撤销发布。

页面编辑规则：

- Draft 相册：页面可编辑和删除，媒体可上传和删除；
- Confirmed、Published、Revoked 相册：页面和媒体只读；
- 页面删除由服务端状态校验保护，不能通过 RPC/API 绕过界面限制。

### ZIP Settings

管理员可从 **Media Albums → Configuration → ZIP Settings** 配置：

- 最大文件数；
- ZIP 总大小；
- ZIP 内存限制；
- ZIP 生成超时；
- 最大并发下载数。

所有值必须为正数，设置只影响新的 ZIP 请求。

## Portal 与 Preview

路由说明：

| 路由 | 使用者 | 授权方式 | 说明 |
|---|---|---|---|
| `/my/media-albums` | Portal 客户 | Published 状态、Token、Commercial Partner 和有效期 | 正式相册入口 |
| `/my/evidence-albums` | Portal 客户 | 同上 | 旧路由，暂保留兼容 |
| `/odoo/evidence-albums/<id>/preview` | 后台用户 | 后台登录、ACL 和 Record Rule | 发布前预览 |

Preview 路由中的 `<id>` 是 `wd.evidence.album` 的数据库记录 ID。

后台用户从 Album Form 点击 **Preview Portal** 时，预览会在新标签页打开。
直接在浏览器地址栏输入 URL 不会自动创建新标签页。

Preview 的特点：

- 仅允许已认证的后台用户；
- 只允许 Draft 和 Confirmed 相册；
- 不使用 Portal Token、Commercial Partner 或有效期授权；
- 不改变相册状态、Token 或发布时间；
- 复用 Portal Viewer、媒体 URL 和媒体 Controller；
- 显示 `Portal Preview — Not Published` 提示；
- 不提供批量 ZIP 下载。

Published Portal 使用客户的 Commercial Partner、Token、有效期和发布状态
进行授权。

## 权限

后台角色与 Odoo 技术组对应如下：

| 角色 | 技术 ID | 继承 | 说明 |
|---|---|---|---|
| WMS Media Album User | `group_album_user` | — | 管理自己的相册 |
| WMS Media Album Reviewer | `group_album_reviewer` | User | 查看和审核相册 |
| WMS Media Album Manager | `group_album_manager` | Reviewer | 完整管理相册、来源配置和 ZIP Settings |

以上技术 ID 位于 `wd_evidence_album` 模块命名空间下，例如：
`wd_evidence_album.group_album_manager`。

Portal 客户不使用上述后台组，而是使用 Odoo 的 `base.group_portal` 和
模块定义的 Portal 记录规则。

## 媒体和 ZIP 约束

### 用户可见行为约束

- 单次 ZIP 下载仅限同一相册同一页面；
- 只能下载当前用户有权访问且媒体可用的媒体项；
- 超过文件数、大小、内存、超时或并发限制时明确报错；
- 请求失败时不生成部分 ZIP；
- ZIP 实时生成，不长期落盘保存。

### 实现边界

- 批量请求只接受媒体项 ID；
- 授权完成后才允许访问附件内容；
- ZIP 文件名会清理控制字符、路径分隔符和路径穿越片段；
- 重复文件名会自动唯一化；
- Portal 媒体 Controller 支持 MIME、404、缩略图以及 HTTP Range 行为。

## 国际化

模块包含：

- [简体中文](mymodules/wd_evidence_album/i18n/zh_CN.po)；
- [荷兰文](mymodules/wd_evidence_album/i18n/nl_NL.po)。

英语是源字符串和 fallback。新增用户可见文案时：

1. Python 中使用 Odoo `_()`；
2. JavaScript 中使用 Odoo `_t("...")`；
3. XML/QWeb 中直接使用源字符串；
4. 导出对应语言的 PO，例如：

   ```bash
   ./venv/bin/python odoo-bin \
     -c odoo.conf \
     -d <数据库名> \
     --i18n-export=/tmp/wd_evidence_album_zh_CN.po \
     -l zh_CN \
     --modules=wd_evidence_album \
     --stop-after-init
   ```

5. 补充译文后升级模块、加载语言并刷新浏览器资源；
6. 使用 Odoo PO 解析器和页面验证确认翻译已生效。

## 开发与验证

以下命令均在项目根目录执行。

Python 语法检查：

```bash
./venv/bin/python -m compileall -q mymodules/wd_evidence_album
```

JavaScript 语法检查：

```bash
node --check mymodules/wd_evidence_album/static/src/js/evidence_album_viewer.js
node --check mymodules/wd_evidence_album/static/src/js/evidence_page_media_gallery.js
```

定向测试：

```bash
./venv/bin/python odoo-bin \
  -c odoo.conf \
  -d <数据库名> \
  --test-enable \
  --test-tags /wd_evidence_album \
  --stop-after-init
```

项目治理和发布记录见：

- [PVR](docs/context/closure/wd_evidence_album_PVR_v1.0.0.md)
- [PCR](docs/context/closure/wd_evidence_album_PCR_v1.0.0.md)
- [Implementation Plan](docs/context/coding/wd_evidence_album_Implementation_Plan_v1.0.0.md)
- [Coding Contracts](docs/context/coding/)

## 常见问题

### 安装后看不到 Media Albums 菜单

确认用户属于 `wd_evidence_album.group_album_user`、Reviewer 或 Manager，
并确认模块已经升级以及浏览器资源已经刷新。

### Portal 看不到相册

确认相册状态为 Published，客户的 Commercial Partner 与相册客户匹配，
Token 有效且没有超过 `valid_until`。后台 Preview 不代表相册已经发布。

### ZIP 下载失败

确认媒体项属于同一页面、媒体仍然可用，并检查 **ZIP Settings** 中的文件数、
大小、内存、超时和并发限制。

### 修改翻译后页面仍显示英文

确认语言已在数据库中加载，执行模块升级，刷新浏览器资源，并检查用户偏好
使用的是 `zh_CN` 或 `nl_NL`。

## 版本与发布

- 项目版本使用 Git tag，例如 `v1.0.0`；
- Odoo 模块版本写在 `mymodules/wd_evidence_album/__manifest__.py`，
  遵循 Odoo 的模块版本格式；
- 两套版本号用于不同目的，不应直接混用；
- 发布与项目收口的详细记录位于 `docs/context/closure/`。
