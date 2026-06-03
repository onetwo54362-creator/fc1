import re

with open('page_auth.html', 'r', encoding='utf-8') as f:
    text = f.read()
    
# Let's search for just "DTSG" and print the context
matches = [m.start() for m in re.finditer(r'DTSG', text, re.IGNORECASE)]
print(f"Found {len(matches)} occurrences of DTSG")

for pos in matches[:5]:
    start = max(0, pos - 50)
    end = min(len(text), pos + 100)
    print(f"\n--- Context ---")
    print(text[start:end])
