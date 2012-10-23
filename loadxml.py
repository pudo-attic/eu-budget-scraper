#coding: utf-8

from lxml import etree

# nmc-section > nmc-revenue > nmc-title > nmc-chapter > nmc-article > nmc-item 
#    > nmc-subitem
# nmc-section > nmc-expenditure > ...


def extract_p(elem):
    if elem is None:
        return
    p = elem.find("p")
    if p is None:
        return
    return p.xpath("string()")


def extract_text(elem):
    if elem is None:
        return
    return '\n'.join(map(etree.tostring, elem.getchildren()))


def extract_num(elem):
    if elem is None:
        return
    text = elem.find("figure").text
    if text is not None:
        text = text.replace(" ", "").replace(",", ".")
    return text


def extract_bud_data(elem, prefix):
    data = {}
    bud_data = elem.find("bud-data")
    if bud_data is not None:
        data[prefix + '_exprev'] = bud_data.get('exprev')
        data[prefix + '_budtype'] = bud_data.get('type')
        for amount in bud_data.findall('.//amount'):
            year = amount.get('year')
            data['level'] = prefix
            data['budamount_' + year] = \
                data[prefix + '_budamount_' + year] = extract_num(amount)
            data['budcatpol_' + year] = \
                data[prefix + '_budcatpol_' + year] = amount.get('catpol')
    return data


def extract_node(elem, prefix):
    data = {
        prefix + '_id': elem.get('id'),
        prefix + '_alias': elem.get('alias')
        }
    data[prefix + '_heading'] = extract_p(elem.find('bud-heading'))

    # todo text:
    data[prefix + '_remarks'] = extract_text(elem.find('bud-remarks'))
    data[prefix + '_legal'] = extract_text(elem.find('bud-legal'))

    data.update(extract_bud_data(elem, prefix))
    return data


def parse_tree(data, elem):
    for title in elem.findall('nmc-title'):
        tdata = data.copy()
        tdata.update(extract_node(title, 'title'))
        for chapter in title.findall('nmc-chapter'):
            cdata = tdata.copy()
            cdata.update(extract_node(chapter, 'chapter'))
            for article in chapter.findall('nmc-article'):
                adata = cdata.copy()
                adata.update(extract_node(article, 'article'))
                items = article.findall('nmc-item')
                if len(items):
                    for item in items:
                        idata = adata.copy()
                        idata.update(extract_node(item, 'item'))
                        subitems = article.findall('nmc-subitem')
                        if len(subitems):
                            for subitem in subitems:
                                sidata = idata.copy()
                                sidata.update(extract_node(subitem, 'subitem'))
                                yield sidata
                        else:
                            yield idata
                else:
                    yield adata


def parse_file(year, file_name):
    doc = etree.parse(file_name)
    section = doc.getroot()
    data = extract_node(section, 'section')
    for base in ['nmc-revenue', 'nmc-expenditure']:
        tag = section.find(base)
        s_data = extract_node(tag, 'base')
        s_data.update(data)
        for post in parse_tree(s_data, tag):
            print post


if __name__ == '__main__':
    import sys
    file_name = sys.argv[1]
    parse_file(2010, file_name)
