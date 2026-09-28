{
    "name": "WMS Evidence Album",
    "summary": "Evidence albums for customer media delivery",
    "version": "18.0.1.0.0",
    "category": "Operations",
    "author": "WMS",
    "license": "LGPL-3",
    "depends": ["base", "mail", "portal", "web"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/album_views.xml",
        "views/page_views.xml",
        "views/item_views.xml",
        "views/source_config_views.xml",
        "views/wizard_views.xml",
        "views/menus.xml",
        "views/portal_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "wd_evidence_album/static/src/js/evidence_album_viewer.js",
            "wd_evidence_album/static/src/xml/evidence_album_viewer.xml",
        ],
    },
    "installable": True,
    "application": True,
}
