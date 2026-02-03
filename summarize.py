import json

with open('/home/user/test_dit/68954780-562f-11ef-9bdd-d16a1a78a50c.json', 'r') as f:
    data = json.load(f)

all_elements = []
def walk(node, depth=0):
    all_elements.append({'id': node.get('id'), 'type': node.get('type'),
                         'props': node.get('props', {}), 'depth': depth})
    for child in node.get('children', []):
        walk(child, depth+1)
for root in data:
    walk(root)

def extract_dremio(props):
    d = props.get('dremio')
    if d is None: return []
    if isinstance(d, dict): return [d]
    if isinstance(d, list): return d
    return []

# ===================================================================
# A) Deduplicated data-source catalogue: $from -> union of all $fields
# ===================================================================
source_fields = {}   # $from-tuple -> set of field names
source_users  = {}   # $from-tuple -> list of (type, purpose-hint)

for e in all_elements:
    all_dremios = extract_dremio(e['props'])
    ad = e['props'].get('additionalDremio')
    if ad:
        if isinstance(ad, dict): all_dremios.append(ad)
        elif isinstance(ad, list): all_dremios.extend(ad)

    for dr in all_dremios:
        q = dr.get('query', {})
        frm = tuple(q.get('$from', []))
        if not frm: continue
        fields = q.get('$fields', {})
        if frm not in source_fields:
            source_fields[frm] = set()
            source_users[frm] = []
        if isinstance(fields, dict):
            source_fields[frm].update(fields.keys())
        # record who uses it
        source_users[frm].append(e['type'])

print("=" * 80)
print("A) DEDUPLICATED DATA SOURCES  (table_name -> all fields ever queried)")
print("=" * 80)
for frm in sorted(source_fields.keys(), key=lambda x: x[0] if x else ''):
    users = list(set(source_users[frm]))
    print(f"\n  SOURCE: {'.'.join(frm)}")
    print(f"  USED BY: {users}")
    print(f"  FIELDS:  {sorted(source_fields[frm])}")

# ===================================================================
# B) All visible column titles across all ElemDremioTable (deduplicated)
# ===================================================================
print("\n" + "=" * 80)
print("B) ALL VISIBLE TABLE COLUMN TITLES (from ElemDremioTable .columns[].title)")
print("   grouped by $from source")
print("=" * 80)
source_titles = {}
for e in all_elements:
    if e['type'] != 'ElemDremioTable': continue
    cols = e['props'].get('columns', [])
    frm = None
    for dr in extract_dremio(e['props']):
        frm = tuple(dr.get('query', {}).get('$from', []))
        break
    if frm not in source_titles:
        source_titles[frm] = set()
    for col in cols:
        t = col.get('title', '').strip()
        if t:
            source_titles[frm].add(t)
        # also collect sort field as it often is the real column name
        s = col.get('sort', '')
        if s:
            source_titles[frm].add(f"[sort:{s}]")

for frm in sorted(source_titles.keys(), key=lambda x: str(x)):
    print(f"\n  {'.'.join(frm) if frm else 'UNKNOWN'}:")
    for t in sorted(source_titles[frm]):
        print(f"      {t}")

# ===================================================================
# C) All Table/ElemHeader dataFields (deduplicated)
# ===================================================================
print("\n" + "=" * 80)
print("C) Table/ElemHeader dataField values (sortable column names)")
print("=" * 80)
hdr_fields = set()
for e in all_elements:
    if e['type'] == 'Table/ElemHeader':
        df = e['props'].get('dataField', '')
        if df: hdr_fields.add(df)
print(f"  {sorted(hdr_fields)}")

# ===================================================================
# D) All ElemStandardFilter: dimension + placeholder (deduplicated)
# ===================================================================
print("\n" + "=" * 80)
print("D) FILTER WIDGETS  (dimension field + placeholder label + source)")
print("=" * 80)
seen_filters = set()
for e in all_elements:
    if e['type'] != 'PerformanceManagement/ElemStandardFilter': continue
    dim = e['props'].get('selectedDimension', '')
    ph  = e['props'].get('textPlaceholder', '')
    frm = None
    for dr in extract_dremio(e['props']):
        frm = tuple(dr.get('query', {}).get('$from', []))
        break
    key = (dim, ph, frm)
    if key in seen_filters: continue
    seen_filters.add(key)
    print(f"  dimension={dim!r:20s}  placeholder={ph!r:15s}  source={'.'.join(frm) if frm else 'none'}")

# ===================================================================
# E) All ElemText labels (deduplicated, stripped)
# ===================================================================
import re
print("\n" + "=" * 80)
print("E) ALL UI LABELS (ElemText .html, deduplicated & tag-stripped)")
print("=" * 80)
labels = set()
for e in all_elements:
    if e['type'] == 'ElemText':
        h = e['props'].get('html', '')
        if h:
            clean = re.sub(r'<[^>]+>', '', h).strip()
            if clean:
                labels.add(clean)
for l in sorted(labels):
    print(f"  {l}")

# ===================================================================
# F) ChartFilterMed dimensions (deduplicated)
# ===================================================================
print("\n" + "=" * 80)
print("F) CHART-FILTER DIMENSIONS (5INSIGHT/ElemChartFilterMed)")
print("=" * 80)
seen_cf = set()
for e in all_elements:
    if e['type'] != '5INSIGHT/ElemChartFilterMed': continue
    dim = e['props'].get('dimension')
    tp  = e['props'].get('type')
    frm = None
    for dr in extract_dremio(e['props']):
        frm = tuple(dr.get('query', {}).get('$from', []))
        break
    key = (dim, tp, frm)
    if key in seen_cf: continue
    seen_cf.add(key)
    flds = set()
    for dr in extract_dremio(e['props']):
        f = dr.get('query', {}).get('$fields', {})
        if isinstance(f, dict): flds.update(f.keys())
    print(f"  dimension={dim!r:25s}  type={tp!r:15s}  source={'.'.join(frm) if frm else 'none'}")
    print(f"      fields: {sorted(flds)}")

# ===================================================================
# G) MultiKpi metric/dimension pairs (deduplicated)
# ===================================================================
print("\n" + "=" * 80)
print("G) KPI WIDGETS  (metric + dimension + prefix + source)")
print("=" * 80)
seen_kpi = set()
for e in all_elements:
    if e['type'] != 'PerformanceManagement/ElemMultiKpi': continue
    sm = e['props'].get('selectedMetric')
    sd = e['props'].get('selectedDimension')
    pf = e['props'].get('preFix')
    tp = e['props'].get('type')
    frm = None
    for dr in extract_dremio(e['props']):
        frm = tuple(dr.get('query', {}).get('$from', []))
        break
    key = (sm, sd, pf, tp, frm)
    if key in seen_kpi: continue
    seen_kpi.add(key)
    print(f"  metric={sm!r:25s}  dim={sd!r:25s}  prefix={pf!r:15s}  type={tp!r:12s}  src={'.'.join(frm) if frm else 'none'}")

# ===================================================================
# H) MultiSpline metric/dimension pairs (deduplicated)
# ===================================================================
print("\n" + "=" * 80)
print("H) SPLINE CHARTS  (metricNames + dimensionOptions + source)")
print("=" * 80)
seen_sp = set()
for e in all_elements:
    if e['type'] != 'PerformanceManagement/ElemMultiSpline': continue
    mn = str(e['props'].get('metricNames'))
    do = str(e['props'].get('dimensionOptions'))
    frm = None
    for dr in extract_dremio(e['props']):
        frm = tuple(dr.get('query', {}).get('$from', []))
        break
    key = (mn, do, frm)
    if key in seen_sp: continue
    seen_sp.add(key)
    print(f"  metricNames:      {e['props'].get('metricNames')}")
    print(f"  dimensionOptions: {e['props'].get('dimensionOptions')}")
    print(f"  source:           {'.'.join(frm) if frm else 'none'}")
    flds = set()
    for dr in extract_dremio(e['props']):
        f = dr.get('query', {}).get('$fields', {})
        if isinstance(f, dict): flds.update(f.keys())
    print(f"  fields:           {sorted(flds)}")
    print()

# ===================================================================
# I) PieChart configs (deduplicated)
# ===================================================================
print("=" * 80)
print("I) PIE / DONUT CHARTS  (dimension + metrics + colorSet + source)")
print("=" * 80)
seen_pie = set()
for e in all_elements:
    if e['type'] != 'PerformanceManagement/ElemPieChartDremio': continue
    sd = e['props'].get('selectedDimension')
    cs = str(e['props'].get('colorSet'))
    frm = None
    for dr in extract_dremio(e['props']):
        frm = tuple(dr.get('query', {}).get('$from', []))
        break
    key = (sd, frm)
    if key in seen_pie: continue
    seen_pie.add(key)
    print(f"  dimension: {sd}")
    print(f"  colorSet:  {e['props'].get('colorSet')}")
    print(f"  source:    {'.'.join(frm) if frm else 'none'}")
    flds = set()
    for dr in extract_dremio(e['props']):
        f = dr.get('query', {}).get('$fields', {})
        if isinstance(f, dict): flds.update(f.keys())
    print(f"  fields:    {sorted(flds)}")
    print()

# ===================================================================
# J) DotMap geo-sources (deduplicated)
# ===================================================================
print("=" * 80)
print("J) GEO / DOT-MAP SOURCES  (geojson files + dremio sources)")
print("=" * 80)
seen_geo = set()
for e in all_elements:
    if e['type'] != 'PerformanceManagement/ElemDotMap': continue
    layers = e['props'].get('layerSettings', [])
    geo_files = []
    for layer_group in layers:
        if isinstance(layer_group, list):
            for layer in layer_group:
                gj = layer.get('geoJson', {})
                for f in gj.get('files', []):
                    geo_files.append(f.get('url', ''))
    frms = set()
    for dr in extract_dremio(e['props']):
        frm = tuple(dr.get('query', {}).get('$from', []))
        if frm: frms.add(frm)
    ad = e['props'].get('additionalDremio')
    if ad:
        ads = [ad] if isinstance(ad, dict) else ad
        for d in ads:
            frm = tuple(d.get('query', {}).get('$from', []))
            if frm: frms.add(frm)
    key = (tuple(geo_files), tuple(sorted(frms)))
    if key in seen_geo: continue
    seen_geo.add(key)
    print(f"  geojson files: {geo_files}")
    print(f"  dremio sources: {['.'.join(f) for f in frms]}")
    print()

# ===================================================================
# K) ElemHouse navigation configs
# ===================================================================
print("=" * 80)
print("K) NAVIGATION / HOUSE WIDGETS")
print("=" * 80)
seen_house = set()
for e in all_elements:
    if e['type'] != 'PerformanceManagement/ElemHouse': continue
    wt = e['props'].get('workType')
    frm = None
    for dr in extract_dremio(e['props']):
        frm = tuple(dr.get('query', {}).get('$from', []))
        break
    key = (wt, frm)
    if key in seen_house: continue
    seen_house.add(key)
    print(f"  workType: {wt}   source: {'.'.join(frm) if frm else 'none'}")
    flds = set()
    for dr in extract_dremio(e['props']):
        f = dr.get('query', {}).get('$fields', {})
        if isinstance(f, dict): flds.update(f.keys())
    print(f"  fields:   {sorted(flds)}")
    print()

# ===================================================================
# L) xlsx export field mappings (CnpXlsxBtn) - deduplicated
# ===================================================================
print("=" * 80)
print("L) XLSX EXPORT DEFINITIONS  (datasetMapped columns + titles)")
print("=" * 80)
seen_xlsx = set()
for e in all_elements:
    if e['type'] != 'PerformanceManagement/ElemCnpXlsxBtn': continue
    dm = str(e['props'].get('datasetMapped'))
    if dm in seen_xlsx: continue
    seen_xlsx.add(dm)
    print(f"  bookName:       {e['props'].get('downloadXLSX', {}).get('bookName') if isinstance(e['props'].get('downloadXLSX'), dict) else ''}")
    print(f"  datasetMapped:  {e['props'].get('datasetMapped')}")
    print(f"  datasetTitles:  {e['props'].get('datasetTitles')}")
    print(f"  excluded:       {e['props'].get('excludedDataFields')}")
    frm = None
    for dr in extract_dremio(e['props']):
        frm = tuple(dr.get('query', {}).get('$from', []))
        break
    print(f"  source:         {'.'.join(frm) if frm else 'none'}")
    print()
