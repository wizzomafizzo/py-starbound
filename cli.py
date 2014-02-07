#!/usr/bin/env python

import optparse
import struct
import sys

import starbound
import starbound.sbbf02
import starbound.sbon

def print_leaves(file, block_number=None, depth=0, prefix=None):
    """Prints out the full B-tree of accessible leaves"""

    if block_number is None:
        block_number = file.root_block
    block = file.get_block(block_number)

    sys.stdout.write('   ' * depth)
    if prefix:
        sys.stdout.write(prefix + ': ')
    print block, '@', block_number

    if isinstance(block, starbound.sbbf02.StarBlockIndex):
        for index, block_reference in enumerate(block.values):
            if index == 0:
                key_hex = '^' * file.key_size * 2
            else:
                key_hex = block.keys[index - 1].encode('hex')

            print_leaves(file, block_reference, depth + 1, prefix=key_hex)

    if isinstance(block, starbound.sbbf02.StarBlockLeaf):
        stream = starbound.sbbf02.LeafReader(file, block)
        num_keys, = struct.unpack('>i', stream.read(4))
        for _ in xrange(num_keys):
            cur_key = stream.read(file.key_size)
            value_length = starbound.sbon.read_varlen_number(stream)
            value = stream.read(value_length)
            sys.stdout.write('    ' * (depth + 1))
            print cur_key.encode('hex'), '=', len(value), 'byte(s)'

def get_value(file, key_path):
    """Get a value out of the file's metadata"""

    if isinstance(file, starbound.StarFileSBVJ01):
        data = file.data
    elif isinstance(file, starbound.StarWorld):
        data = file.get_world_data()
    else:
        raise ValueError('--get-value requires a player or world file')

    key_parts = key_path.split('.')
    for key in key_parts:
        data = data[key]
    print key_path, '=', data


def main():
    p = optparse.OptionParser()

    p.add_option('-g', '--get-value', dest='get_value',
                 help=get_value.__doc__)

    p.add_option('-l', '--print-leaves', dest='print_leaves',
                 action='store_true', default=False,
                 help=print_leaves.__doc__)

    options, arguments = p.parse_args()

    for path in arguments:
        with starbound.open_file(path) as file:
            print file
            print

            if options.get_value:
                get_value(file, options.get_value)
                print

            if options.print_leaves:
                print_leaves(file)
                print

if __name__ == '__main__':
    main()