from lxml import etree
from pprint import pprint

import sqlaload as sl

engine = sl.connect('sqlite:///budget.db')
table = sl.get_table(engine, 'budget')
year = 2010

FIGURE_FIELDS = {
    'total': ['amount_total', 'amount_reserve_total_total', 'amount_reserve_figure_total'],
    'comm': ['amount_comm', 'amount_reserve_comm_comm', 'amount_reserve_figure_comm'],
    'pay': ['amount_pay', 'amount_reserve_pay_pay', 'amount_reserve_figure_pay']
    }

def xml_dict(file_name, depth=2):
    doc = etree.parse(file_name)
    def _node(node, depth):
        data = {'!name': node.tag, '!e': node}
        if node.tail is not None and len(node.tail.strip()):
            data[':tail'] = node.tail
        if node.text is not None and len(node.text.strip()):
            data[':text'] = node.text
        for a, v in node.attrib.items():
            data['@' + a] = v
        if depth > 0:
            for child in node:
                cd = _node(child, depth-1)
                if not child.tag in data:
                    data[child.tag] = cd
                elif isinstance(data[child.tag], list):
                    data[child.tag].append(cd)
                else:
                    data[child.tag] = [data[child.tag], cd]
        return data
    return _node(doc.getroot(), depth)

def print_remaining(d):
    print_ = False
    for k in d.keys():
        if k not in ['!name', '!e', '@lang']:
            print_ = True
    if print_:
        pprint(d)

def emit(data):
    if not 'amount_n_total' in data and not 'amount_n_pay' in data:
        return
    for colyear, d in [('amount_nm2_', 2), ('amount_nm1_', 1), ('amount_n_', 0)]:
        rec = {'year': year - d}
        for k, v in data.items():
            if k.startswith(colyear):
                k = k.replace(colyear, 'amount_')
                rec[k] = v
            elif not k.startswith('amount_'):
                rec[k] = v
        for figure_type, fields in FIGURE_FIELDS.items():
            r = rec.copy()
            r.update({
                'amount': rec.get(fields[0]),
                'amount_reserve_total': rec.get(fields[1]),
                'amount_reserve_figure': rec.get(fields[2]),
                'figure_type': figure_type
                })
            for fields in FIGURE_FIELDS.values():
                for f in fields:
                    r.pop(f, None)
            sl.add_row(engine, table, r)

def get_p(d):
    text = []
    for p in _each(d.pop('p', [])):
        if ':text' in p:
            text.append(p.pop(':text'))
        if 'ft' in p:
            for ft in _each(p.pop('ft')):
                text.append(ft.pop(':text', ""))
    return '\n\n'.join(text)

def bud_data(bd):
    d = {}
    if '@exprev' in bd:
        d['exprev'] = bd.pop('@exprev')
    if '@tot' in bd:
        d['tot'] = bd.pop('@tot')
    if '@type' in bd:
        d['type'] = bd.pop('@type')
    if 'hresources' in bd:
        hresources = bd.pop('hresources')
        #print_remaining(hresources)
    if 'relations' in bd:
        relation = bd.pop('relations').pop('relation', {})
        d['relation'] = relation.get('@value', None)
    if 'amounts' in bd:
        for amount in _each(bd.pop('amounts').get('amount')):
            name = 'amount_%s' % amount.pop('@year')
            d[name + '_catpol'] = amount.pop('@catpol', None)
            d[name + '_comp'] = amount.pop('@comp', None)
            d[name + '_diff'] = amount.pop('@diff', None)
            d[name + '_aele'] = amount.pop('@aele', None)
            d[name + '_peco'] = amount.pop('@peco', None)
            d[name + '_delegation'] = amount.pop('@delegation', None)
            for fig in _each(amount.pop('figure')):
                d[name + '_' + fig.pop('@commpay', 'total')] = fig.pop(':text', None)

            if 'reserve' in amount:
                reserve = amount.pop('reserve')
                d[name + '_reserve_alias'] = reserve.pop('alias').pop(':text')
                for fig in _each(reserve.pop('figure')):
                    d[name + '_reserve_figure_' + fig.pop('@commpay', 'total')] = fig.pop(':text', None)
                for fig in _each(reserve.pop('total').pop('figure')):
                    d[name + '_reserve_total_' + fig.pop('@commpay', 'total')] = fig.pop(':text', None)
            print_remaining(amount)
    print_remaining(bd)
    return d

def bud_heading(bh):
    # TODO check
    return bh.pop('p').pop(':text', None)

def bud_legal(bl):
    # TODO check
    if bl is None:
        return None
    if 'p' in bl:
        return get_p(bl)
    if 'reuse-link' in bl:
        reuse_link = bl.pop('reuse-link')
        # TODO: Handle re-use links
        #print_remaining(reuse_link)
    if 'list' in bl:
        l = bl.pop('list')
        t = ''
        for li in _each(l):
            for item in _each(li.pop('int.li')):
                t += get_p(item) + '\n'
            for item in _each(li.pop('item')):
                t += '\n * '
                t += get_p(item)
        return t
    print_remaining(bl)
    return None

def bud_remarks(bl):
    return bud_legal(bl)

def bud_reference(bl):
    return bud_legal(bl)

def _each(e):
    if e is not None:
        if isinstance(e, list):
            for i in e:
                yield i
        else:
            yield e

def extract_subitem(base, subitem):
    base = base.copy()
    base.update({
        'subitem_id': subitem.pop('@id'),
        'subitem_alias': subitem.pop('@alias'),
        'subitem_name': bud_heading(subitem.pop('bud-heading')),
        'subitem_legal': bud_legal(subitem.pop('bud-legal', None)),
        'subitem_remarks': bud_remarks(subitem.pop('bud-remarks', None)),
        'subitem_reference': bud_reference(subitem.pop('bud-reference', None))
        })
    base.update(bud_data(subitem.pop('bud-data')))
    emit(base)
    print_remaining(subitem)

def extract_item(base, item):
    base = base.copy()
    base.update({
        'item_id': item.pop('@id'),
        'item_alias': item.pop('@alias'),
        'item_name': bud_heading(item.pop('bud-heading')),
        'item_legal': bud_legal(item.pop('bud-legal', None)),
        'item_remarks': bud_remarks(item.pop('bud-remarks', None)),
        'item_reference': bud_reference(item.pop('bud-reference', None))
        })
    assert not ('amounts' in item.get('bud-data') and 'nmc-subitem' in item), item
    base.update(bud_data(item.pop('bud-data')))
    for subitem in _each(item.pop('nmc-subitem', None)):
        extract_subitem(base, subitem)
    #if not 'nmc-subitem' in data:
    emit(base)
    print_remaining(item)

def extract_article(base, article):
    base = base.copy()
    base.update({
        'article_id': article.pop('@id'),
        'article_alias': article.pop('@alias'),
        'article_type': article.pop('@type', None),
        'article_name': bud_heading(article.pop('bud-heading')),
        'article_legal': bud_legal(article.pop('bud-legal', None)),
        'article_remarks': bud_remarks(article.pop('bud-remarks', None)),
        'article_reference': bud_reference(article.pop('bud-reference', None))
        })
    assert not ('amounts' in article.get('bud-data') and 'nmc-item' in article), article
    base.update(bud_data(article.pop('bud-data')))
    for item in _each(article.pop('nmc-item', None)):
        extract_item(base, item)
    emit(base)
    print_remaining(article)

def extract_chapter(base, chapter):
    base = base.copy()
    base.update({
        'chapter_id': chapter.pop('@id'),
        'chapter_alias': chapter.pop('@alias'),
        'chapter_type': chapter.pop('@type', None),
        'chapter_name': bud_heading(chapter.pop('bud-heading')),
        'chapter_legal': bud_legal(chapter.pop('bud-legal', None)),
        'chapter_remarks': bud_remarks(chapter.pop('bud-remarks', None)),
        'chapter_reference': bud_reference(chapter.pop('bud-reference', None))
        })
    base.update(bud_data(chapter.pop('bud-data')))
    for article in _each(chapter.pop('nmc-article', None)):
        extract_article(base, article)
    print_remaining(chapter)

def extract_title(base, title):
    base = base.copy()
    base.update({
        'title_id': title.pop('@id'),
        'title_alias': title.pop('@alias'),
        'title_name': bud_heading(title.pop('bud-heading')),
        'title_legal': bud_legal(title.pop('bud-legal', None)),
        'title_remarks': bud_remarks(title.pop('bud-remarks', None)),
        'title_reference': bud_reference(title.pop('bud-reference', None))
        })
    title.pop('bud-intro', None)
    base.update(bud_data(title.pop('bud-data')))
    for chapter in _each(title.pop('nmc-chapter', None)):
        extract_chapter(base, chapter)
    print_remaining(title)

def extract_part(base, part):
    base = base.copy()
    base.update({
        'part_id': part.pop('@id'),
        'part_alias': part.pop('@alias'),
        })
    base.update(bud_data(part.pop('bud-data')))
    base['part_name'] = bud_heading(part.pop('bud-heading'))
    for title in _each(part.pop('nmc-title')):
        extract_title(base, title)
    print_remaining(part)

def parse_file(year, file_name):
    data = xml_dict(file_name, depth=1000)
    base = {'section_alias': data.pop('@alias'), 'section_id': data.pop('@id')}
    base['section_name'] = bud_heading(data.pop('bud-heading'))
    for part_name in ['nmc-revenue', 'nmc-expenditure']:
        if part_name in data:
            extract_part(base, data.pop(part_name))
    #print_remaining(data)

if __name__ == '__main__':
    import sys
    file_name = sys.argv[1]
    parse_file(2010, file_name)
