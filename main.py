import xml.etree.ElementTree as ElementTree
import argparse
import sys

SAVE_LENGTH = 0x550
BASE_ADDR = 0xC5B0

DATATYPE_INVALID = -1
DATATYPE_BYTE = 0
DATATYPE_WORD = 1
DATATYPE_BYTE_BCD = 2
DATATYPE_WORD_BCD = 3
DATATYPE_STRING = 4
DATATYPE_BIT = 5
DATATYPE_BITS = 6
DATATYPE_BYTE_ARRAY = 7

GAMETYPE_SEASONS = 0,
GAMETYPE_AGES = 1,
GAMETYPE_INVALID = 2


def load_items(filename="ages.xml"):
    items = []
    tree = ElementTree.parse(filename)
    root = tree.getroot()
    for section in root.findall('section'):
        section_name = section.get('name')
        for item in section.findall('item'):
            i = {
                'section': section_name,
            }
            for e in item.iter():
                if e.tag == 'item':
                    continue

                if e.tag in ('addr', 'agesaddr', 'ssnsaddr'):
                    i[e.tag] = int(e.text, 16) - BASE_ADDR
                elif e.tag in ('max', 'length', 'firstbit', 'lastbit'):
                    i[e.tag] = int(e.text, 16)
                elif e.tag == 'datatype':
                    datatype = DATATYPE_INVALID

                    if e.text.upper() == 'BYTE':
                        datatype = DATATYPE_BYTE
                    elif e.text.upper() == 'WORD':
                        datatype = DATATYPE_WORD
                    elif e.text.upper() == 'BYTE BCD':
                        datatype = DATATYPE_BYTE_BCD
                    elif e.text.upper() == 'WORD BCD':
                        datatype = DATATYPE_WORD_BCD
                    elif e.text.upper() == 'STRING':
                        datatype = DATATYPE_STRING
                    elif e.text.upper() == 'BIT':
                        datatype = DATATYPE_BIT
                    elif e.text.upper() == 'BITS':
                        datatype = DATATYPE_BITS

                    i['datatype'] = datatype
                else:
                    i[e.tag] = e.text
            items += [i, ]

    # cleanup bit with firstbit > 7
    for item in items:
        if item.get('datatype') in (DATATYPE_BIT, DATATYPE_BITS):
            first_bit = item.get('firstbit', None)
            if first_bit is None:
                raise ValueError('firstbit is not allowed to be None!')
            if first_bit > 7:
                byte = first_bit // 8

                item['firstbit'] = first_bit % 8
                if 'addr' in item:
                    item['addr'] = item['addr'] + byte
                if 'agesaddr' in item:
                    item['agesaddr'] = item['agesaddr'] + byte
                if 'ssnsaddr' in item:
                    item['ssnsaddr'] = item['ssnsaddr'] + byte

                if 'lastbit' in item:
                    item['lastbit'] = item['lastbit'] - (byte * 8)

    # add Known Bytes
    items += [
        {
            'section': 'Header',
            'name': 'Checksum',
            'addr': 0x00,
            'datatype': DATATYPE_WORD,
        },
        {
            'section': 'Header',
            'name': 'GameType Identifier',
            'addr': 0x02,
            'length': 0xd,
            'datatype': DATATYPE_STRING,
        },
        {
            'section': 'Main',
            'name': 'wUnappraisedRings',
            'addr': 0x10,
            'length': 0x40,
            'datatype': DATATYPE_BYTE_ARRAY,
            'hint': 'List of unappraised rings. each byte always seems to have bit 6 set, indicating that the'
                    ' ring is unappraised. It probably gets unset the moment you appraise it, but only for'
                    ' a moment because then it disappears from this list.',
        },

        {
            'section': 'Main',
            'name': 'Dummy Value (always 1)',
            'addr': 0x58,
            'datatype': DATATYPE_BYTE,
        },
        {
            'section': 'Main',
            'name': 'wWhichGame',
            'addr': 0x61,
            'datatype': DATATYPE_BYTE,
        },
        {
            'section': 'Main',
            'name': 'wRingsObtained',
            'addr': 0x66,
            'length': 0x8,
            'datatype': DATATYPE_BYTE_ARRAY,
        },
        {
            'section': 'Main',
            'name': 'wPlaytimeCounter',
            'addr': 0x72,
            'length': 0x4,
            'datatype': DATATYPE_BYTE_ARRAY,
        },
        {
            'section': 'Respawn',
            'name': 'Link object index',
            'addr': 0x84,
            'datatype': DATATYPE_BYTE,
        },
        {
            'section': 'Respawn',
            'name': '0xC635',
            'addr': 0x85,
            'datatype': DATATYPE_BYTE,
        },
        {
            'section': 'Respawn',
            'name': 'wMinimapGroup',
            'addr': 0x8a,
            'length': 0x4,
            'datatype': DATATYPE_BYTE_ARRAY,
        },
        {
            'section': 'Inventory',
            'name': 'wInventoryA',
            'addr': 0xd8,
            'datatype': DATATYPE_BYTE,
        },
        {
            'section': 'Inventory',
            'name': 'wInventoryB',
            'addr': 0xd9,
            'datatype': DATATYPE_BYTE,
        },
        {
            'section': 'Inventory',
            'name': 'wInventoryStorage',
            'addr': 0xda,
            'length': 0x10,
            'datatype': DATATYPE_BYTE_ARRAY,
        },
        {
            'section': 'Inventory',
            'name': 'wObtainedTreasureFlags',
            'addr': 0xea,
            'length': 0x10,
            'datatype': DATATYPE_BYTE_ARRAY,
        },


        {
            'section': 'Health',
            'name': 'wRingBoxContents',
            'addr': 0x116,
            'length': 0x5,
            'datatype': DATATYPE_BYTE_ARRAY,
        },




        {
            'section': 'Secrets',
            'name': 'Missing Secret Flags',
            'addr': 0x14f,
            'datatype': DATATYPE_BYTE,
        },

        {
            'section': 'Map',
            'name': 'Present Map Flags',
            'addr': 0x150,
            'length': 0x100,
            'datatype': DATATYPE_BYTE_ARRAY,
        },
        {
            'section': 'Map',
            'name': 'Past Map Flags',
            'addr': 0x250,
            'length': 0x100,
            'datatype': DATATYPE_BYTE_ARRAY,
        },
        {
            'section': 'Map',
            'name': 'Group 4 Map Flags',
            'addr': 0x350,
            'length': 0x100,
            'datatype': DATATYPE_BYTE_ARRAY,
        },
        {
            'section': 'Map',
            'name': 'Group 5 Map Flags',
            'addr': 0x450,
            'length': 0x100,
            'datatype': DATATYPE_BYTE_ARRAY,
        },
    ]

    return items


def find_unknown_addresses(items, game_type=GAMETYPE_AGES):
    known_adresses = {}

    for x in items:
        addr = x.get('addr', x.get('agesaddr' if game_type == GAMETYPE_AGES else 'ssnsaddr', 0x00))

        width = 1
        if x.get('datatype', DATATYPE_INVALID) in (DATATYPE_WORD, DATATYPE_WORD_BCD):
            width = 2
        elif x.get('datatype', DATATYPE_INVALID) in (DATATYPE_STRING, DATATYPE_BYTE_ARRAY):
            width = x.get('length') + 1

        for i in range(width):
            known_adresses[addr + i] = True

    known_adresses = [k for k in known_adresses.keys() if known_adresses[k]]
    unknown_adresses = [u for u in range(SAVE_LENGTH) if u not in known_adresses]

    return unknown_adresses


def load_save(filename, index):
    with open(filename, 'rb') as f:
        f.seek(16 + index * SAVE_LENGTH)
        save_raw = f.read(SAVE_LENGTH)

    save = [int(b) for b in save_raw]
    return save


def parse_save_with_items(save_raw, items=None, game_type=GAMETYPE_AGES):
    if items is None:
        raise ValueError('items needs to be set')

    crc = calculate_checksum(save_raw)
    file_crc = save_raw[0] | save_raw[1] << 8
    if crc != file_crc:
        raise ValueError(f'CRC invalid {hex(crc)} vs {hex(file_crc)}')

    save_game_type = ''
    for i in range(8):
        save_game_type += chr(save_raw[2 + i])

    if (save_game_type == "Z11216-0" and game_type != GAMETYPE_SEASONS) \
            or (save_game_type == "Z21216-0" and game_type != GAMETYPE_AGES):
        raise ValueError('gametype not correct')

    save = {}
    for item in items:
        name = item.get('name')
        data_type = item.get('datatype', DATATYPE_INVALID)
        addr = item.get('addr', item.get('agesaddr' if game_type == GAMETYPE_AGES else 'ssnsaddr', 0x00))

        if data_type in (DATATYPE_BYTE, DATATYPE_BYTE_BCD):
            save[name] = save_raw[addr]
        elif data_type in (DATATYPE_WORD, DATATYPE_WORD_BCD):
            save[name] = save_raw[addr] | save_raw[addr + 1] << 8
        elif data_type == DATATYPE_STRING:
            save[name] = ''
            for pos in range(item.get('length')):
                save[name] += chr(save_raw[addr + pos])
            save[name] = save[name].rstrip('\00')
        elif data_type == DATATYPE_BYTE_ARRAY:
            save[name] = []
            for pos in range(item.get('length')):
                save[name] += [save_raw[addr + pos], ]
        elif data_type in (DATATYPE_BIT, DATATYPE_BITS):
            first_bit = item.get('firstbit', 0)
            last_bit = item.get('lastbit', first_bit)

            mask = 0
            for b in range(first_bit, last_bit + 1):
                mask += 1 << b

            if data_type == DATATYPE_BIT:  # This is Boolean
                save[name] = (save_raw[addr] & mask) > 0
            else:  # else we generate Int with this bits
                save[name] = (save_raw[addr] & mask) >> first_bit
        else:
            raise ValueError(f'DATATYPE {data_type} is unknown for {name}')

    return save


def sort_by_addr(item, game_type=GAMETYPE_AGES):
    return item.get('addr', item.get('agesaddr' if game_type == GAMETYPE_AGES else 'ssnsaddr', 0xFFF))


def print_parsed_save(save, items, game_type=GAMETYPE_AGES):
    old_section = ''
    max_len = max([len(x.get('name')) for x in items])
    for item in sorted(items, key=sort_by_addr):
        section = item.get('section', '')
        if section != old_section:
            print(f'\n**** {section} ****')
            old_section = section

        name = item.get('name')
        value = save.get(name)
        addr = item.get('addr', item.get('agesaddr' if game_type == GAMETYPE_AGES else 'ssnsaddr', 0xFFF))

        if addr == 0xfff:
            continue

        if isinstance(value, bool):
            value = str(value)
        elif isinstance(value, int):
            value = hex(value)
        elif isinstance(value, list):
            v = []
            size = 32
            for i in range(0, len(value), size):
                part_list = value[i:i+size]
                padding = 3 * (size - len(part_list))
                if len(part_list) <= size // 2:
                    padding -= 1
                v += [' '.join(['{:02x}'.format(x) for x in part_list[:size//2]]) + '  ' +
                      ' '.join(['{:02x}'.format(x) for x in part_list[size//2:]]) + ' ' +
                      ' ' * padding + ' | ' +
                      ''.join([chr(x) if x < 0x80 and chr(x).isprintable() else '.' for x in part_list]), ]

            value = ('\n' + ' ' * (max_len + 14)).join(v)
        else:
            value = str(value)

        print(f'(0x{hex(addr)[2:].zfill(4)}) {name}: ' + '.' * (max_len - len(name) + 2) + ' ' + value)


def calculate_checksum(save_raw):
    checksum = 0

    for i in range(2, SAVE_LENGTH, 2):
        checksum += save_raw[i] | save_raw[i+1] << 8
        checksum = checksum & 0xFFFF

    return checksum


def main(args):
    items = load_items("fields.xml")

    print(f"SAVEFILE {args.index}")
    save = load_save(args.save, args.index)
    print_parsed_save(parse_save_with_items(save, items), items)

    u = find_unknown_addresses(items)
    if len(u):
        print()
        print(f'{len(u)} unknown Adresses:')
        print([hex(x) for x in u])
        # print([hex(x) + ' ' + hex(x + BASE_ADDR) for x in u])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Show Oracle of Ages/Seasons Savegame.')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('-i', '--index', default=0, type=int, help='Save Slot to show.')

    parser.add_argument('save', type=str, metavar="<SaveGame>", help='Savegame to view.')
    sys.exit(main(parser.parse_args()))

