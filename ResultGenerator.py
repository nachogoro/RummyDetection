import os
from operator import attrgetter
from enum import Enum

LETTER_FOR_COLOR = {'BLACK': 'K', 'BLUE': 'B', 'ORANGE': 'O', 'PINK': 'P'}

class Group(Enum):
    TRIO = 1
    STAIR = 2
    UNCERTAIN = 3
    INVALID = 4

def _group_tiles_spacially(tiles):
    bin_size = int(max([t.intHeight for t in tiles])/2)
    by_height = {}
    for tile in tiles:
        added = False
        for y_pos in by_height.keys():
            if y_pos - bin_size < tile.intCenterY < y_pos + bin_size:
                by_height[y_pos].append(tile)
                added = True
                break
        if not added:
            by_height[tile.intCenterY] = [tile]

    # by_height contains the list of tiles which have the same height, now we
    # need to sort them from left to right
    for height, tiles in by_height.items():
        by_height[height] = sorted(tiles, key=attrgetter('intCenterX'))

    result = []
    for key in sorted(by_height.keys()):
        result.append(by_height[key])
    return result


def _deduct_group_type(group):
    all_colors = [tile.color for tile in group if tile.value != 'j']
    all_colors_set = set(all_colors)
    seen_numbers = [tile.value for tile in group]
    seen_numbers_set = set(seen_numbers)
    non_jokers = len(all_colors)

    if non_jokers <= 1:
        return Group.UNCERTAIN

    if len(all_colors_set) == 1:
        # Either a stair or invalid
        first_reg = next(x for x in group if x.value != 'j')
        first_val = int(first_reg.value)
        next_val = first_val + 1 if first_val != 13 else 1
        index = group.index(first_reg)

        wraps_around = False
        if next_val < first_val or index > first_val-1:
            wraps_around = True

        for i, tile in enumerate(group[index+1:]):
            if tile.value == 'j' or int(tile.value) == next_val:
                next_val = next_val + 1 if next_val != 13 else 1
                if next_val == 1 and i + 1 < len(group) - (index+1):
                    wraps_around = True
            else:
                return Group.INVALID

        # If a stair contains a '1', it can only be either at the beginning or
        # the end
        if (len(group) > 13
                or (wraps_around and not (
                    group[-1].value == '1'
                    or group[-1].value == 'j' and group[-2].value == '13'
                    or group[-2].value == 'j' and group[-3].value == '12'))):
            return Group.INVALID

        return Group.STAIR

    elif (len(all_colors) == len(all_colors_set)
            and len(group) <= 4
            and len(seen_numbers_set - {'j'}) == 1):
        return Group.TRIO
    else:
        return Group.INVALID


def _group_tiles_in_trios_and_stairs(tiles_by_height):
    result = []
    error = False
    for line in tiles_by_height:
        while line:
            current_group = []
            current_group_type = Group.UNCERTAIN

            for tile in line:
                if not current_group:
                    current_group.append(tile)
                    continue

                if tile.intCenterX - current_group[-1].intCenterX < 2*tile.intHeight:
                    # They are close enough that they could be part of the same
                    # group
                    g_type = _deduct_group_type(current_group + [tile])
                    if g_type != Group.INVALID:
                        current_group.append(tile)
                        current_group_type = g_type
                    else:
                        break
                else:
                    break

            line = [t for t in line if t not in current_group]
            if (current_group_type == Group.INVALID or len(current_group) < 3
                    and not error):
                print('ERROR GROUPING TILES, DOUBLE CHECK THE OUTPUT')
                error = True
            result.append(current_group)
    return result


def write_deck(tiles, output_dir):
    output = []

    # We order them before printing to make debugging easier
    tiles = [tile for line in _group_tiles_spacially(tiles) for tile in line]

    for tile in tiles:
        if tile.value == 'j':
            output.append('J')
        else:
            output.append('%c%d' % (LETTER_FOR_COLOR[tile.color],
                                    int(tile.value)))

    if output_dir:
        with open(os.path.join(output_dir, 'deck.txt'), 'w') as out_file:
            for line in output:
                print(line, file=out_file)
    else:
        for line in output:
            print(line)


def write_table(tiles, output_dir):
    # We need to group the tiles into hands and runs (trios and stairs). For
    # that, we first sort them from top to bottom and from left to right
    sorted_tiles = _group_tiles_spacially(tiles)

    grouped_tiles = _group_tiles_in_trios_and_stairs(sorted_tiles)
    output = []

    for group in grouped_tiles:
        group_str = ''
        for tile in group:
            if tile.value == 'j':
                group_str += 'J '
            else:
                group_str += '%c%d ' % (LETTER_FOR_COLOR[tile.color],
                                        int(tile.value))
        output.append(group_str.rstrip())

    if output_dir:
        with open(os.path.join(output_dir, 'table.txt'), 'w') as out_file:
            for line in output:
                print(line, file=out_file)
    else:
        for line in output:
            print(line)
