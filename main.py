import sys
from pathlib import Path
import xmltodict
from PIL import Image
from math import isclose, ceil
from sheet_entry import SheetEntry

PROJECT_PATH = Path(sys.path[0])
RESOURCES_PATH = PROJECT_PATH.joinpath('resources')
RESOURCES_PACKS_PATH = PROJECT_PATH.joinpath('resources/packs')
RESOURCES_EXISTING_SHEETS_PATH = PROJECT_PATH.joinpath('resources/existing_sheets')

EXPORTS_PATH = PROJECT_PATH.joinpath('exports')
EXPORTS_WARNING_PATH = EXPORTS_PATH.joinpath('__DO NOT SAVE HERE__.txt')

# {'property': 'booleanX'}
# {'property': 'fileNameSize'}
# {'property': 'filename'}
# {'property': 'format'}
# {'property': 'frameEntries'}
# {'property': 'numFrameEntries'}

def main():

    if EXPORTS_PATH.exists():
        delete_directory(EXPORTS_PATH)

    EXPORTS_PATH.mkdir()

    if not EXPORTS_WARNING_PATH.exists():
        with open(EXPORTS_WARNING_PATH, "w") as warning_file:
            print('Do not save any changes to this directory, it will be overwritten by the next operation!',
                  file=warning_file)

    existing_sheets = []

    if RESOURCES_EXISTING_SHEETS_PATH.exists():
        for sheet in RESOURCES_EXISTING_SHEETS_PATH.iterdir():
            if sheet.is_dir():
                continue
            existing_sheets.append(sheet.stem)

    sheets = {}

    for dir in RESOURCES_PACKS_PATH.iterdir():
        if dir.is_dir():
            for file in dir.iterdir():
                if file.is_file() and str(file).endswith('.xml'):
                    with open(file, 'r') as reader:
                        root = xmltodict.parse(reader.read())['java']['object']['void'][0]['array']['void']
                        for child in root:
                            consume_sheet(file.stem, child, sheets)

    new_sheets = []

    sheet_count = len(sheets.keys())

    print('Processing {} sheets'.format(sheet_count))

    for i in range(0, sheet_count):
        print('_', end='')

    print('\n', end='')

    for key, value in sheets.items():
        if existing_sheets:
            if key not in existing_sheets:
                new_sheets.append(key)
        clone_sheet(key, value)
        print('.', end='')

    print('\nDone! {} sheets stitched'.format(sheet_count))

    if new_sheets:
        print('New Sheets:')
        for sheet in new_sheets:
            print('\t{}'.format(sheet))

def consume_sheet(pack_name, root, sheets):
    root = root['object']['void']

    directory = None
    frame_count = None
    frame_entries = None

    for property in root:
        property_name = property['@property']
        if property_name == 'filename':
            directory = property['string']
        elif property_name == 'numFrameEntries':
            frame_count = property['int']
        elif property_name == 'frameEntries':
            frame_entries = property['array']['void']

    root_asset_path = RESOURCES_PACKS_PATH.joinpath(pack_name).joinpath(directory)

    for entry in frame_entries:
        asset = SheetEntry(entry['object']['void'], root_asset_path)
        sheet = sheets.get(asset.sheet)
        if not sheet:
            sheet = []
            sheets[asset.sheet] = sheet
        sheet.append(asset)


def delete_directory(target_path):
    if not target_path:
        raise Exception('Invalid target path provided!')

    for sub in target_path.iterdir():
        if sub.is_dir():
            delete_directory(sub)
        else:
            sub.unlink()
    target_path.rmdir()

def clone_sheet(sheet_name, entries):
    sheet_path = EXPORTS_PATH.joinpath('{}.png'.format(sheet_name))
    sheet_assets_path = EXPORTS_PATH.joinpath(sheet_name)
    sheet_assets_path.mkdir()

    indices_skipped = []
    index_last = 0
    for entry in entries:
        index_current = int(entry.index)
        for i in range(index_last, index_current):
            indices_skipped.append(i)
        index_last = index_current + 1
        clone_asset(sheet_assets_path.joinpath('{}.png'.format(index_current)), entry)

    for index in indices_skipped:
        clone_asset(sheet_assets_path.joinpath('{}.png'.format(index)), None)

    cell_height = 1

    if 8 < index_last:
        if isclose(index_last % 8.0, 0.0):
            cell_height = index_last / 8
        else:
            cell_height = ceil(index_last / 8.0)

    cell_height = int(cell_height)

    stitch_asset(sheet_assets_path, sheet_path, index_last, cell_height)

    delete_directory(sheet_assets_path)

def clone_asset(export_path, entry):
    result = Image.new('RGBA', (128, 256))
    if entry is not None:
        source = Image.open(entry.asset_path)
        result.paste(source, (entry.offset_x, entry.offset_y))

    result.save(export_path)

def stitch_asset(source_path, export_path, count, cell_height):

    sheet = Image.new('RGBA', (128 * 8, 256 * cell_height))

    index = 0
    is_done = False

    for y in range(0, cell_height):
        for x in range(0, 8):
            source = Image.open(source_path.joinpath('{}.png'.format(index)))
            sheet.paste(source, (x * 128, y * 256))
            index = index + 1
            is_done = count <= index
            if is_done:
                break
        if is_done:
            break

    sheet.save(export_path)
    # print('source: {}, export: {}, count: {}, cell_height: {}'.format(source_path, export_path, count, cell_height))

if __name__ == '__main__':
    main()
