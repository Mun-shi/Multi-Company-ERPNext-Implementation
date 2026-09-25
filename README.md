# Intercompany Transaction Tracker (`intercompany_tracker`)

A production-grade custom Frappe application designed for multi-company supply chain tracking between **Ecofinit Dubai** (Procurement & Trading Entity) and **Metal Green Saudi Arabia** (Operating & Recycling Entity).

Developed as part of the Technical Assessment for **EZORO DIGITAL SOLUTIONS LLP**.

---

## Table of Contents
1. [Business Architecture & Flow Overview](#1-business-architecture--flow-overview)
2. [Installation & Setup Instructions](#2-installation--setup-instructions)
3. [Standard ERPNext Features vs Customizations](#3-standard-erpnext-features-vs-customizations)
4. [Assumptions Made During Implementation](#4-assumptions-made-during-implementation)
5. [Automated Test Suite](#5-automated-test-suite)
6. [Task 10: Deep-Dive Debugging Exercise (PR Mismatch Issue)](#6-task-10-deep-dive-debugging-exercise)
7. [Task 12: Technical Architecture & Governance Answers](#7-task-12-technical-architecture--governance-answers)

---

## 1. Business Architecture & Flow Overview

This implementation models an international circular economy and scrap metal trading operation across two legal entities:

```
[ External Supplier ]
(Global Metal Trading LLC)
         │
         │  1. Purchase Order: 100 MT @ SAR 2,000 (AED 196,000)
         ▼
[ Ecofinit Dubai ] (Procuring Entity - Base Currency: AED)
   ├── 2. Partial Receipts: GRN 1 (30 MT) + GRN 2 (40 MT) = 70 MT Checkpoint
   ├── 3. Final Receipt: GRN 3 (30 MT) -> PO Status: 100% Received ("To Bill")
   ├── 4. Supplier Purchase Invoice with native Commercial Invoice attachment
   ├── 5. Sales Order for Metal Green: 100 MT @ SAR 2,000
   └── 6. Multi-Tier Workflow: Draft -> Pending Approval -> Approved (Manager Role)
         │
         │  7. Intercompany Invoicing (Native Mapping)
         ▼
[ Metal Green Saudi Arabia ] (Operating Entity - Base Currency: SAR)
   ├── 8. Inter-Company Purchase Invoice auto-generated and submitted
   ├── 9. Stock Receipt into "Stores - MGSA" (100 MT)
   └── 10. Internal Transfer: Stores - MGSA -> Finished Goods - MGSA (50 MT)
         │
         ▼
[ Intercompany Transaction Tracker ]
(Custom Frappe App & Script Report: Unified Audit & Reconciliation Dashboard)
```

---

## 2. Installation & Setup Instructions

### Prerequisites
- Frappe Framework v15.x
- ERPNext v15.x
- Python 3.10+ / 3.12+
- MariaDB 10.6+

### Step-by-Step Installation

```bash
# 1. Navigate to your frappe bench directory
cd /home/ubuntu/frappe-bench

# 2. Get the app from GitHub (or local apps folder)
bench get-app https://github.com/Mun-shi/Multi-Company-ERPNext-Implementation.git

# 3. Install the app on your site
bench --site machinetest.local install-app intercompany_tracker

# 4. Run migrations and clear cache
bench --site machinetest.local migrate
bench --site machinetest.local clear-cache
```

### Accessing the Report
Once installed, open Desk and search for **`Intercompany Transaction Tracker`** in the Awesome Bar, or navigate directly to:
```
http://<your-server-ip>:8000/app/query-report/Intercompany%20Transaction%20Tracker
```

---

## 3. Standard ERPNext Features vs Customizations

Following the **Important Assessment Principles**, standard ERPNext features were maximized to ensure zero core bloat, long-term upgradeability, and strict adherence to framework best practices.

### A. Standard ERPNext Features Used
1. **Multi-Company Architecture**: Dual corporate entities configured in a single bench instance:
   - `Ecofinit Dubai` (Abbr: `ED`, Currency: `AED`, UAE Chart of Accounts).
   - `Metal Green Saudi Arabia` (Abbr: `MGSA`, Currency: `SAR`, Standard Chart of Accounts).
2. **Currency Exchange & Multi-Currency Valuation**:
   - `Currency Exchange` master configured for `SAR` to `AED` @ `0.98` for both Buying and Selling.
   - Dual-currency general ledger tracking using standard GL entries (`SAR` transaction balance, `AED` base financial reporting).
3. **Internal Customer / Supplier Mapping**:
   - Customer `Metal Green Saudi Arabia` in Ecofinit linked with `is_internal_customer = 1` representing `Metal Green Saudi Arabia`.
   - Supplier `Ecofinit Dubai` in Metal Green linked with `is_internal_supplier = 1` representing `Ecofinit Dubai`.
4. **Partial Goods Receipts (GRN Workflow)**:
   - Standard `Purchase Receipt` documents linked to `Purchase Order` (`PUR-ORD-2026-00001`).
   - Handled three partial deliveries (30 MT, 40 MT, 30 MT) with automatic recalculation of `received_qty` and `per_received`.
5. **Native Document Management**:
   - Used Frappe's standard `File` doctype and desk attachment manager to attach supplier commercial invoices and bills of lading to submitted invoices.
6. **Multi-Currency Party Accounting**:
   - Enabled standard `allow_multi_currency_invoices_against_single_party_account` in **Accounts Settings**, keeping the Chart of Accounts clean while allowing SAR invoices against the base AED payable ledger.
7. **Frappe Workflow Engine**:
   - Configured standard `Workflow` on `Sales Order` with roles (`Sales User`, `Sales Manager`), custom states (`Draft`, `Pending Approval`, `Approved`, `Rejected`), and automated submission on approval.
8. **Intercompany Invoice Generation**:
   - Used standard `make_inter_company_transaction` mechanism from `Sales Invoice` to create the downstream `Purchase Invoice`.
9. **Perpetual Inventory & Stock Transfers**:
   - Automatic inventory valuation via `Stock In Hand - MGSA`.
   - Material movement executed using standard `Stock Entry` (Purpose: `Material Transfer`).

### B. Customizations Introduced
1. **Custom Frappe App (`intercompany_tracker`)**:
   - Independent modular application cleanly separated from ERPNext core.
2. **Custom Script Report (`Intercompany Transaction Tracker`)**:
   - Python-driven query and mapper that dynamically pairs Ecofinit Sales Invoices with Metal Green Purchase Invoices.
   - Real-time stock status computation reading actual bin balances across `Stores - MGSA` and `Finished Goods - MGSA`.
   - Client-side formatting with color-coded status pills and fluid container-width alignment.
3. **Workflow Master Records**:
   - Standard Workflow configuration linking `Sales Order` to role-governed authorization states.

---

## 4. Assumptions Made During Implementation

1. **Procurement Entity Role**: Ecofinit Dubai acts as the commercial buying entity that holds the relationship with foreign raw material suppliers, while Metal Green Saudi Arabia is the physical receiving and operating plant.
2. **Fixed Operational Exchange Rate**: An exchange rate of `1 SAR = 0.98 AED` was applied for the duration of the demonstration period. In production, an automated daily currency feed or central bank integration would be connected.
3. **Perpetual Inventory Enabled**: Both companies maintain real-time automated stock accounting. Goods received into warehouse immediately credit the clearing account / trade payable and debit the inventory asset ledger.
4. **Single Tax Regime in Baseline Phase**: Intercompany trade was configured under cross-border zero-rated/standard pricing, pending Phase 2 ZATCA tax rules.
5. **Warehouse Hierarchy**: Metal Green utilizes standard warehouse separation: raw unloading into `Stores - MGSA`, and secondary staging / production output into `Finished Goods - MGSA`.

---

## 5. Automated Test Suite

A dedicated unit test suite is included in the custom app to validate report execution, column integrity, and data matching.

### Running the Tests
```bash
bench --site machinetest.local run-tests --module intercompany_tracker.intercompany_tracker.report.intercompany_transaction_tracker.test_intercompany_transaction_tracker
```

### Test Coverage:
- Verifies that all 10 report columns are generated with correct fieldtypes and alignment.
- Validates the cross-company join between `Sales Invoice` and `Purchase Invoice`.
- Asserts that transaction quantity (100 MT), unit rate (SAR 2,000), and total value (SAR 200,000) match between legal entities.

---

## 6. Task 10: Deep-Dive Debugging Exercise

### Scenario:
> *A Purchase Order is for 100 MT. Two submitted Purchase Receipts total only 70 MT (e.g. 30 MT and 40 MT), but the Purchase Order dashboard incorrectly shows 100 MT received.*

### Diagnostic Methodology & Root Cause Investigation:

An experienced ERPNext engineer does not guess or immediately patch the database. A structured, evidence-based diagnostic process is executed:

#### Step 1: Database & Field-Level Inspection
First, check the source tables directly via MariaDB / Frappe Console to isolate data truth from UI caching:

```python
# In bench console:
po = frappe.get_doc("Purchase Order", "PUR-ORD-2026-00001")
for item in po.items:
    print(f"PO Item {item.name}: Qty={item.qty}, Received Qty={item.received_qty}, Billed Qty={item.billed_qty}")

# Check actual submitted Purchase Receipt child items linked to this PO
pr_items = frappe.db.sql("""
    SELECT pri.parent, pri.item_code, pri.qty, pr.docstatus
    FROM `tabPurchase Receipt Item` pri
    JOIN `tabPurchase Receipt` pr ON pr.name = pri.parent
    WHERE pri.purchase_order = %s AND pr.docstatus = 1
""", ("PUR-ORD-2026-00001",), as_dict=True)

print("Actual submitted PR rows:", pr_items)
print("Total actual qty received:", sum(r.qty for r in pr_items))
```

**Diagnostic Questions**:
- Does `SUM(tabPurchase Receipt Item.qty)` equal `70.0`?
- Is `tabPurchase Order Item.received_qty` stored as `100.0` or `70.0`?
  - If DB has `70.0` but UI shows `100.0`: The issue is a **Client-Side Cache / Redis Cache / Dashboard getter defect**.
  - If DB has `100.0`: The issue is a **Database Write / Controller Update defect**.

#### Step 2: Trace Document Relationships & Hidden Receipts
Check if another document erroneously links to the PO:
```python
# Check if a 3rd draft, cancelled, or duplicate PR updated the parent before failing
all_linked = frappe.get_all("Purchase Receipt Item", 
    filters={"purchase_order": "PUR-ORD-2026-00001"}, 
    fields=["parent", "qty", "docstatus"])
print("All linked rows (draft, submitted, cancelled):", all_linked)
```
- Verify if a third PR was submitted and subsequently cancelled without properly reverting `received_qty`.
- Check if a Purchase Invoice was submitted with **Update Stock = 1** directly against the PO, which updates `received_qty` independently of Purchase Receipts.

#### Step 3: Inspect ERPNext Core Execution Logic
In ERPNext, `received_qty` on PO items is maintained by `erpnext.controllers.buying_controller.update_qty`:
- When a Purchase Receipt is submitted (`on_submit`), it calls:
  `self.update_prevdoc_detail()` $\rightarrow$ queries all submitted PR items for that PO line and updates `tabPurchase Order Item.received_qty`.
- When a Purchase Receipt is cancelled (`on_cancel`), it recalculates and subtracts.

**Potential Culprits**:
1. **Custom Client Script / Server Script**: A custom script triggered on submit overriding `po_item.received_qty` or setting `po.per_received = 100`.
2. **Asynchronous Background Worker Race Condition**: If multiple receipts were submitted simultaneously via API or background jobs, two worker threads updating the same PO item simultaneously without row-level locking (`SELECT ... FOR UPDATE`) can create lost-update concurrency anomalies.
3. **UOM Conversion Mismatch**: The PO was ordered in `MT` (100 MT), but one PR was entered in `Kg` (e.g. 70,000 Kg with a faulty conversion factor of 1 instead of 0.001), skewing the calculation.
4. **Direct Purchase Invoice with "Update Stock"**: If a user created a Purchase Invoice directly from the PO for 30 MT with "Update Stock" checked, ERPNext treats that invoice as physical stock receipt, adding 30 MT to `received_qty` on top of the 70 MT PRs!

#### Step 4: Audit Server Logs & Frappe Version History
- Inspect `tabVersion` for `Purchase Order`:
  `frappe.get_all("Version", filters={"docname": "PUR-ORD-2026-00001"}, fields=["data", "owner", "creation"])`
  This reveals exactly which user, script, or automated process changed `received_qty` to 100.
- Check `logs/worker.error.log` and `Error Log` doctype for failed rollbacks during document cancellation.

#### Step 5: Safe Resolution & Long-Term Prevention
1. **Never directly SQL `UPDATE tabPurchase Order`**: Use ERPNext's standard document updater to maintain document lifecycle consistency:
   ```python
   po = frappe.get_doc("Purchase Order", "PUR-ORD-2026-00001")
   po.update_received_qty()
   po.set_status(update=True)
   frappe.db.commit()
   ```
2. **Prevention**:
   - Ensure custom apps do not hook into `on_submit` of `Purchase Receipt` with unhandled database commits.
   - Enforce UOM validation rules on item masters.
   - If high-volume API ingest is used, ensure transactions lock the PO parent row (`for_update=True`).

---

## 7. Task 12: Technical Architecture & Governance Answers

### Question 1: What requirements did you achieve using standard ERPNext?
We achieved over **90% of the entire assessment scope** using native, un-customized ERPNext features:
- Complete multi-company structure with distinct base currencies (AED and SAR).
- Multi-currency transaction processing with automated exchange rate conversion (0.98).
- Multi-currency party liability accounting against a single consolidated ledger (`Trade Payable - ED`).
- Native document attachment capability on submitted financial records without third-party plugins.
- Multi-partial Goods Receipts (30 MT, 40 MT, 30 MT) with automatic percentage and balance tracking.
- Role-restricted multi-tier authorization workflow (`Draft` $\rightarrow$ `Pending Approval` $\rightarrow$ `Approved`) with auto-submission upon manager approval.
- Intercompany document mapping: Automatically converting Ecofinit's Sales Invoice into Metal Green's Purchase Invoice.
- Real-time perpetual inventory updates, warehouse-level Stock Ledgers, and internal Material Transfers.

### Question 2: What did you customize?
1. **Created a Custom Frappe App (`intercompany_tracker`)**: Packaged under `apps/intercompany_tracker` with dedicated hooks, tests, and module definitions.
2. **Created a Custom Script Report (`Intercompany Transaction Tracker`)**: A cross-company financial and inventory visibility report built with Python (`.py`), client formatting (`.js`), and schema definition (`.json`).
3. **Workflow Configuration**: Standard Frappe Workflow records (`Sales Order Approval`, custom states, role transitions).

### Question 3: Why was each customization necessary?
- Standard ERPNext reports are strictly siloed by company. A user viewing the Sales Invoice register in Ecofinit Dubai cannot see whether the corresponding Purchase Invoice in Metal Green has been generated, submitted, or received into inventory without manually logging out or switching company sessions.
- The `Intercompany Transaction Tracker` bridges this gap: it extracts the bi-directional intercompany reference (`inter_company_invoice_reference`), queries live inventory bin balances across Saudi warehouses, and displays the complete end-to-end transaction state in a single pane of glass.
- Placing this in a custom app ensures clean separation of concerns, zero core code modification, and complete portability across environments.

### Question 4: What would you change or improve before deploying this solution to production?
1. **Automated Intercompany Reconciliation**: Implement a background job (`hooks.py` scheduler) that automatically reconciles outstanding intercompany receivables and payables and alerts the finance team of any pricing or quantity discrepancies.
2. **Automated Currency Revaluation**: Schedule the native `Currency Exchange Revaluation` tool at each month-end to unrealized foreign exchange gains or losses on foreign currency party accounts.
3. **Enhanced Validation Hooks**: Introduce an event hook on `Sales Invoice.validate` ensuring that intercompany selling rates never fall below the original procurement cost from external suppliers, protecting gross margins.
4. **Granular Role Hierarchy**: Create specific corporate roles (`Ecofinit Commercial Approver`, `Metal Green Plant Manager`) rather than relying on generic manager roles.
5. **CI/CD Integration**: Connect GitHub Actions to run automated linter (`ruff`), unit tests, and bench migration tests on pull requests before deployment to staging/production benches.

### Question 5: How would you approach Saudi VAT and ZATCA e-invoicing integration for Metal Green at a later stage?
Saudi Arabia mandates strict e-invoicing compliance under ZATCA (Zakat, Tax and Customs Authority). The integration would be structured in two phases:

1. **Phase 1 (Generation Phase - Already Supported)**:
   - Install the regional Saudi compliance app (`erpnext_ksa` / `ksa_vat`).
   - Configure company tax registration details: VAT Registration Number (15 digits), Company Address in Arabic, and VAT Accounts.
   - Use standard ERPNext KSA Print Formats containing the encrypted TLV (Tag-Length-Value) Base64-encoded QR code containing seller name, VAT number, timestamp, total with VAT, and VAT amount.

2. **Phase 2 (Integration Phase - Advanced API Clearance/Reporting)**:
   - **Device Onboarding & Cryptographic Stamp**: Register the ERPNext deployment with ZATCA's Fatoora portal using the Cryptographic Stamp Identifier (CSID) and Compliance CSID.
   - **XML UBL 2.1 Generation**: For every B2B invoice, ERPNext automatically generates the standardized UBL 2.1 XML document, hashes it using SHA-256, signs it with the digital private key, and generates the cryptographic invoice counter value (PIH - Previous Invoice Hash).
   - **Direct API Submission**:
     - **B2B (Standard Tax Invoices)**: Sent via ZATCA API for **Clearance** before sending to the customer; ZATCA returns a cleared XML with digital signature.
     - **B2C (Simplified Invoices)**: Issued immediately with QR code and reported to ZATCA within 24 hours (**Reporting** API).
   - This entire logic is handled by standard regional Frappe extensions, requiring **zero modifications to our custom `intercompany_tracker` app**.

### Question 6: How would you structure upgrades so that ERPNext/Frappe version updates do not break your customizations?
1. **Zero Core Code Modifications**: Never touch a single line of code in `apps/frappe` or `apps/erpnext`. All custom logic resides strictly within `apps/intercompany_tracker`.
2. **Hook-Based Architecture**: Use official Frappe extension points declared in `hooks.py`:
   - `doc_events` for trigger validation.
   - `override_doctype_class` for extending controller logic using Python inheritance (`super()`).
3. **Fixtures Management**: Export all custom fields, workflows, and property setters into JSON fixtures using `bench export-fixtures`. When `bench migrate` runs during a version upgrade, Frappe automatically reapplies customizations cleanly on top of new database schemas.
4. **Semantic Versioning & Branch Strategy**:
   - Maintain `version-15` branch for current production and a `develop` / `version-16` staging branch for testing upcoming Frappe releases.
5. **Automated Upgrade Testing**: Maintain staging environments where upgrades are rehearsed (`bench update --patch`) against sanitized production database backups before updating production.

### Question 7: How would you handle permissions and company-level data isolation in a larger three-company implementation?
In an enterprise multi-company deployment (e.g. adding a 3rd entity like an Indian processing facility or US trading arm):

1. **Frappe User Permissions (Strict Tenant Isolation)**:
   - Create `User Permission` records linking each user to their specific `Company` document (e.g. User A has permission only for `Company == Metal Green Saudi Arabia`).
   - Once set, Frappe's ORM automatically injects `WHERE company = 'Metal Green Saudi Arabia'` into every single database query across all doctypes (Invoices, Orders, Stock, GL Entries), completely blinding users to transactions of sister companies.
2. **Central Shared Masters vs Entity-Specific Masters**:
   - **Shared Universally**: Item Masters (`Aluminium Dross`), UOMs, Currencies.
   - **Entity-Specific**: Warehouses, Chart of Accounts, Bank Accounts, Cost Centers, Tax Templates.
3. **Role-Based Document Access**:
   - Local operational roles (`Plant Operator - MGSA`, `Procurement Specialist - ED`).
   - Corporate auditing roles (`Group Financial Controller`) who hold read-only permissions across all 3 companies with access to the `Intercompany Transaction Tracker`.
4. **Intercompany Clearing Automation**:
   - Internal Customer/Supplier pairs restricted to specific intercompany transaction roles, ensuring unauthorized staff cannot trigger cross-company liability entries.

---
---

## License
MIT License. Developed for technical evaluation purposes.
