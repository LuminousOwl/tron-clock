import board
import rp2pio
import adafruit_pioasm

class AD7302:
    def __init__(self):
        # side !LDAC A/B !WR
        dac = """
            .program dac_out_1
            .side_set 3

            .wrap_target
            start:
            out pins 8     side 0b101 ; output a
            nop            side 0b100 ; wr low
            nop            side 0b101 ; wr high

            out pins 8     side 0b111 ; output b
            nop            side 0b110 ; wr low
            nop            side 0b111 ; wr high

            out x 16       side 0b001 ; ldac low

            jmp !x start   side 0b101 ; ldac high

            brightness:               ; loop for relative brightness
                nop [3]
                jmp x-- brightness [3]

            .wrap
        """

        self._state_machine = rp2pio.StateMachine(
            adafruit_pioasm.assemble(dac),
            frequency=125_000_000,
            first_out_pin=board.GP0,
            out_pin_count=8,
            first_sideset_pin=board.GP8,
            sideset_pin_count=3,
            auto_pull=True,
            pull_threshold=32
        )

    def write(self, draw_buff, byte_count):
        mv = memoryview(draw_buff).cast('L')[0:int(byte_count / 4)]
        self._state_machine.background_write(loop=mv)

