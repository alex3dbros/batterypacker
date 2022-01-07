from phomemo_printer.ESCPOS_printer import Printer
from PIL import Image, ImageFont, ImageDraw
from phomemo_printer.ESCPOS_constants import *
import qrcode


class Phomemo(Printer):

    def print_label(self, image, width, height):
        """
            Print an label

            Args:
                image (pil image)
                width (int) width of the label
                height (int) height of the label
        """

        IMAGE_WIDTH_BYTES = width
        IMAGE_WIDTH_BITS = IMAGE_WIDTH_BYTES * 8

        IMAGE_HEIGHT_BYTES = height
        IMAGE_HEIGBT_BITS = IMAGE_HEIGHT_BYTES * 8

        image = image.resize(
            size=(IMAGE_WIDTH_BITS, IMAGE_HEIGBT_BITS)
        )

        print(image.width)

        # black&white printer: dithering
        image = image.convert(mode="1")

        self._print_bytes(HEADER)
        for start_index in range(0, image.height, 256):
            end_index = (
                start_index + 256 if image.height - 256 > start_index else image.height
            )
            line_height = end_index - start_index

            BLOCK_MARKER = (
                    GSV0
                    + bytes([IMAGE_WIDTH_BYTES])
                    + b"\x00"
                    + bytes([line_height - 1])
                    + b"\x00"
            )
            self._print_bytes(BLOCK_MARKER)

            image_lines = []
            for image_line_index in range(line_height):
                image_line = b""
                for byte_start in range(int(image.width / 8)):
                    byte = 0
                    for bit in range(8):
                        if (
                                image.getpixel(
                                    (byte_start * 8 + bit, image_line_index + start_index)
                                )
                                == 0
                        ):
                            byte |= 1 << (7 - bit)
                    # 0x0a breaks the rendering
                    # 0x0a alone is processed like LineFeed by the printe
                    if byte == 0x0A:
                        byte = 0x14
                    # self._print_bytes(byte.to_bytes(1, 'little'))
                    image_line += byte.to_bytes(1, "little")

                image_lines.append(image_line)

            for l in image_lines:
                self._print_bytes(l)


def print_label(cells, printer_address):
    for cell in cells:
        send_to_printer(cell["id"], cell["capacity"], cell["esr"], cell["voltage"], cell["device"], cell["uuid"], printer_address)


def send_to_printer(serial_number, capacity, esr, charge_volt, dev_name, qr_content, printer_address):
    printer = Phomemo(bluetooth_address=printer_address, channel=1)
    phomemo_label = Image.open("../labeltemplates/phomemo_blank_30x20.jpg")
    label_editable = ImageDraw.Draw(phomemo_label)

    # The header content and font
    header_font = ImageFont.truetype('../labeltemplates/fonts/OpenSans-Bold.ttf', 62)
    header_text = "%s-C:%s" % (serial_number, capacity)
    label_editable.text((9, 0), header_text, (0, 0, 0), font=header_font)

    # Left Values E: (Internal Resistance); Discharge Voltage, Store Voltage, Charge Voltage ; Device Name used for testing
    left_values_font = ImageFont.truetype('../labeltemplates/fonts/OpenSans-Regular.ttf', 42)
    left_values = "E: %s\n%s\nDev:%s" % (esr, charge_volt, dev_name)
    label_editable.text((9, 100), left_values, (0, 0, 0), font=left_values_font)

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=5)

    qr.add_data(qr_content)
    qr.make(fit=True)
    qr_img = qr.make_image(fill='black', back_color='white')
    qr_img = qr_img.crop((0, 0, 350, 350))
    qr_img = qr_img.resize((150, 150))

    phomemo_label.paste(qr_img, (290, 90))

    printer.print_label(phomemo_label, 30, 20)
