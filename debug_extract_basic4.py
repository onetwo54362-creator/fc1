import re
import json

with open("test_page.html", "r", encoding="utf-8") as f:
    html = f.read()

out = []

m = re.search(r'"author":\{[^}]*?"name":"([^"]+)"', html)
out.append("author: " + (m.group(1) if m else "None"))

m2 = re.search(r'"actors":\[\{[^}]*?"name":"([^"]+)"', html)
out.append("actors: " + (m2.group(1) if m2 else "None"))

# Another common one: "owning_profile"
m3 = re.search(r'"owning_profile":\{[^}]*?"name":"([^"]+)"', html)
out.append("owning_profile: " + (m3.group(1) if m3 else "None"))

# title fallback
m4 = re.search(r'<title>(.*?)</title>', html)
out.append("title: " + (m4.group(1) if m4 else "None"))

# Let's search for ABS-CBN News (the author of the test post)
abs_cbn_matches = re.finditer(r'\{[^}]*"name":"ABS-CBN News"[^}]*\}', html)
for i, x in enumerate(abs_cbn_matches):
    if i > 2: break
    out.append("ABS-CBN context: " + x.group(0))

with open("debug_out.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))

