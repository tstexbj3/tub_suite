#!/usr/bin/env python3
"""
Pre-deployment validation script for v2.1.0

Run this script BEFORE deploying to production to check if the site is ready.

Usage:
    bench --site tub.x-desk.tech execute tub_suite.scripts.pre_deployment_check.run_checks
"""

import frappe


def run_checks():
    """
    Run all pre-deployment checks and report status
    """
    print("\n" + "="*70)
    print("TUB Suite v2.1.0 - Pre-Deployment Validation")
    print("="*70 + "\n")

    checks = [
        check_site_info,
        check_existing_repairs,
        check_assets,
        check_users_roles,
        check_disk_space,
        check_database_size,
    ]

    results = []
    for check_func in checks:
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            results.append({
                "check": check_func.__name__,
                "status": "ERROR",
                "message": str(e)
            })

    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    passed = sum(1 for r in results if r["status"] == "PASS")
    warnings = sum(1 for r in results if r["status"] == "WARN")
    errors = sum(1 for r in results if r["status"] == "ERROR")

    for result in results:
        icon = "✓" if result["status"] == "PASS" else "⚠" if result["status"] == "WARN" else "✗"
        print(f"{icon} {result['check']}: {result['message']}")

    print(f"\nTotal: {len(results)} | Passed: {passed} | Warnings: {warnings} | Errors: {errors}")

    if errors > 0:
        print("\n❌ DEPLOYMENT NOT RECOMMENDED - Fix errors first")
        return False
    elif warnings > 0:
        print("\n⚠️  DEPLOYMENT POSSIBLE - Review warnings")
        return True
    else:
        print("\n✅ READY FOR DEPLOYMENT")
        return True


def check_site_info():
    """Check basic site information"""
    site = frappe.local.site
    return {
        "check": "Site Info",
        "status": "PASS",
        "message": f"Site: {site}"
    }


def check_existing_repairs():
    """Check existing Asset Repair documents"""
    count = frappe.db.count("Asset Repair")
    submitted_count = frappe.db.count("Asset Repair", {"docstatus": 1})

    return {
        "check": "Existing Repairs",
        "status": "PASS",
        "message": f"Found {count} repairs ({submitted_count} submitted)"
    }


def check_assets():
    """Check Asset documents"""
    count = frappe.db.count("Asset")
    maintenance_count = frappe.db.count("Asset Maintenance")

    return {
        "check": "Assets",
        "status": "PASS",
        "message": f"Found {count} assets with {maintenance_count} maintenance schedules"
    }


def check_users_roles():
    """Check user roles"""
    roles_to_check = [
        "Maintenance User",
        "Maintenance Manager",
        "Engineering Team"
    ]

    results = []
    for role in roles_to_check:
        count = frappe.db.count("Has Role", {"role": role})
        results.append(f"{role}: {count} users")

    status = "PASS" if all(frappe.db.count("Has Role", {"role": r}) > 0 for r in roles_to_check) else "WARN"
    message = ", ".join(results)

    return {
        "check": "User Roles",
        "status": status,
        "message": message
    }


def check_disk_space():
    """Check available disk space"""
    import shutil

    try:
        stat = shutil.disk_usage("/")
        free_gb = stat.free / (1024**3)
        total_gb = stat.total / (1024**3)
        percent_free = (stat.free / stat.total) * 100

        status = "PASS" if free_gb > 5 else "WARN" if free_gb > 2 else "ERROR"
        message = f"{free_gb:.1f}GB free of {total_gb:.1f}GB ({percent_free:.1f}%)"

        return {
            "check": "Disk Space",
            "status": status,
            "message": message
        }
    except Exception as e:
        return {
            "check": "Disk Space",
            "status": "WARN",
            "message": f"Could not check: {str(e)}"
        }


def check_database_size():
    """Check database size"""
    try:
        result = frappe.db.sql("""
            SELECT
                table_schema AS 'Database',
                ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
            FROM information_schema.TABLES
            WHERE table_schema = %s
            GROUP BY table_schema
        """, (frappe.conf.db_name,), as_dict=True)

        if result:
            size_mb = result[0].get("Size (MB)", 0)
            status = "PASS"
            message = f"Database size: {size_mb}MB"
        else:
            status = "WARN"
            message = "Could not determine database size"

        return {
            "check": "Database Size",
            "status": status,
            "message": message
        }
    except Exception as e:
        return {
            "check": "Database Size",
            "status": "WARN",
            "message": f"Could not check: {str(e)}"
        }


if __name__ == "__main__":
    run_checks()
