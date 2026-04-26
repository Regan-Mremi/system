import win32print
import datetime


def print_order(order):
    try:
        # Get default printer
        PRINTER_NAME = win32print.GetDefaultPrinter()
        print("Using printer:", PRINTER_NAME)

        hPrinter = win32print.OpenPrinter(PRINTER_NAME)

        # Start document
        win32print.StartDocPrinter(hPrinter, 1, ("Cafe Receipt", None, "RAW"))
        win32print.StartPagePrinter(hPrinter)

        # Initialize printer (ESC/POS)
        win32print.WritePrinter(hPrinter, b'\x1b\x40')

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        receipt = ""
        receipt += "    Swahili AMELL BUFFET\n"
        receipt += "------------------------------\n"
        receipt += f"Order No : {order.id}\n"
        receipt += f"Date     : {now}\n"
        receipt += "------------------------------\n"

        total = 0

        # Print items
        for item in order.orderitem_set.all():
            name = item.item.name
            qty = item.quantity
            price = item.item.price
            subtotal = item.subtotal()

            receipt += f"{name}\n"
            receipt += f"{qty} x {price} = {subtotal}\n"

            total += subtotal

        receipt += "------------------------------\n"
        receipt += f"TOTAL: {total}\n"
        receipt += "------------------------------\n"
        receipt += "\nThank you!\n\n\n"

        # Send text to printer
        win32print.WritePrinter(hPrinter, receipt.encode("ascii"))

        # Cut paper
        win32print.WritePrinter(hPrinter, b'\x1d\x56\x41\x10')

        # End printing
        win32print.EndPagePrinter(hPrinter)
        win32print.EndDocPrinter(hPrinter)
        win32print.ClosePrinter(hPrinter)

        print("PRINT SUCCESS")

    except Exception as e:
        print("PRINT ERROR:", e)



        