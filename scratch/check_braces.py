import re

with open('build_portal.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern for single { or } that are not placeholders (like {series_name})
# This is tricky in Python itself.
# Let's just look for any { that isn't {{ and isn't followed by a valid placeholder name + }

placeholders = ["series_name", "series_slug", "primary_color", "primary_rgb", "accent_color", "accent_rgb", "bg_color", "hover_color", "bg_img", "hero_desc", "nav_links", "chapters_html", "global_node_list", "ga_id", "footer_links", "favicon", "kinetic_header", "chapter_name", "chapter_id", "first_img", "images_html", "all_chapters_options", "current_url", "series_file"]

def check_braces(text, var_name):
    # Find the string content of the variable
    match = re.search(f'{var_name} = """(.*?)"""', text, re.DOTALL)
    if not match: return
    val = match.group(1)
    
    # Check for single {
    singles_open = re.findall(r'(?<!\{)\{(?!\{)', val)
    for s in singles_open:
        # Check if it's a placeholder
        is_placeholder = False
        for p in placeholders:
            if val.find('{' + p + '}') != -1: # very naive
                pass
        # Better: find all {xxx} and see if xxx in placeholders
        found_placeholders = re.findall(r'\{([a-zA-Z0-9_]+)\}', val)
        for fp in found_placeholders:
            if fp not in placeholders:
                print(f"Potential single brace in {var_name}: {{{fp}}}")
        
    # Check for single }
    singles_close = re.findall(r'(?<!\})\}(?!\})', val)
    if singles_close:
        print(f"Found {len(singles_close)} potential single closing braces in {var_name}")

print("Checking templates...")
check_braces(content, "KINETIC_HEADER_JS")
check_braces(content, "READER_TEMPLATE_HTML")
check_braces(content, "HTML_TEMPLATE")
