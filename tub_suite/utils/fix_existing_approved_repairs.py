#!/usr/bin/env python3
"""
Fix asset status for repairs that were Approved before the v2.0.1 fix
Run: bench --site tub execute tub_suite.utils.fix_existing_approved_repairs.fix_approved_repairs
"""

import frappe

def fix_approved_repairs():
    """
    Find all Approved Major repairs and update asset status to Out of Order
    This is a one-time fix for repairs approved before v2.0.1
    """

    print("\n" + "="*80)
    print("FIXING EXISTING APPROVED REPAIRS")
    print("="*80)

    # Find all Approved Major repairs that haven't been Finished
    approved_major = frappe.get_all("Asset Repair",
        filters={
            "workflow_state": "Approved",
            "issue_severity": "Major - Asset Must Stop"
        },
        fields=["name", "asset", "asset_name", "description", "workflow_state"]
    )

    print(f"\nFound {len(approved_major)} Approved Major repairs\n")

    fixed_count = 0

    for repair in approved_major:
        print(f"Repair: {repair.name}")
        print(f"  Asset: {repair.asset} ({repair.asset_name})")
        print(f"  State: {repair.workflow_state}")

        # Get asset
        asset_doc = frappe.get_doc("Asset", repair.asset)
        current_status = asset_doc.status

        print(f"  Current asset status: {current_status}")

        if current_status != "Out of Order":
            # Fix asset status
            asset_doc.status = "Out of Order"
            asset_doc.add_comment("Comment",
                f"Asset marked Out of Order (retroactive fix for v2.0.1) - Manager approved Major repair: {repair.description}")
            asset_doc.save(ignore_permissions=True)

            print(f"  ✅ FIXED: Asset now Out of Order")
            fixed_count += 1
        else:
            print(f"  ✓ Already Out of Order")

        print()

    print("="*80)
    print(f"FIXED {fixed_count} assets")
    print("="*80 + "\n")

    return {
        "total_repairs": len(approved_major),
        "fixed_assets": fixed_count
    }
