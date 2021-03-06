# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals

import frappe
import frappe.utils
from frappe.utils import cstr
from frappe import msgprint, throw, _

class DocType():
	def __init__(self, d, dl):
		self.doc, self.doclist = d, dl
		
	def onload(self):
		if self.doc.email_sent:
			self.doc.fields["__status_count"] = dict(frappe.db.sql("""select status, count(*)
				from `tabBulk Email` where ref_doctype=%s and ref_docname=%s
				group by status""", (self.doc.doctype, self.doc.name))) or None

	def test_send(self, doctype="Lead"):
		self.recipients = self.doc.test_email_id.split(",")
		self.send_to_doctype = "Lead"
		self.send_bulk()
		msgprint("{send} {email}".format**{
			"send": _("Scheduled to send to"),
			"email": self.doc.test_email_id
		})

	def send_emails(self):
		"""send emails to leads and customers"""
		if self.doc.email_sent:
			throw(_("Newsletter has already been sent"))

		self.recipients = self.get_recipients()
		self.send_bulk()
		
		msgprint("{send} {recipients} {doctype}(s)".format(**{
			"send": _("Scheduled to send to"),
			"recipients": len(self.recipients),
			"doctype": self.send_to_doctype
		}))

		frappe.db.set(self.doc, "email_sent", 1)
	
	def get_recipients(self):
		self.email_field = None
		if self.doc.send_to_type=="Contact":
			self.send_to_doctype = "Contact"
			if self.doc.contact_type == "Customer":		
				return frappe.db.sql_list("""select email_id from tabContact 
					where ifnull(email_id, '') != '' and ifnull(customer, '') != ''""")

			elif self.doc.contact_type == "Supplier":		
				return frappe.db.sql_list("""select email_id from tabContact 
					where ifnull(email_id, '') != '' and ifnull(supplier, '') != ''""")
	
		elif self.doc.send_to_type=="Lead":
			self.send_to_doctype = "Lead"
			conditions = []
			if self.doc.lead_source and self.doc.lead_source != "All":
				conditions.append(" and source='%s'" % self.doc.lead_source)
			if self.doc.lead_status and self.doc.lead_status != "All":
				conditions.append(" and status='%s'" % self.doc.lead_status)

			if conditions:
				conditions = "".join(conditions)
				
			return frappe.db.sql_list("""select email_id from tabLead 
				where ifnull(email_id, '') != '' %s""" % (conditions or ""))

		elif self.doc.send_to_type=="Employee":
			self.send_to_doctype = "Employee"
			self.email_field = "company_email"

			return frappe.db.sql_list("""select 
				if(ifnull(company_email, '')!='', company_email, personal_email) as email_id 
				from `tabEmployee` where status='Active'""")

		elif self.doc.email_list:
			email_list = [cstr(email).strip() for email in self.doc.email_list.split(",")]
			for email in email_list:
				create_lead(email)
					
			self.send_to_doctype = "Lead"
			return email_list
	
	def send_bulk(self):
		self.validate_send()

		sender = self.doc.send_from or frappe.utils.get_formatted_email(self.doc.owner)
		
		from frappe.utils.email_lib.bulk import send
		
		if not frappe.flags.in_test:
			frappe.db.auto_commit_on_many_writes = True

		send(recipients = self.recipients, sender = sender, 
			subject = self.doc.subject, message = self.doc.message,
			doctype = self.send_to_doctype, email_field = self.email_field or "email_id",
			ref_doctype = self.doc.doctype, ref_docname = self.doc.name)

		if not frappe.flags.in_test:
			frappe.db.auto_commit_on_many_writes = False

	def validate_send(self):
		if self.doc.fields.get("__islocal"):
			throw(_("Please save the Newsletter before sending."))

		from frappe import conf
		if (conf.get("status") or None) == "Trial":
			throw(_("Sending newsletters is not allowed for Trial users, \
				to prevent abuse of this feature."))

@frappe.whitelist()
def get_lead_options():
	return {
		"sources": ["All"] + filter(None, 
			frappe.db.sql_list("""select distinct source from tabLead""")),
		"statuses": ["All"] + filter(None, 
			frappe.db.sql_list("""select distinct status from tabLead"""))
	}


def create_lead(email_id):
	"""create a lead if it does not exist"""
	from email.utils import parseaddr
	from frappe.model.doc import get_default_naming_series
	real_name, email_id = parseaddr(email_id)
	
	if frappe.db.get_value("Lead", {"email_id": email_id}):
		return
	
	lead = frappe.bean({
		"doctype": "Lead",
		"email_id": email_id,
		"lead_name": real_name or email_id,
		"status": "Contacted",
		"naming_series": get_default_naming_series("Lead"),
		"company": frappe.db.get_default("company"),
		"source": "Email"
	})
	lead.insert()