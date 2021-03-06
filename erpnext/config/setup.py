from frappe import _
from frappe.widgets.moduleview import get_config

data = [
	{
		"label": _("Customize"),
		"icon": "icon-glass",
		"items": [
			{
				"type": "doctype",
				"name": "Features Setup",
				"description": _("Show / Hide features like Serial Nos, POS etc.")
			},
			{
				"type": "doctype",
				"name": "Authorization Rule",
				"description": _("Create rules to restrict transactions based on values.")
			},
			{
				"type": "doctype",
				"name": "Notification Control",
				"label": _("Email Notifications"),
				"description": _("Automatically compose message on submission of transactions.")
			}
		]
	},
	{
		"label": _("Email"),
		"icon": "icon-envelope",
		"items": [
			{
				"type": "doctype",
				"name": "Email Digest",
				"description": _("Create and manage daily, weekly and monthly email digests.")
			},
			{
				"type": "doctype",
				"name": "Email Settings",
				"label": _("Support Email Settings"),
				"description": _("Setup incoming server for support email id. (e.g. support@example.com)")
			},
			{
				"type": "doctype",
				"name": "Sales Email Settings",
				"description": _("Setup incoming server for sales email id. (e.g. sales@example.com)")
			},
			{
				"type": "doctype",
				"name": "Jobs Email Settings",
				"description": _("Setup incoming server for jobs email id. (e.g. jobs@example.com)")
			},
		]
	},
	{
		"label": _("Masters"),
		"icon": "icon-star",
		"items": [
			{
				"type": "doctype",
				"name": "Company",
				"description": _("Company (not Customer or Supplier) master.")
			},
			{
				"type": "doctype",
				"name": "Item",
				"description": _("Item master.")
			},
			{
				"type": "doctype",
				"name": "Customer",
				"description": _("Customer master.")
			},
			{
				"type": "doctype",
				"name": "Supplier",
				"description": _("Supplier master.")
			},
			{
				"type": "doctype",
				"name": "Contact",
				"description": _("Contact master.")
			},
			{
				"type": "doctype",
				"name": "Address",
				"description": _("Address master.")
			},
		]
	},
]

def get_data():
	out = list(data)
	
	for module, label, icon in (
		("accounts", _("Accounts"), "icon-money"),
		("stock", _("Stock"), "icon-truck"),
		("selling", _("Selling"), "icon-tag"),
		("buying", _("Buying"), "icon-shopping-cart"),
		("hr", _("Human Resources"), "icon-group"),
		("support", _("Support"), "icon-phone"),
		("website", _("Website"), "icon-globe")):
		
		try:
			config = get_config("erpnext", module)
		except ImportError:
			continue
		
		for section in config:
			if section.get("label")==_("Setup"):
				out.append({
					"label": label,
					"icon": icon,
					"items": section["items"]
				})
				break
	
	return out