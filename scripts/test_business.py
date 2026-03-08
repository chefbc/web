import sys
import re
from pathlib import Path
from markdown import Markdown

# Add the project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from business_plugin.plugin import BusinessExtension

def strip_schema(html):
    """Strip the JSON-LD schema script block from the HTML."""
    return re.sub(r'<script type="application/ld\+json">.*?</script>', '', html, flags=re.DOTALL).strip()

def test_shortcodes():
    test_cases = [
        # Default location (main_office)
        ("{% business 'name' %}", "Zensical Main Office"),
        ("{% business 'email' %}", "hello@zensical.org"),
        ("{% business 'phone' %}", "+1 (555) 123-4567"),
        ("{% business 'address' %}", "123 Innovation Way, San Francisco, CA 94105, USA"),
        ("{% business 'hours' %}", "Monday-Friday: 09:00-17:00<br>Saturday: 10:00-14:00"),
        
        # Specific location (branch_office)
        ("{% business 'branch_office' 'name' %}", "Zensical East"),
        ("{% business 'branch_office' 'phone' %}", "+1 (555) 987-6543"),
        ("{% business 'branch_office' 'address' %}", "456 Atlantic Ave, New York, NY 10001, USA"),
        
        # Missing fields/locations
        ("{% business 'non_existent' 'name' %}", "<!-- Business location 'non_existent' not found -->"),
        ("{% business 'main_office' 'fax' %}", "<!-- Field 'fax' not found in location 'main_office' -->"),
    ]
    
    for input_str, expected_output in test_cases:
        # Create a new Markdown instance for each test to avoid schema_injected state carryover
        md = Markdown(extensions=[BusinessExtension()])
        output = md.convert(input_str).strip()
        output = strip_schema(output)
        
        # Markdown might wrap in <p> tags
        if output.startswith("<p>") and output.endswith("</p>"):
            output = output[3:-4].strip()
            
        if output == expected_output:
            print(f"PASS: {input_str} -> {output}")
        else:
            print(f"FAIL: {input_str}")
            print(f"  Expected: {expected_output}")
            print(f"  Got:      {output}")

def test_google_maps():
    md = Markdown(extensions=[BusinessExtension()])
    output = md.convert("{% business 'map' %}").strip()
    if 'google.com/maps/embed' in output and '!1m18!1m12!1m3!1d3153.01912' in output:
        print("PASS: Google Maps iframe generated correctly.")
    else:
        print("FAIL: Google Maps iframe generation failed.")
        print(f"  Got: {output}")

def test_schema_injection():
    md = Markdown(extensions=[BusinessExtension()])
    output = md.convert("Some content").strip()
    if 'application/ld+json' in output and '"@type": "LocalBusiness"' in output:
        print("PASS: Schema.org JSON-LD injected correctly.")
    else:
        print("FAIL: Schema.org JSON-LD injection failed.")

if __name__ == "__main__":
    test_shortcodes()
    test_google_maps()
    test_schema_injection()
