from os import environ
import logging
import requests
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import matplotlib.colors as mcolors
import io
from cartesi_wallet.util import hex_to_str, str_to_hex
import json
import base64
from eth_abi import encode, decode
import hashlib

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

rollup_server = environ["ROLLUP_HTTP_SERVER_URL"]
logger.info(f"HTTP rollup_server url is {rollup_server}")

creator_image_mapping = {}
def map_image_to_creator(user_address, image_hash):
    creator_image_mapping[user_address] = image_hash

def binary2hex(binary):
    """
    Encode a binary as an hex string
    """
    return "0x" + binary.hex()

# CLASSIC MANDELBROT ALGORITHM
def generate_mandelbrot_fractal(width, height, max_iterations, xmin, xmax, ymin, ymax):
    # Initialize the fractal image
    fractal = np.zeros((height, width))

    # Calculate pixel size
    dx = (xmax - xmin) / (width - 1)
    dy = (ymax - ymin) / (height - 1)

    # Generate the Mandelbrot fractal
    for y in range(height):
        for x in range(width):
            # Map pixel coordinates to the complex plane
            cx = xmin + x * dx
            cy = ymin + y * dy

            # Initialize z
            zx = 0.0
            zy = 0.0

            # Iterate the Mandelbrot function
            for i in range(max_iterations):
                # Calculate z^2
                zx2 = zx * zx
                zy2 = zy * zy

                # Check for overflow
                if zx2 + zy2 > 4.0:
                    break

                # Calculate new z value
                zy = 2.0 * zx * zy + cy
                zx = zx2 - zy2 + cx

            # Assign color based on iteration count
            fractal[y, x] = i

    return fractal

# BURNING SHIP EQUATION
def generate_burning_ship_fractal(width, height, max_iterations, xmin, xmax, ymin, ymax):
    # Initialize the fractal image
    fractal = np.zeros((height, width))

    # Calculate pixel size
    dx = (xmax - xmin) / (width - 1)
    dy = (ymax - ymin) / (height - 1)

    # Generate the Burning Ship fractal
    for y in range(height):
        for x in range(width):
            # Map pixel coordinates to the complex plane
            cx = xmin + x * dx
            cy = ymin + y * dy

            # Initialize z
            zx = 0.0
            zy = 0.0

            # Iterate the Burning Ship function
            for i in range(max_iterations):
                # Calculate z^2
                zx2 = zx * zx
                zy2 = zy * zy

                # Check for overflow
                if zx2 + zy2 > 4.0:
                    break

                # Calculate new z value
                zy = abs(2.0 * zx * zy) + cy
                zx = zx2 - zy2 + cx

            # Assign color based on iteration count
            fractal[y, x] = i

    return fractal


def generate_svg_from_fractal(fractal, xmin, xmax, ymin, ymax, background_color="#FFFFFF", fractal_colors=["#000000"], fractal_cmap="inferno"):
    # Convert the fractal to a matplotlib figure
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_facecolor(background_color)  # Set background color

    # Customize the colormap if provided
    if len(fractal_colors) > 1:
        cmap = mcolors.ListedColormap(fractal_colors)
    else:
        cmap = fractal_cmap

    ax.imshow(fractal, cmap=cmap, extent=[xmin, xmax, ymin, ymax])
    ax.axis('off')

    # Save the figure as SVG string
    svg_buffer = io.StringIO()
    plt.savefig(svg_buffer, format='svg', bbox_inches='tight', pad_inches=0)
    plt.close(fig)

    # Get the SVG data from the buffer
    svg_data = svg_buffer.getvalue()

    return svg_data

def generate_base64_from_fractal(fractal, xmin, xmax, ymin, ymax, background_color="#FFFFFF", fractal_colors=["#000000"], fractal_cmap="inferno"):
    # Convert the fractal to a matplotlib figure
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_facecolor(background_color) 

    # Customize the colormap if provided
    if len(fractal_colors) > 1:
        cmap = mcolors.ListedColormap(fractal_colors)
    else:
        cmap = fractal_cmap

    ax.imshow(fractal, cmap=cmap, extent=[xmin, xmax, ymin, ymax])
    ax.axis('off')

    # Save the figure as a buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', pad_inches=0)
    plt.close(fig)

    # Get the base64 encoded data from the buffer
    base64_data = base64.b64encode(buffer.getvalue()).decode()

    return base64_data

def handle_advance(data):
    logger.info(f"Received advance request data {data}")

    if msg_sender.lower() == "0xF5DE34d6BbC0446E2a45719E718efEbaaE179daE".lower():
        global rollup_address
        logger.info(f"Received advance from dapp relay")
        rollup_address = payload
        response = requests.post(rollup_server + "/notice", json={"payload": str_to_hex(f"Set rollup_address {rollup_address}")})
        return "accept"

    width = 800
    height = 800

    # Check inputs: define max width, height
    # Extract information from the data
    msg_sender = data["metadata"]["msg_sender"]
    payload = hex_to_str(data["payload"])
    logger.info(f"Payload: {payload}")
    payload = json.loads(payload)
    theme = payload.get("theme", {})
    max_iterations = int(payload.get("iterations", "100"))
    colors = theme.get("colors", {})
    plot = payload.get("plot", {})
    xmin = float(plot.get("xmin", "-1"))
    xmax = float(plot.get("xmax", "1"))
    ymin = float(plot.get("ymin", "-1"))
    ymax = float(plot.get("ymax", "1"))
    logger.info(f"theme: {theme} \n colors: {colors}")
    background_color = theme.get("background_color", "#FFFFFF") 

    # Extract color codes for the fractal
    fractal_colors = colors.get("fractal", ["#000000"])  
    fractal_cmap = colors.get("cmap", "inferno")
    equation = payload.get("equation")
    logger.info(f"Equation is: {equation}")
    if equation == "mandelbrot":
        fractal = generate_mandelbrot_fractal(width, height, max_iterations, xmin, xmax, ymin, ymax)
    elif equation == "burning_ship":
        fractal = generate_burning_ship_fractal(width, height, max_iterations, xmin, xmax, ymin, ymax)
    else:
        logger.error("Invalid fractal equation selected")
        return "reject"

    # Generate SVG from fractal
    #mandelbrot_svg = generate_svg_from_fractal(fractal, xmin, xmax, ymin, ymax)
    mandelbrot_base64 = generate_base64_from_fractal(fractal, xmin, xmax, ymin, ymax, background_color, fractal_colors, fractal_cmap)
    logger.info(f"Mandelbrot base64 data: {mandelbrot_base64}")

    # Generate report with base64 data
    response = requests.post(rollup_server + "/report", json={"payload": str_to_hex(mandelbrot_base64)})

    # store & map hash of the image to creator
    base64_obj = base64.b64decode(mandelbrot_base64)
    image_hash = hashlib.sha256(base64_obj).hexdigest()
    logger.info(f"Image hash:  {image_hash}")
    map_image_to_creator(msg_sender, image_hash)

    # create voucher to mint NFT
    MINT_TO_FUNCTION_SELECTOR = b'u^\xdd\x17\xdc\xc4t\x0f\x04w\xcc\xcd\x9e\xfc\xc1\xa5\x07f!\xad\x86\x95\x8f\xfay\xfe\xef\xea\xee\xbf`\xc6'[:4]
    data = encode(['address'], [msg_sender])
    voucher_payload = binary2hex(MINT_TO_FUNCTION_SELECTOR + data)
    destination = "0x68E3Ee84Bcb7543268D361Bb92D3bBB17e90b838"
    voucher_response = requests.post(rollup_server + "/voucher", json={"destination": destination, "payload": voucher_payload})
    logger.info("Voucher Created")
    return "accept"


def handle_inspect(data):
    logger.info(f"Received inspect request data {data}")
    return "accept"


handlers = {
    "advance_state": handle_advance,
    "inspect_state": handle_inspect,
}

finish = {"status": "accept"}

while True:
    logger.info("Sending finish")
    response = requests.post(rollup_server + "/finish", json=finish)
    logger.info(f"Received finish status {response.status_code}")
    if response.status_code == 202:
        logger.info("No pending rollup request, trying again")
    else:
        rollup_request = response.json()
        data = rollup_request["data"]
        handler = handlers[rollup_request["request_type"]]
        finish["status"] = handler(rollup_request["data"])
