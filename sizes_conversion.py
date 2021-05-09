import re

class ClothingConversion:
    def __init__(self, json):
        self.json = json
        self.ITALY_TO_SML = {'42': 'XXS', '44': 'XS', '46': 'S', '48': 'M',
                             '50': 'L', '52': 'XL', '54': 'XXL', '56': 'XXXL',
                             '58': '4XL', '60': '5XL'}

        self.MONCLER_TO_SML = {'00': 'XXS', '0': 'XS', '1': 'M', '2': 'L', '3': 'M/L', '4': 'XL', '5': 'XL/XXL',
                               '6': 'XXL',
                               '7': '3XL', '8': '4XL'}

    def convert(self, sizes_lists, sizes_dict):
        converted_sizes = []
        for size in sizes_lists:

            try:
                size = re.findall('\d+', size)[0]
            except:
                pass

            try:
                converted_sizes.append(sizes_dict[size])
            except:
                continue

        return converted_sizes


class ShoesConversion:
    def __init__(self, json):
        self.json = json
        self.ITALY_TO_UK = {
            '38': '4', '39': '5', '39.5': '5.5', '40': '6',
            '40.5': '6.5', '41': '7', '41.5': '7.5', '42': '8',
            '42.5': '8.5', '43': '9', '43.5': '9.5', '44': '10',
            '44.5': '10.5', '45': '11', '45.5': '11.5', '46': '12',
            '46.5': '12.5', '47': '13', '47.5': '13.5'
        }

        self.USA_TO_UK = {
            '5': '4', '6': '5', '6.5': '5.5', '7': '6',
            '7.5': '6.5', '8': '7', '8.5': '7.5', '9': '8',
            '9.5': '8.5', '10': '9', '10.5': '9.5', '11': '10',
            '11.5': '10.5', '12': '11', '12.5': '11.5', '13': '12',
            '13.5': '12.5', '14': '13', '14.5': '13.5'
        }

        self.FRANCE_TO_UK = self.ITALY_TO_UK

    def convert(self, sizes_lists, sizes_dict):
        converted_sizes = []
        for size in sizes_lists:
            try:
                converted_sizes.append(sizes_dict[size])
            except:
                continue

        return converted_sizes


def convert_sizes(json):
    object_type = json['object_type']
    size_type = json['size_type']
    sizes = json['sizes']

    if object_type == 'Clothing' and size_type is not None:
        object = ClothingConversion(json)

        if 'IT' in size_type:
            return {
                'object_type': object_type,
                'size_type': 'S/M/L',
                'sizes': object.convert(sizes, object.ITALY_TO_SML)
            }

        elif 'Jeans' in size_type:
            return json

        elif 'S/M/L' in size_type:
            return json

        elif 'UK' in size_type:
            return json

        elif 'CM' in size_type:
            return json

        elif 'moncler' in size_type.lower():
            return {
                'object_type': object_type,
                'size_type': 'S/M/L',
                'sizes': object.convert(sizes, object.MONCLER_TO_SML)
            }

    elif object_type == 'Shoes' and size_type is not None:
        object = ShoesConversion(json)

        if 'UK' in size_type:
            return json

        elif 'IT' in size_type:
            return {
                'object_type': object_type,
                'size_type': 'UK',
                'sizes': object.convert(sizes, object.ITALY_TO_UK)
            }

        elif 'USA' in size_type or 'US' in size_type:
            return {
                'object_type': object_type,
                'size_type': 'UK',
                'sizes': object.convert(sizes, object.USA_TO_UK)
            }

    elif object_type == 'Jeans':
        if 'IT' in size_type:
            return {
                'object_type': object_type,
                'size_type': 'IT',
                'sizes': sizes
            }

    else:
        return json


if __name__ == '__main__':
    print('Not supported')
