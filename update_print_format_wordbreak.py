#!/usr/bin/env python3
import frappe

def update_print_format():
    # Read the updated HTML with word-break fix
    with open('/tmp/compact_print_format.html', 'r') as f:
        html = f.read()

    # Update the CSS to add word-break properties
    html = html.replace(
        '''/* Notes */
.plain-box{
  background:#fafafa!important; border:1px solid #ddd!important;
  border-radius:4px!important;
  padding:4px!important; font-size:8px!important; line-height:1.4!important;
}''',
        '''/* Notes */
.plain-box{
  background:#fafafa!important; border:1px solid #ddd!important;
  border-radius:4px!important;
  padding:4px!important; font-size:8px!important; line-height:1.4!important;
  word-wrap:break-word!important; word-break:break-word!important;
  overflow-wrap:break-word!important; max-width:100%!important;
}'''
    )

    # Get the print format
    pf = frappe.get_doc('Print Format', 'FM-EN-04')
    pf.html = html
    pf.save()

    frappe.db.commit()
    print('✓ Updated FM-EN-04 print format with word-break fix for text overflow')

if __name__ == "__main__":
    update_print_format()
