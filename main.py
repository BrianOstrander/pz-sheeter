import sys
from pathlib import Path
import xmltodict
import time
import json
from shutil import copyfile
from PIL import Image, ImageChops
from math import isclose, ceil
from sheet_entry import SheetEntry

PROJECT_PATH = Path(sys.path[0])
RESOURCES_PATH = PROJECT_PATH.joinpath('resources')
RESOURCES_PACKS_PATH = RESOURCES_PATH.joinpath('packs')
RESOURCES_EXISTING_SHEETS_PATH = RESOURCES_PATH.joinpath('existing_sheets')
RESOURCES_PATCHES_PATH = RESOURCES_PATH.joinpath('patches')

EXPORTS_PATH = PROJECT_PATH.joinpath('exports')
EXPORTS_DIFFS_NEW_PATH = EXPORTS_PATH.joinpath('__diffs new__')
EXPORTS_DIFFS_CHANGED_PATH = EXPORTS_PATH.joinpath('__diffs changed__')
EXPORTS_WARNING_PATH = EXPORTS_PATH.joinpath('___DO NOT SAVE HERE___.txt')


def main(destructive=False):
    time_begin = time.time()

    if destructive:
        if EXPORTS_PATH.exists():
            delete_directory(EXPORTS_PATH)

        EXPORTS_PATH.mkdir()
        EXPORTS_DIFFS_NEW_PATH.mkdir()
        EXPORTS_DIFFS_CHANGED_PATH.mkdir()

    if not EXPORTS_WARNING_PATH.exists():
        with open(EXPORTS_WARNING_PATH, "w") as warning_file:
            print('Do not save any changes to this directory, it will be overwritten by the next operation!',
                  file=warning_file)

    existing_sheets = {}

    if RESOURCES_EXISTING_SHEETS_PATH.exists():
        for sheet in RESOURCES_EXISTING_SHEETS_PATH.iterdir():
            if sheet.is_file() and str(sheet).endswith('.png'):
                sheet_image = Image.open(sheet)
                existing_sheets[sheet.stem] = (int(sheet_image.width / 128), int(sheet_image.height / 256))
                sheet_image.close()

    sheets = {}

    for dir in RESOURCES_PACKS_PATH.iterdir():
        if dir.is_dir():
            for file in dir.iterdir():
                if file.is_file() and str(file).endswith('.xml'):
                    with open(file, 'r') as reader:
                        root = xmltodict.parse(reader.read())['java']['object']['void'][0]['array']['void']
                        for child in root:
                            consume_sheet(file.stem, child, sheets)

    sheet_count = len(sheets.keys())

    print('Processing {} sheets'.format(sheet_count))

    for i in range(0, sheet_count):
        print('_', end='')

    print('\n', end='')

    next_bar = 0
    for key, value in sheets.items():
        width_minimum = 0
        height_minimum = 0
        if existing_sheets:
            if key in existing_sheets.keys():
                width_minimum = existing_sheets[key][0]
                height_minimum = existing_sheets[key][1]
        if destructive:
            clone_sheet(key, value, width_minimum, height_minimum)

        if next_bar == 4:
            print('|', end='')
            next_bar = 0
        else:
            print('.', end='')
            next_bar = next_bar + 1

    print('')

    operations = patch()

    missing_sheets = []
    sheet_size_changes = {}
    sheet_hash_changes = []
    sheet_hash_rejections = []

    print('Hashing {} sheets'.format(len(existing_sheets)))

    for i in range(0, len(existing_sheets)):
        print('_', end='')

    print('\n', end='')

    next_bar = 0
    for existing_sheet in existing_sheets.keys():
        if existing_sheet in sheets.keys():
            image_existing = Image.open(RESOURCES_EXISTING_SHEETS_PATH.joinpath('{}.png'.format(existing_sheet)))
            image_exported = Image.open(EXPORTS_PATH.joinpath('{}.png'.format(existing_sheet)))

            if image_existing.width != image_exported.width or image_existing.height != image_exported.height:
                width = int(image_exported.width - image_existing.width)
                height = int(image_exported.height - image_existing.height)

                sign_width = '+' if 0 < width else '-'
                sign_height = '+' if 0 < height else '-'

                size = ''
                if width != 0 and height != 0:
                    size = 'w {}{} , h {}{}'.format(sign_width, int(width / 128), sign_height, int(height / 256))
                elif width != 0:
                    size = 'w {}{}'.format(sign_width, int(width / 128))
                elif height != 0:
                    size = 'h {}{}'.format(sign_height, int(height / 256))

                sheet_size_changes[existing_sheet] = size
            else:
                alpha_existing = image_existing.split()[-1].convert('1')
                alpha_exported = image_exported.split()[-1].convert('1')
                image_difference = ImageChops.difference(alpha_existing, alpha_exported)
                image_box = image_difference.getbbox()
                if image_box:
                    if 2 < (image_box[2] - image_box[0]) and 2 < (image_box[3] - image_box[1]):
                        sheet_hash_changes.append(existing_sheet)
                        image_difference.save(EXPORTS_DIFFS_CHANGED_PATH.joinpath('{}_diff.png'.format(existing_sheet)))
                        image_difference.close()
                    else:
                        sheet_hash_rejections.append(existing_sheet)

            image_existing.close()
            image_exported.close()

        else:
            missing_sheets.append(existing_sheet)

        if next_bar == 4:
            print('|', end='')
            next_bar = 0
        else:
            print('.', end='')
            next_bar = next_bar + 1

    if operations:
        print('')
        for operation in sorted(operations.keys(), key=str.casefold):
            print('')
            print('Operation: {}'.format(operation))
            for operation_entry in operations[operation]:
                print('\t{}'.format(operation_entry))

    print('')

    new_sheets = []

    for file in EXPORTS_PATH.iterdir():
        if file.is_file() and str(file).endswith('.png'):
            if file.stem not in existing_sheets.keys():
                new_sheets.append(file.stem)

    sheet_diffs = []

    if new_sheets:
        print('New Sheets: \t{}'.format(len(new_sheets)))
        for sheet in sorted(new_sheets, key=str.casefold):
            print('\t{}'.format(sheet))
            sheet_diffs.append(sheet)
            copyfile(EXPORTS_PATH.joinpath('{}.png'.format(sheet)), EXPORTS_DIFFS_NEW_PATH.joinpath('{}.png'.format(sheet)))
        print('')

    if missing_sheets:
        print('Missing Sheets: \t{}'.format(len(missing_sheets)))
        for sheet in sorted(missing_sheets, key=str.casefold):
            print('\t{}'.format(sheet))
        print('')

    all_sheet_changes = []

    if sheet_size_changes:
        print('Sheet Size Changes: \t{}'.format(len(sheet_size_changes)))
        for sheet in sorted(sheet_size_changes.keys(), key=str.casefold):
            all_sheet_changes.append(sheet)
            print('{}\t:\t{}'.format(sheet_size_changes[sheet], sheet))
        print('')

    if sheet_hash_changes:
        print('Sheet Hash Changes: \t{}'.format(len(sheet_hash_changes)))
        for sheet in sorted(sheet_hash_changes, key=str.casefold):
            if sheet not in all_sheet_changes:
                all_sheet_changes.append(sheet)
            print('\t{}'.format(sheet))
        print('')

    if sheet_hash_rejections:
        print('Sheet Hash Rejections: \t{}'.format(len(sheet_hash_rejections)))
        for sheet in sorted(sheet_hash_rejections, key=str.casefold):
            print('\t{}'.format(sheet))
        print('')

    if new_sheets:
        print('All Sheet Changes: \t{}'.format(len(all_sheet_changes)))
        for sheet in sorted(all_sheet_changes, key=str.casefold):
            print('\t{}'.format(sheet))
            sheet_diffs.append(sheet)
            copyfile(EXPORTS_PATH.joinpath('{}.png'.format(sheet)), EXPORTS_DIFFS_CHANGED_PATH.joinpath('{}.png'.format(sheet)))
        print('')

    if sheet_diffs:
        print('All New and Changed Sheets: \t{}'.format(len(sheet_diffs)))
        for sheet in sorted(sheet_diffs, key=str.casefold):
            print('\t{}'.format(sheet))
        print('')

    time_total = time.time() - time_begin

    if time_total < 60:
        time_total = '{} seconds'.format(time_total)
    else:
        time_total = '{}:{} minutes'.format(int(time_total / 60), int(time_total % 60))

    print('\nDone! {} sheets stitched in {}'.format(sheet_count, time_total))


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


def clone_sheet(sheet_name, entries, width_minimum, height_minimum, cleanup=True):
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

    cell_width = 1
    cell_height = 1

    if width_minimum != 0:
        cell_width = max(int(cell_width), width_minimum)
    else:
        cell_width = 8

    if 8 < index_last:
        if isclose(index_last % 8.0, 0.0):
            cell_height = index_last / 8
        else:
            cell_height = ceil(index_last / 8.0)

    if height_minimum != 0:
        cell_height = max(int(cell_height), height_minimum)

    stitch_asset(sheet_assets_path, sheet_path, index_last, int(cell_width), int(cell_height))

    if cleanup:
        delete_directory(sheet_assets_path)


def clone_asset(export_path, entry):
    if entry is None and export_path.exists():
        return

    result = Image.new('RGBA', (128, 256))
    if entry is not None:
        source = Image.open(entry.asset_path)
        result.paste(source, (entry.offset_x, entry.offset_y))
        source.close()

    result.save(export_path, 'PNG')
    result.close()


def stitch_asset(source_path, export_path, count, cell_width, cell_height):

    sheet = Image.new('RGBA', (128 * cell_width, 256 * cell_height))

    index = 0
    is_done = False

    for y in range(0, cell_height):
        for x in range(0, cell_width):
            source = Image.open(source_path.joinpath('{}.png'.format(index)))
            sheet.paste(source, (x * 128, y * 256))
            source.close()
            index = index + 1
            is_done = count <= index
            if is_done:
                break
        if is_done:
            break

    sheet.save(export_path, 'PNG')
    sheet.close()


def patch():

    operations = {}

    for file in RESOURCES_PATCHES_PATH.iterdir():
        if file.is_file() and str(file).endswith('.json'):
            with open(file) as file_json:
                file_json_data = json.load(file_json)
                if file_json_data.get('type') == 'patch':
                    index = 0
                    for entry in file_json_data['entries']:
                        operation = entry['operation']

                        if operation == 'replace':
                            operation_results = patch_replace(entry)
                        elif operation == 'delete':
                            operation_results = patch_delete(entry)
                        else:
                            operation_results = ['[FAIL]\tUnrecognized operation \'{}\' for entry index {} in patch file {}'.format(operation, index, file)]
                            operation = 'unknown'

                        if not operations.get(operation):
                            operations[operation] = []

                        for operation_result in operation_results:
                            operations[operation].append(operation_result)

                        index = index + 1

    return operations


def patch_replace(entry):
    try:
        sheet_exported_path = EXPORTS_PATH.joinpath(entry['source'] + '.png')

        sheet_existing = Image.open(RESOURCES_EXISTING_SHEETS_PATH.joinpath(entry['source'] + '.png'))
        sheet_exported = Image.open(sheet_exported_path)

        x = entry['source_x'] * 128
        y = entry['source_y'] * 256

        sheet_existing = sheet_existing.crop((x, y, x + (entry['width'] * 128), y + (entry['height'] * 256)))
        sheet_exported.paste(sheet_existing, (x, y))
        sheet_exported.save(sheet_exported_path)

        sheet_existing.close()
        sheet_exported.close()

        return ['[PASS]\tSheet {} recieved replacement starting at cell coordinates ( {} , {} )'.format(entry['source'], entry['source_x'], entry['source_y'])]
    except:
        return ['[FAIL]\tSheet {} caused exception: {}'.format(sys.exc_info()[0])]


def patch_delete(entry):
    results = []
    for target in entry['targets']:
        try:
            EXPORTS_PATH.joinpath(target + '.png').unlink()
            results.append('[PASS]\tSheet {} deleted'.format(target))
        except:
            results.append('[FAIL]\tSheet {} caused exception: {}'.format(sys.exc_info()[0]))

    return results


if __name__ == '__main__':
    # Change this to True in order to rerun operation on unpacked files within resources folder.
    main(True)

