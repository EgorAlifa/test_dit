import json, re

with open('/home/user/test_dit/68954780-562f-11ef-9bdd-d16a1a78a50c.json', 'r') as f:
    data = json.load(f)

all_elements = []
def walk(node, depth=0, path="root"):
    elem = {
        'id': node.get('id'),
        'type': node.get('type'),
        'props': node.get('props', {}),
        'depth': depth,
        'path': path,
    }
    all_elements.append(elem)
    for i, child in enumerate(node.get('children', [])):
        walk(child, depth+1, path + f"/{child.get('type','?')}")

for root in data:
    walk(root)

# ============================================================
# 1) ALL dremio queries: extract $from, $fields, $dimensions, $metrics, $filters
# ============================================================
print("=" * 70)
print("1) ALL DREMIO DATA SOURCES ($from tables + fields)")
print("=" * 70)

def extract_dremio(props):
    """Pull dremio config - may be dict or list of dicts"""
    d = props.get('dremio')
    if d is None:
        return []
    if isinstance(d, dict):
        return [d]
    if isinstance(d, list):
        return d
    return []

seen_queries = set()
for e in all_elements:
    dremios = extract_dremio(e['props'])
    # also check additionalDremio
    ad = e['props'].get('additionalDremio')
    if ad:
        if isinstance(ad, dict): dremios.append(ad)
        elif isinstance(ad, list): dremios.extend(ad)

    for dr in dremios:
        q = dr.get('query', {})
        frm = q.get('$from', [])
        fields = q.get('$fields', {})
        dims = q.get('$dimensions', [])
        metrics = q.get('$metrics', [])
        filters = q.get('$filters', [])
        key = (e['type'], str(frm), str(sorted(fields.keys()) if isinstance(fields, dict) else fields))
        if key in seen_queries:
            continue
        seen_queries.add(key)
        print(f"\n  [{e['type']}] id={e['id']}")
        print(f"      $from:       {frm}")
        if isinstance(fields, dict):
            print(f"      $fields:     {sorted(fields.keys())}")
        else:
            print(f"      $fields:     {fields}")
        # dimensions - extract field names
        dim_names = []
        for d in dims:
            if isinstance(d, dict):
                dim_names.extend(d.keys())
            elif isinstance(d, str):
                dim_names.append(d)
        print(f"      $dimensions: {dim_names}")
        # metrics - extract field names
        met_names = []
        for m in metrics:
            if isinstance(m, dict):
                met_names.extend(m.keys())
            elif isinstance(m, str):
                met_names.append(m)
        print(f"      $metrics:    {met_names}")
        # filters summary
        if filters:
            print(f"      $filters:    {str(filters)[:200]}")
        # dataProviderId
        dpid = dr.get('dataProviderId')
        if dpid:
            print(f"      dataProviderId: {dpid}")

# ============================================================
# 2) ALL Table/ElemHeader definitions
# ============================================================
print("\n" + "=" * 70)
print("2) ALL Table/ElemHeader (column headers)")
print("=" * 70)
for e in all_elements:
    if e['type'] == 'Table/ElemHeader':
        print(f"  id={e['id']}  header={e['props'].get('header')}  dataField={e['props'].get('dataField')}  cssClass={e['props'].get('cssClass')}")

# ============================================================
# 3) ALL ElemText html content (deduplicated)
# ============================================================
print("\n" + "=" * 70)
print("3) ALL ElemText html content")
print("=" * 70)
seen_html = set()
for e in all_elements:
    if e['type'] == 'ElemText':
        h = e['props'].get('html', '')
        if h and h not in seen_html:
            seen_html.add(h)
            # strip tags for summary
            clean = re.sub(r'<[^>]+>', '', h).strip()
            print(f"  depth={e['depth']:2d}  raw={h[:120]}")
            if clean != h[:120]:
                print(f"            text={clean[:100]}")

# ============================================================
# 4) ALL ElemStandardFilter dimensions & placeholders
# ============================================================
print("\n" + "=" * 70)
print("4) ALL ElemStandardFilter (filter widgets)")
print("=" * 70)
for e in all_elements:
    if e['type'] == 'PerformanceManagement/ElemStandardFilter':
        p = e['props']
        print(f"  id={e['id']}")
        print(f"      selectedDimension: {p.get('selectedDimension')}")
        print(f"      textPlaceholder:   {p.get('textPlaceholder')}")
        print(f"      slot:              {p.get('slot')}")
        print(f"      multiMode:         {p.get('multiMode')}")
        print(f"      filtrationMode:    {p.get('filtrationMode')}")
        va = p.get('varAliases', {})
        print(f"      varAliases:        {va}")
        # dremio $from
        for dr in extract_dremio(p):
            q = dr.get('query', {})
            print(f"      dremio.$from:      {q.get('$from')}")
            flds = q.get('$fields', {})
            print(f"      dremio.$fields:    {sorted(flds.keys()) if isinstance(flds,dict) else flds}")

# ============================================================
# 5) ALL MultiKpi configs
# ============================================================
print("\n" + "=" * 70)
print("5) ALL PerformanceManagement/ElemMultiKpi")
print("=" * 70)
for e in all_elements:
    if e['type'] == 'PerformanceManagement/ElemMultiKpi':
        p = e['props']
        print(f"  id={e['id']}")
        print(f"      selectedMetric:    {p.get('selectedMetric')}")
        print(f"      selectedDimension: {p.get('selectedDimension')}")
        print(f"      preFix:            {p.get('preFix')}")
        print(f"      type:              {p.get('type')}")
        for dr in extract_dremio(p):
            q = dr.get('query', {})
            print(f"      dremio.$from:      {q.get('$from')}")
            flds = q.get('$fields', {})
            print(f"      dremio.$fields:    {sorted(flds.keys()) if isinstance(flds,dict) else flds}")

# ============================================================
# 6) ALL MultiSpline configs
# ============================================================
print("\n" + "=" * 70)
print("6) ALL PerformanceManagement/ElemMultiSpline")
print("=" * 70)
for e in all_elements:
    if e['type'] == 'PerformanceManagement/ElemMultiSpline':
        p = e['props']
        print(f"  id={e['id']}")
        print(f"      metricNames:       {p.get('metricNames')}")
        print(f"      dimensionOptions:  {p.get('dimensionOptions')}")
        for dr in extract_dremio(p):
            q = dr.get('query', {})
            print(f"      dremio.$from:      {q.get('$from')}")
            flds = q.get('$fields', {})
            print(f"      dremio.$fields:    {sorted(flds.keys()) if isinstance(flds,dict) else flds}")

# ============================================================
# 7) ALL ElemSmartGallery slot/metric configs
# ============================================================
print("\n" + "=" * 70)
print("7) ALL ElemSmartGallery")
print("=" * 70)
for e in all_elements:
    if e['type'] == 'ElemSmartGallery':
        p = e['props']
        print(f"  id={e['id']}  depth={e['depth']}")
        print(f"      metrics:  {p.get('metrics')}")
        print(f"      slots:    {p.get('slots')}")
        print(f"      slot:     {p.get('slot')}")
        for dr in extract_dremio(p):
            q = dr.get('query', {})
            print(f"      dremio.$from:  {q.get('$from')}")
            flds = q.get('$fields', {})
            print(f"      dremio.$fields: {sorted(flds.keys()) if isinstance(flds,dict) else flds}")

# ============================================================
# 8) ElemEventStack state machines
# ============================================================
print("\n" + "=" * 70)
print("8) ALL ElemEventStack (state machines / navigation)")
print("=" * 70)
for e in all_elements:
    if e['type'] == 'ElemEventStack':
        p = e['props']
        print(f"  id={e['id']}  depth={e['depth']}")
        print(f"      activeState: {p.get('activeState')}")
        print(f"      states:      {p.get('states')}")
        print(f"      slot:        {p.get('slot')}")

# ============================================================
# 9) ChartFilterMed configs
# ============================================================
print("\n" + "=" * 70)
print("9) ALL 5INSIGHT/ElemChartFilterMed")
print("=" * 70)
seen_cf = set()
for e in all_elements:
    if e['type'] == '5INSIGHT/ElemChartFilterMed':
        p = e['props']
        dim = p.get('dimension')
        key = (dim, p.get('type'), str(p.get('varAliases')))
        if key in seen_cf:
            continue
        seen_cf.add(key)
        print(f"  id={e['id']}")
        print(f"      dimension:      {dim}")
        print(f"      type:           {p.get('type')}")
        print(f"      valueByDefault: {p.get('valueByDefault')}")
        print(f"      varAliases:     {p.get('varAliases')}")
        for dr in extract_dremio(p):
            q = dr.get('query', {})
            print(f"      dremio.$from:   {q.get('$from')}")
            flds = q.get('$fields', {})
            print(f"      dremio.$fields: {sorted(flds.keys()) if isinstance(flds,dict) else flds}")

# ============================================================
# 10) ElemLayersContainer - layer structure
# ============================================================
print("\n" + "=" * 70)
print("10) ALL ElemLayersContainer (overlay layers)")
print("=" * 70)
for e in all_elements:
    if e['type'] == 'ElemLayersContainer':
        print(f"  id={e['id']}  depth={e['depth']}")
        print(f"      layers: {e['props'].get('layers')}")

# ============================================================
# 11) ElemHouse configs
# ============================================================
print("\n" + "=" * 70)
print("11) ALL PerformanceManagement/ElemHouse")
print("=" * 70)
for e in all_elements:
    if e['type'] == 'PerformanceManagement/ElemHouse':
        p = e['props']
        print(f"  id={e['id']}")
        print(f"      workType:         {p.get('workType')}")
        print(f"      currentMetric:    {p.get('currentMetric')}")
        print(f"      enableCurrentMetric: {p.get('enableCurrentMetric')}")
        print(f"      fetchDataEvent:   {p.get('fetchDataEvent')}")
        for dr in extract_dremio(p):
            q = dr.get('query', {})
            print(f"      dremio.$from:     {q.get('$from')}")
            flds = q.get('$fields', {})
            print(f"      dremio.$fields:   {sorted(flds.keys()) if isinstance(flds,dict) else flds}")

# ============================================================
# 12) DremioTable columns detail (title, sort/dataField, render)
# ============================================================
print("\n" + "=" * 70)
print("12) ALL ElemDremioTable column definitions (title + sort field + render)")
print("=" * 70)
for e in all_elements:
    if e['type'] == 'ElemDremioTable':
        cols = e['props'].get('columns', [])
        print(f"\n  id={e['id']}  depth={e['depth']}  showHead={e['props'].get('showHead')}")
        # dremio $from
        for dr in extract_dremio(e['props']):
            q = dr.get('query', {})
            print(f"      $from: {q.get('$from')}")
        for i, col in enumerate(cols):
            title = col.get('title', '')
            sort = col.get('sort', '')
            render = col.get('render', '')
            dataField = col.get('dataField', '')
            print(f"      col[{i}]: title={title!r:30s} sort={sort!r:30s} dataField={dataField!r:25s} render={render!r}")
