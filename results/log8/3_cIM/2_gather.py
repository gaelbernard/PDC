from anytree.importer import JsonImporter
from anytree import RenderTree
import xml.etree.ElementTree as ET

def get_by_name(xml, name):
    results = [e for e in xml.iter('manualTask') if e.attrib['name'] == name]
    if len(results)!=1:
        raise ValueError('Name does not exist exactly once!')
    return results[0]

def delete_node(xml, id):
    tbd = None
    for e in xml.find('processTree'):
        if e.attrib['id'] == id:
            tbd = e
            break

    if tbd is None:
        raise ValueError('Id was not found')

    xml.find('processTree').remove(e)

def add_content(main_xml, content_to_copy):
    m = main_xml.find('processTree')
    for e in content_to_copy.find('processTree'):
        m.append(e)

def changing_id(xml, needle, replace_by):
    for e in xml.find('processTree'):
        for a in ['id', 'sourceId', 'targetId']:
            if a in e.attrib.keys():
                if e.attrib[a] == needle:
                    e.attrib[a] = replace_by


importer = JsonImporter()
with open('1_split/rendertree.json', 'r') as f:
    root = importer.read(f)



main = ET.parse('2_gather/{}.ptml'.format(root.name))

print (RenderTree(root))
for c in root.children:
    sub = ET.parse('2_gather/{}.ptml'.format(c.name))
    id_in_main = get_by_name(main, c.name).attrib['id']
    id_in_sub = sub.find('processTree').attrib['root']
    delete_node(main, id_in_main)

    changing_id(sub, id_in_sub, id_in_main)
    add_content(main, sub)

main.write('2_gather/pt.ptml')


