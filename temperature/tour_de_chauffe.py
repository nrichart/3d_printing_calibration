#!/usr/bin/env python3
import click


class Layers:
    def __init__(self, gcode):
        self._gcode = gcode
        self._iter = iter(gcode)
        self._end = False

    def __iter__(self):
        return self

    def __next__(self):
        lines = []

        if self._end:
            raise StopIteration

        while True:
            try:
                line = next(self._iter)
            except StopIteration:
                self._end = True
                return [None, lines]

            lines.append(line)
            if line == ";BEFORE_LAYER_CHANGE\n":
                line = next(self._iter)
                lines.append(line)

                z = float(line[1:-1])

                return [z, lines]


@click.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--offset', default=0, help='Offset in mm to start')
@click.option('--block_height', default=10,
              help='Size of mm of each temperature block')
@click.option('--max_temp', default=230, help='Max temperature')
@click.option('--step', default=5, help='Temperature steps')
def tweak_temperature(file, offset, block_height, max_temp, step):
    """Tweak the temperature at Z changes"""
    with open(file, 'r') as fh:
        lines = fh.readlines()

    temp = max_temp
    temp_change_z = offset
    with open(file, 'w') as fh:
        for z, gcode in Layers(lines):
            fh.writelines(gcode)

            if z is not None and z - temp_change_z >= 0.:
                print(f'{z} -> {temp}')
                fh.write(f'M104 S{temp}\n')
                temp = temp - step
                temp_change_z = temp_change_z + block_height


if __name__ == '__main__':
    tweak_temperature()
