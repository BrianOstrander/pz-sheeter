class SheetEntry:

    def __init__(self, xml, root_asset_path):
        self.xml = xml
        self.index = None
        self.sheet = None
        self.asset_path = None
        self.offset_x = 0
        self.offset_y = 0
        self.width = 0
        self.height = 0

        # XCoord
        # XOffset
        # YOffset
        # actualHeight
        # actualWidth
        # height
        # name
        # nameSize
        # width

        for property in xml:
            property_name = property['@property']

            if property_name == 'name':
                name_raw = property['string']
                self.asset_path = root_asset_path.joinpath(name_raw + '.png')

                if name_raw[-1].isdigit():
                    if '_' in name_raw:
                        self.index = name_raw.split('_')[-1]
                        self.sheet = name_raw[:((len(self.index) + 1) * -1)]
                    else:
                        self.index = 0
                        self.sheet = name_raw
                else:
                    self.index = 0
                    self.sheet = name_raw
            elif property_name == 'XOffset':
                self.offset_x = int(property['int'])
            elif property_name == 'YOffset':
                self.offset_y = int(property['int'])
            elif property_name == 'width':
                self.width = int(property['int'])
            elif property_name == 'height':
                self.height = int(property['int'])