import json

with open('/home/user/test_dit/68954780-562f-11ef-9bdd-d16a1a78a50c.json', 'r') as f:
    data = json.load(f)

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

# --- 1) Per-type: what prop keys actually appear (excluding cssStyle) ---
print("=== PROP KEYS PER TYPE ===")
type_keys = {}
for e in all_elements:
    t = e['type']
    if t not in type_keys:
        type_keys[t] = set()
    for k in e['props']:
        if k != 'cssStyle':
            type_keys[t].add(k)

for t in sorted(type_keys):
    print(f"  {t}: {sorted(type_keys[t])}")

# --- 2) Sample 3 full prop dicts (minus cssStyle) for every type that has text-like keys ---
print()
print("=== SAMPLE PROPS FOR TEXT-BEARING TYPES ===")
text_keys = {'text','label','title','placeholder','options','value','items',
             'content','name','description','caption','heading','msg','message',
             'html','data','config','source','columns','rows','fields'}
shown = {}
for e in all_elements:
    t = e['type']
    if shown.get(t, 0) >= 3:
        continue
    props_clean = {k:v for k,v in e['props'].items() if k != 'cssStyle'}
    if set(props_clean.keys()) & text_keys:
        print(f"\n  [{t}] id={e['id']}")
        for k,v in props_clean.items():
            print(f"      {k}: {str(v)[:300]}")
        shown[t] = shown.get(t, 0) + 1

# --- 3) Dump ALL props (no filter) for every ElemText (first 10) ---
print()
print("=== FIRST 10 ElemText FULL PROPS ===")
count = 0
for e in all_elements:
    if e['type'] == 'ElemText' and count < 10:
        print(f"\n  id={e['id']}  depth={e['depth']}")
        for k,v in e['props'].items():
            print(f"      {k}: {str(v)[:300]}")
        count += 1

# --- 4) Dump ALL props for first 5 of each "interesting" widget type ---
interesting = ['ElemDremioTable','ElemDropdown','ElemSmartGallery','ElemButton',
               'PerformanceManagement/ElemStandardFilter','PerformanceManagement/ElemMultiSpline',
               'PerformanceManagement/ElemMultiKpi','5INSIGHT/ElemChartFilterMed',
               'Table/ElemHeader','PerformanceManagement/ElemHouse',
               'PerformanceManagement/ElemDotMap','PerformanceManagement/ElemPieChartDremio',
               'PerformanceManagement/ElemCnpXlsxBtn','ElemEventStack',
               'ElemLayersContainer','basic::ElemGridLayout','ElemTile']
print()
print("=== SAMPLE PROPS FOR INTERESTING WIDGET TYPES ===")
for itype in interesting:
    count = 0
    for e in all_elements:
        if e['type'] == itype and count < 3:
            props_clean = {k:v for k,v in e['props'].items() if k != 'cssStyle'}
            print(f"\n  [{itype}] id={e['id']}  depth={e['depth']}")
            for k,v in props_clean.items():
                print(f"      {k}: {str(v)[:300]}")
            count += 1
