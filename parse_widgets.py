import json

with open('/home/user/test_dit/68954780-562f-11ef-9bdd-d16a1a78a50c.json', 'r') as f:
    data = json.load(f)

# Recursively walk the tree and collect all elements
all_elements = []

def walk(node, depth=0):
    elem = {
        'id': node.get('id'),
        'pid': node.get('pid'),
        'type': node.get('type'),
        'props': node.get('props', {}),
        'visible': node.get('visible'),
        'depth': depth,
    }
    all_elements.append(elem)
    for child in node.get('children', []):
        walk(child, depth+1)

for root in data:
    walk(root)

# Print summary
print(f"Total elements: {len(all_elements)}")
print()

# Unique types
types = {}
for e in all_elements:
    t = e['type']
    types[t] = types.get(t, 0) + 1
print("=== UNIQUE TYPES ===")
for t, c in sorted(types.items(), key=lambda x: -x[1]):
    print(f"  {t}: {c}")

print()
print("=== ALL TEXT CONTENT (ElemText, ElemDropdown, etc.) ===")
for e in all_elements:
    props = e['props']
    # collect any textual content
    texts = []
    if 'text' in props:
        texts.append(('text', props['text']))
    if 'label' in props:
        texts.append(('label', props['label']))
    if 'title' in props:
        texts.append(('title', props['title']))
    if 'placeholder' in props:
        texts.append(('placeholder', props['placeholder']))
    if 'options' in props:
        texts.append(('options', props['options']))
    if 'value' in props:
        texts.append(('value', props['value']))
    if 'items' in props:
        texts.append(('items', props['items']))
    if texts:
        print(f"  [{e['type']}] id={e['id'][:20]}... depth={e['depth']}")
        for k, v in texts:
            print(f"      {k}: {str(v)[:200]}")

print()
print("=== WIDGET-LIKE CONTAINERS (depth 1-3) ===")
for e in all_elements:
    if e['depth'] <= 3:
        props = e['props']
        print(f"  depth={e['depth']} type={e['type']} id={e['id'][:24]}...")
        # print non-css props
        for k,v in props.items():
            if k != 'cssStyle':
                print(f"      {k}: {str(v)[:150]}")
