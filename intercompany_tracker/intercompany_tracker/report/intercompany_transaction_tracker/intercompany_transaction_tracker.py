# Copyright (c) 2026, EZORO and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{
			"label": _("Date"),
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 105,
			"align": "left",
		},
		{
			"label": _("Sales Invoice (Ecofinit)"),
			"fieldname": "si_name",
			"fieldtype": "Link",
			"options": "Sales Invoice",
			"width": 195,
			"align": "left",
		},
		{
			"label": _("SI Status"),
			"fieldname": "si_status",
			"fieldtype": "Data",
			"width": 95,
			"align": "center",
		},
		{
			"label": _("Purchase Invoice (Metal Green)"),
			"fieldname": "pi_name",
			"fieldtype": "Link",
			"options": "Purchase Invoice",
			"width": 215,
			"align": "left",
		},
		{
			"label": _("PI Status"),
			"fieldname": "pi_status",
			"fieldtype": "Data",
			"width": 95,
			"align": "center",
		},
		{
			"label": _("Item Code"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 140,
			"align": "left",
		},
		{
			"label": _("Quantity (MT)"),
			"fieldname": "qty_display",
			"fieldtype": "Data",
			"width": 110,
			"align": "center",
		},
		{
			"label": _("Unit Rate (SAR)"),
			"fieldname": "rate_display",
			"fieldtype": "Data",
			"width": 120,
			"align": "right",
		},
		{
			"label": _("Total Amount (SAR)"),
			"fieldname": "amount_display",
			"fieldtype": "Data",
			"width": 140,
			"align": "right",
		},
		{
			"label": _("Stock Location (MGSA)"),
			"fieldname": "inventory_status",
			"fieldtype": "Data",
			"width": 160,
			"align": "center",
		},
	]


def get_data(filters=None):
	filters = filters or {}
	conditions = []
	values = {}

	if filters.get("item_code"):
		conditions.append("pii.item_code = %(item_code)s")
		values["item_code"] = filters["item_code"]

	if filters.get("from_date"):
		conditions.append("pi.posting_date >= %(from_date)s")
		values["from_date"] = filters["from_date"]

	if filters.get("to_date"):
		conditions.append("pi.posting_date <= %(to_date)s")
		values["to_date"] = filters["to_date"]

	extra_cond = (" AND " + " AND ".join(conditions)) if conditions else ""

	query = f"""
		SELECT
			pi.name as pi_name,
			pi.posting_date,
			pi.company as pi_company,
			pi.status as pi_status,
			pi.update_stock as pi_update_stock,
			pi.currency as currency,
			pi.inter_company_invoice_reference as si_name,
			pii.item_code,
			pii.item_name,
			pii.qty,
			pii.uom,
			pii.rate,
			pii.amount
		FROM `tabPurchase Invoice` pi
		JOIN `tabPurchase Invoice Item` pii ON pii.parent = pi.name
		WHERE pi.docstatus = 1
		  AND (pi.inter_company_invoice_reference IS NOT NULL AND pi.inter_company_invoice_reference != '')
		  {extra_cond}
		ORDER BY pi.posting_date DESC, pi.name DESC
	"""

	records = frappe.db.sql(query, values, as_dict=True)
	data = []

	for row in records:
		si = frappe.db.get_value(
			"Sales Invoice",
			row.si_name,
			["posting_date", "customer", "company", "status"],
			as_dict=True,
		)

		if si:
			row.si_status = si.status
		else:
			row.si_status = "N/A"

		# Clean formatted numbers for perfect column alignment
		qty_int = int(row.qty) if row.qty.is_integer() else row.qty
		row.qty_display = f"{qty_int:,} {row.uom}"
		row.rate_display = f"{row.rate:,.2f}"
		row.amount_display = f"{row.amount:,.2f}"

		# Check live inventory balance in Metal Green
		stores_qty = frappe.db.get_value("Bin", {"warehouse": "Stores - MGSA", "item_code": row.item_code}, "actual_qty") or 0
		fg_qty = frappe.db.get_value("Bin", {"warehouse": "Finished Goods - MGSA", "item_code": row.item_code}, "actual_qty") or 0

		if fg_qty > 0 and stores_qty > 0:
			row.inventory_status = f"{int(stores_qty)} Stores / {int(fg_qty)} FG"
		elif fg_qty > 0:
			row.inventory_status = f"{int(fg_qty)} FG"
		elif stores_qty > 0:
			row.inventory_status = f"{int(stores_qty)} Stores"
		else:
			row.inventory_status = "In Stock"

		data.append(row)

	return data
