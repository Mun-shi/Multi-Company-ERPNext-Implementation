// Copyright (c) 2026, EZORO and contributors
// For license information, please see license.txt

frappe.query_reports["Intercompany Transaction Tracker"] = {
	"filters": [
		{
			"fieldname": "item_code",
			"label": __("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
			"default": ""
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1)
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()
		}
	],
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname === "si_status" || column.fieldname === "pi_status") {
			if (data[column.fieldname] === "Paid") {
				value = `<div style="text-align: center;"><span class="indicator-pill green">${data[column.fieldname]}</span></div>`;
			} else if (data[column.fieldname] === "Unpaid") {
				value = `<div style="text-align: center;"><span class="indicator-pill orange">${data[column.fieldname]}</span></div>`;
			} else if (data[column.fieldname] === "Overdue") {
				value = `<div style="text-align: center;"><span class="indicator-pill red">${data[column.fieldname]}</span></div>`;
			}
		}
		if (column.fieldname === "inventory_status") {
			value = `<div style="text-align: center;"><span class="indicator-pill green" style="font-weight: 500;">${data[column.fieldname]}</span></div>`;
		}
		if (column.fieldname === "rate_display" || column.fieldname === "amount_display") {
			value = `<div style="text-align: right; padding-right: 6px; font-weight: 500;">${value}</div>`;
		}
		if (column.fieldname === "qty_display") {
			value = `<div style="text-align: center; font-weight: 500;">${value}</div>`;
		}
		return value;
	},
	get_datatable_options(options) {
		return Object.assign(options, {
			layout: "fluid",
			cellHeight: 38,
		});
	}
};
