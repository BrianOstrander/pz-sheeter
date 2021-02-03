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

import click

@click.group()
def cli():
  pass

@cli.command(name='version')
def generic():
    click.echo('todo')

@cli.command(name='unpack')
@click.argument('resources_xml_path', type=click.Path(), default=str(RESOURCES_XML_PATH), description="XML to extract from.")
def unpack(resources_xml_path):
    """Unpacks raw texture sheet data into their original format."""
    print(resources_xml_path)
    with open(resources_xml_path, 'r') as reader:  
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
    cli()
