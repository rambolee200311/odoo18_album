# WMS Evidence Album — Technical Validation Report

## 验证边界

- Odoo：18.0 Community Edition，项目 `venv` 可导入，版本验证通过。
- 本次主要验证 Odoo 源码契约、Python/HTTP/ZIP 原语和临时策略代码；随后补充了基于项目 `odoo.conf` 的只读 Odoo ORM 验证。
- 未创建业务 ORM 模型、业务 UI 或完整模块。
- 未创建或删除数据库业务数据。真实 Controller 集成、浏览器行为、ACL/Record Rule 的完整交互仍未宣称通过。
- Odoo Shell 连接数据库 `odoo18ce` 成功；所有数据库结论仅限于实际执行的只读 ORM 检查。

## TV-01 媒体访问与自定义 Controller 权限控制

### 验证步骤

1. 检查 Odoo 18 默认 `/web/content` 控制器和 `ir.binary` 的访问检查路径。
2. 编译临时 Controller 策略代码。
3. 用内存中的 Portal 用户、客户和附件对象验证“先授权、后 `sudo()` 读取”。
4. 用 Odoo 的流式响应原语验证 JPG 和 MP4 的响应头。
5. 通过项目 `odoo.conf` 的 Odoo Shell 只读确认数据库中存在附件记录，但当前尚未安装相册模型。

### 临时代码片段

```python
from odoo import http
from odoo.http import request


class TvMediaController(http.Controller):
    @http.route(
        "/tv/album/media/<int:attachment_id>",
        type="http",
        auth="user",
        methods=["GET"],
        website=True,
    )
    def media(self, attachment_id):
        user = request.env.user
        if not user.has_group("base.group_portal"):
            return request.not_found()

        # 临时验证占位：真实模块应以相册项关联关系查询相册。
        album = request.env["wd.evidence.album"].sudo().search(
            [("item_attachment_ids", "in", attachment_id)],
            limit=1,
        )
        if (
            not album
            or album.customer_id.commercial_partner_id
            != user.partner_id.commercial_partner_id
        ):
            return request.not_found()

        attachment = (
            request.env["ir.attachment"]
            .sudo()
            .browse(attachment_id)
            .exists()
        )
        if not attachment:
            return request.not_found()

        return request.make_response(
            attachment.raw,
            headers=[
                (
                    "Content-Type",
                    attachment.mimetype or "application/octet-stream",
                )
            ],
        )
```

### 验证结论

1. **Portal 登录要求：通过（源码验证）**  
   Odoo 18 的 `auth="user"` 会要求用户已认证；仍需显式检查 `base.group_portal`，不能仅依赖登录状态。

2. **自定义路由绕过默认附件权限：需要额外条件**  
   Odoo 18 默认 `/web/content` 会通过 `ir.binary` 对记录执行读取权限检查。自定义 Controller 可以在完成相册授权后用 `sudo()` 读取附件，从而不依赖来源业务记录的 Portal 权限；但 `sudo()` 不能在授权前使用，否则会形成越权。

3. **未授权 Portal 用户拒绝：通过（策略与内存验证）**  
   跨客户用户和非 Portal 用户在授权检查前被拒绝。真实 HTTP 状态仍需在数据库和 Controller 集成测试中确认，推荐统一返回 404，避免泄露资源存在性。

4. **JPG/PNG 与 MP4 流式访问：通过（HTTP 原语验证）**  
   Odoo/Werkzeug 的流式响应能够返回 `image/jpeg`、`image/png` 和 `video/mp4`。浏览器 Range 播放行为尚未在真实浏览器中验证。

5. **仅知道 `attachment_id` 不能绕过相册权限：通过（设计条件成立）**  
   只要相册项关联校验和 Commercial Partner 校验位于 `sudo()` 之前，ID 本身不构成授权。若 Controller 直接按 ID `sudo().browse()` 返回内容，则该结论不成立。

6. **当前数据库运行态：部分验证**  
   Odoo Shell 实际发现数据库中已有 `ir.attachment` 记录，但 `wd.evidence.album` 尚未加载。因此真实相册授权链和自定义 Controller 请求尚未执行，不能把策略验证扩大解释为集成通过。

### 风险与注意事项

- 不得复用 `/web/content` 的匿名访问语义作为相册授权。
- `sudo()` 只能包围已经完成业务授权后的附件读取。
- 必须校验附件属于相册中的相册项、媒体可用、类型合法。
- 真实集成测试仍需覆盖未登录用户、其他客户 Portal 用户、已撤销相册和过期相册。

## TV-02 Portal 用户 → Commercial Partner 的权限判断

### 验证步骤

1. 阅读 Odoo 18 `res.partner.commercial_partner_id` 的计算逻辑。
2. 阅读 `res.users.partner_id` 的标准关系。
3. 用一个公司和三个子联系人执行等价的 Commercial Partner 归一化逻辑。
4. 比较直接联系人相等和 Commercial Partner 相等两种判断。
5. 通过项目 `odoo.conf` 的 Odoo Shell 读取当前数据库 Portal 用户及其 Commercial Partner。

### 临时代码片段

```python
def can_access_album(album, portal_user):
    return (
        album.customer_id.commercial_partner_id
        == portal_user.partner_id.commercial_partner_id
    )
```

### 验证结论

- **同一客户公司的多个 Portal 用户：通过（源码与内存验证）**  
  Odoo 18 中，子联系人通过 `parent_id.commercial_partner_id` 归一到公司主体。因此 John、Mary、David 都可以与 `ABC Company` 相册匹配。

- **相册客户为公司主体：通过**  
  推荐使用：

  ```python
  album.customer_id.commercial_partner_id \
      == request.env.user.partner_id.commercial_partner_id
  ```

- **相册客户为子联系人：需要额外条件**  
  直接比较：

  ```python
  album.customer_id == portal_user.partner_id
  ```

  只允许同一个具体联系人，不符合 SRS 对同一客户公司的要求。使用双方的 `commercial_partner_id` 比较时，子联系人相册仍可被同一商业实体下的 Portal 用户访问。

- **当前数据库 ORM 观察：部分验证**  
  Odoo Shell 实际连接 `odoo18ce`，发现 1 个 Portal 用户（`portal`），其 `partner_id` 与 `commercial_partner_id` 当前为同一联系人。数据库中没有现成的“三个同公司 Portal 联系人”样本，因此该多用户场景仍由源码/内存验证支持，未完成真实数据验证。

### 风险与注意事项

- 建议在相册创建或写入时将客户规范化为 Commercial Partner，或者在所有访问入口统一使用 Commercial Partner 比较。
- 不得只比较 `res.users.partner_id` 的直接 ID。
- 真实 Portal 用户和 Record Rule 行为仍需数据库集成验证。

## TV-03 动态模型 + 动态 Many2many(ir.attachment) 字段读取

### 验证步骤

1. 验证 Odoo 18 存在 `ir.model` / `ir.model.fields` 元数据模型。
2. 验证 Recordset 支持 `record[field_name]` 动态字段读取。
3. 编译并检查动态字段发现和标题/描述字段解析代码。
4. 通过项目 `odoo.conf` 的 Odoo Shell 读取真实元数据。

### 临时代码片段

```python
model = env["ir.model"].search(
    [("model", "=", "wd.qooling.inbound.form")],
    limit=1,
)

attachment_fields = env["ir.model.fields"].search([
    ("model_id", "=", model.id),
    ("ttype", "=", "many2many"),
    ("relation", "=", "ir.attachment"),
])

field_name = attachment_fields[0].name
record = env["wd.qooling.inbound.form"].browse(record_id)
attachments = record[field_name]

title_field = env["ir.model.fields"].search([
    ("model_id", "=", model.id),
    ("name", "=", configured_title_field),
    ("ttype", "=", "char"),
], limit=1)
description_field = env["ir.model.fields"].search([
    ("model_id", "=", model.id),
    ("name", "=", configured_description_field),
], limit=1)
```

### 验证结论

- **通过（源码契约、代码编译及真实 ORM 元数据验证）**  
  Odoo 18 的 `ir.model.fields` 支持按模型、字段类型和 relation 查找字段；Recordset 的 `__getitem__` 支持用运行时字段名读取字段值。

  当前数据库实际发现：

  - `wd.qooling.inbound.form` 存在于 `ir.model` 元数据；
  - `photo_ids` 存在，标签为 `Photos and videos`；
  - 字段类型为 `many2many`，relation 为 `ir.attachment`。

- **动态 Many2many 读取可行，但必须做配置校验**  
  必须确认模型存在、字段仍存在、`ttype == "many2many"`、`relation == "ir.attachment"`，并检查当前后台用户对来源记录和字段有读取权限。

- **标题/描述字段解析可行**  
  `ir.model.fields` 可以解析管理员配置的字段名；实现时必须校验字段类型、字段可读性和字段是否允许作为文本展示。

### 未验证项

当前数据库验证仍不能宣称以下事实通过：

- `wd.qooling.inbound.form` 是否在当前 Odoo Registry 中加载。实际 ORM 检查显示：元数据存在，但 Registry 中未加载该模型；
- 能否对该模型的真实记录执行 `record[field_name]`。由于模型未加载，该运行时读取未执行；
- `photo_ids` 对真实记录是否返回预期附件；
- 当前用户对来源模型和字段的实际权限；
- 多条记录、空字段和已删除字段配置的运行时行为。

## TV-04 Portal 页面 + OWL/JS 媒体查看器实现方式

### 验证步骤

1. 检查 Odoo 18 Portal manifest 是否声明 `web.assets_frontend`。
2. 检查 Portal 是否已经在前端资源中使用 OWL `Component` 和 `mount`。
3. 编译临时的 Portal + OWL 组合思路。
4. 确认图片和视频可以使用普通 HTML 媒体元素指向自定义 HTTP 路由。

### 临时代码片段

```javascript
/** @odoo-module **/

import { Component, xml } from "@odoo/owl";

export class TvAlbumViewer extends Component {
    static template = xml`
        <div class="o_tv_album_viewer">
            <img t-att-src="props.imageUrl" alt="Evidence"/>
            <video t-att-src="props.videoUrl" controls="controls"/>
        </div>
    `;

    static props = ["imageUrl", "videoUrl"];
}
```

Portal 资源声明的最小形态：

```python
"assets": {
    "web.assets_frontend": [
        "wd_evidence_album/static/src/js/album_viewer.js",
    ],
}
```

### 验证结论

- **Portal + OWL：通过（Odoo 18 源码验证）**  
  Portal 已声明 `web.assets_frontend`，并且 Odoo 18 Portal 自身已经使用 `@odoo/owl` 的 `Component` 和 `mount`。

- **`<img src="...">` 与 `<video src="...">`：通过（协议层可行）**  
  两者可以指向自定义媒体 Controller。视频播放需要正确的 `Content-Type`，真实大文件 Range 请求仍需浏览器集成验证。

- **不需要额外的媒体 RPC 才能展示**  
  对于简单查看器，媒体 URL 可以直接作为 HTML 属性；OWL 只负责渲染和交互状态。

### 未验证项与注意事项

- 未运行真实 Portal 页面和浏览器；
- 未验证 QWeb 模板中挂载 OWL 的具体挂载点；
- 需要在 TDD 中确定使用 Portal 页面内挂载、公共 Widget 或独立 OWL App；
- 媒体 URL 仍必须由 Controller 做完整授权，不能因为 URL 出现在 HTML 中就放宽访问控制。

## TV-05 临时 ZIP 生成与流式下载

### 验证步骤

1. 使用 Python `BytesIO` 和 `zipfile.ZipFile` 在内存中生成 ZIP。
2. 先检查文件数量和总字节数，再写入 ZIP。
3. 使用 Odoo/Werkzeug `send_file` 以附件形式返回。
4. 验证超出数量和大小限制时返回用户可理解的错误。

### 临时代码片段

```python
from io import BytesIO
import zipfile

from odoo.http import request

MAX_FILES = 100
MAX_TOTAL_BYTES = 100 * 1024 * 1024


def build_zip(files):
    # files: [(safe_filename, bytes_content), ...]
    if len(files) > MAX_FILES:
        raise ValueError("超过文件数量限制，请分批下载。")

    total_size = sum(len(content) for _, content in files)
    if total_size > MAX_TOTAL_BYTES:
        raise ValueError("超过总大小限制，请分批下载。")

    stream = BytesIO()
    with zipfile.ZipFile(
        stream,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        allowZip64=True,
    ) as archive:
        for filename, content in files:
            archive.writestr(filename, content)

    stream.seek(0)
    return stream


def download_zip(files):
    stream = build_zip(files)
    return request.make_response(
        stream.getvalue(),
        headers=[
            ("Content-Type", "application/zip"),
            ("Content-Disposition", 'attachment; filename="album.zip"'),
        ],
    )
```

### 验证结论

- **内存生成 ZIP：通过**  
  Python `BytesIO` + `zipfile.ZipFile` 可以生成不落盘的 ZIP。

- **流式/附件响应：通过（HTTP 原语验证）**  
  Odoo 18 的响应工具可以返回 `application/zip` 和附件下载头。

- **数量和总大小限制：通过（内存验证）**  
  在读取附件内容并写入 ZIP 前计算数量和总大小，可以可靠阻断超限请求。

- **不需要 OCA `attachment_zipped_download`**  
  V1 的临时 ZIP 需求可以使用 Python 标准库和 Odoo HTTP 响应自行实现。是否引入 OCA 不属于当前必要技术前提。

### 风险与注意事项

- ZIP 内文件名必须清洗，防止路径穿越和重复文件名覆盖。
- 生成 ZIP 前必须先完成相册权限、相册项归属、媒体可用性和附件读取校验。
- 不能把用户提交的 `attachment_id` 直接用于 `sudo()` 读取。
- 大文件场景需要在 TDD 中确定内存上限、超时和并发策略；当前只验证了小型内存 ZIP 原语。

## 总体结论

### 已验证的 SRS 技术假设

- Odoo 18 Community Edition 可以通过自定义 `auth="user"` Controller 实现登录后媒体访问。
- Odoo 18 默认二进制路由会执行附件访问检查；自定义 Controller 可以在自有业务授权完成后使用 `sudo()` 读取附件。
- `Commercial Partner` 判断逻辑成立，能覆盖同一客户公司的多个 Portal 联系人。
- `ir.model.fields` 可以从真实数据库发现配置候选 `photo_ids`；动态 `record[field_name]` 的 API 契约成立，但当前数据库中的来源模型未加载，真实记录读取仍未验证。
- Portal 前端资源可以承载 OWL 组件。
- 图片和视频可以通过自定义媒体 URL 使用 `<img>` / `<video>` 展示。
- 临时 ZIP 可以使用内存流生成和返回，不需要长期保存，也不强制依赖 OCA 模块。

### 必须在 TDD 中明确的条件

- 授权检查必须发生在任何 `sudo()` 附件读取之前。
- Portal 路由必须显式要求登录，并显式校验 Portal 角色。
- 所有媒体 URL 必须校验相册、相册项、Commercial Partner、发布状态、撤销状态、有效期和媒体可用性。
- 相册客户建议规范化为 Commercial Partner，或所有入口统一按 Commercial Partner 比较。
- 动态字段必须验证模型、字段类型、relation、可读权限和字段配置有效性。
- ZIP 文件名清洗、数量限制、总大小限制和大文件资源策略必须写入 TDD。

### 是否可以进入 TDD

**可以进入 TDD，但不能把本报告当作完整集成验收。**

进入 TDD 前不需要因为上述静态验证结果修改 SRS；但 TDD 必须保留本报告中的授权前置条件和未验证项。真实数据库、ACL、Record Rule、Portal 用户、Controller 请求、浏览器媒体播放和大文件 ZIP 必须在后续实施/测试阶段通过 Odoo 运行时和 Playwright/集成测试验证。
