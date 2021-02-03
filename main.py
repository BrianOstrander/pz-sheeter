import sys
from pathlib import Path
import xml.etree.ElementTree as ET
import xmltodict

PROJECT_PATH = Path(sys.path[0])
RESOURCES_PATH = PROJECT_PATH.joinpath('resources/Tiles2x')
RESOURCES_XML_PATH = RESOURCES_PATH.joinpath('Tiles2x.xml')

# {'property': 'booleanX'}
# {'property': 'fileNameSize'}
# {'property': 'filename'}
# {'property': 'format'}
# {'property': 'frameEntries'}
# {'property': 'numFrameEntries'}

def main():
    print(RESOURCES_XML_PATH)
    with open(RESOURCES_XML_PATH, 'r') as reader:
        root = xmltodict.parse(reader.read())['java']['object']['void'][0]['array']['void']
        for child in root:
            process(child)
            break

    # tree = ET.parse(RESOURCES_XML_PATH)
    # root = tree.getroot()
    #
    # # for child in root[0][0][0]:
    # #     print(child.attrib)
    #
    # for child in root[0][0][0]:
    #     # print(child[0][0].attrib)
    #     process(child[0])
    #     break
    #
    # # for child in root[0][0][0][0].items:
    #     print(child.get('filename'))

def process(root):
    print(root['@index'])
    for child in root['object']['void']:
        print(child['@property'])

if __name__ == '__main__':
    main()
