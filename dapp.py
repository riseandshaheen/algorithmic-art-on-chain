from os import access, environ
import logging
import requests
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import matplotlib.colors as mcolors
import io
from cartesi_wallet.util import hex_to_str, str_to_hex
import cartesi_wallet.wallet as Wallet
import json
import base64
from eth_abi import encode, decode
import hashlib
from urllib.parse import urlparse
import pydenticon

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

rollup_server = environ["ROLLUP_HTTP_SERVER_URL"]
logger.info(f"HTTP rollup_server url is {rollup_server}")
wallet = Wallet
rollup_address = ""
nftaddress = ""
dapp_relay_address = "0xF5DE34d6BbC0446E2a45719E718efEbaaE179daE" #open(f'./deployments/{network}/ERC20Portal.json')
ether_portal_address = "0xFfdbe43d4c855BF7e0f105c400A50857f53AB044" #open(f'./deployments/{network}/EtherPortal.json')
erc20_portal_address = "0x9C21AEb2093C32DDbC53eEF24B873BDCd1aDa1DB" #open(f'./deployments/{network}/ERC20Portal.json')
erc721_portal_address = "0x237F8DD094C0e47f4236f12b4Fa01d6Dae89fb87" #open(f'./deployments/{network}/ERC721Portal.json')

creator_image_mapping = {}
def map_image_to_creator(user_address, image_hash):
    creator_image_mapping[user_address] = image_hash

def binary2hex(binary):
    """
    Encode a binary as an hex string
    """
    return "0x" + binary.hex()

def encode_json(d):
    return "0x" + json.dumps(d).encode("utf-8").hex()

def decode_json(b):
    s = bytes.fromhex(b[2:]).decode("utf-8")
    d = json.loads(s)
    return d

# IDENTICON
def generate_identicon(address):
    generator = pydenticon.Generator(5, 5)

    foreground = [ "rgb(45,79,255)",
                "rgb(254,180,44)",
                "rgb(226,121,234)",
                "rgb(30,179,253)",
                "rgb(232,77,65)",
                "rgb(49,203,115)",
                "rgb(141,69,170)" ]

    # Set-up a background colour (taken from Sigil).
    background = "rgb(224,224,224)"

    # Instantiate a generator that will create 5x5 block identicons using SHA1
    # digest.
    generator = pydenticon.Generator(5, 5, digest=hashlib.sha1,
                                    foreground=foreground, background=background)

    padding = (20, 20, 20, 20)

    # Generate a 240x240 PNG identicon.
    identicon = generator.generate(address, 200, 200, padding=padding, inverted=True, output_format="png")
    base64_data = base64.b64encode(identicon)
    raw_base64_string = base64_data.decode('utf-8')
    return raw_base64_string

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

# JULIA SET EQUATION
def generate_julia_set(width, height, max_iterations, xmin, xmax, ymin, ymax, C=-0.8 + 0.35j, R=5):
    x = np.linspace(xmin, xmax, width).astype(np.float32)
    y = np.linspace(ymax, ymin, height).reshape(height, 1).astype(np.float32) * 1j

    z = x + y
    counter = np.zeros_like(z, dtype=np.uint32)
    boolean = np.less(abs(z), R)

    for i in range(max_iterations):
        z[boolean] = z[boolean]**2 + C
        boolean = np.less(abs(z), R)
        if not boolean.any():
            break
        counter[boolean] += 1

    return counter

# FRACTAL PLOT TO BASE64
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
    sender = data["metadata"]["msg_sender"].lower()
    
    if sender.lower() == "0xF5DE34d6BbC0446E2a45719E718efEbaaE179daE".lower():
        global rollup_address
        logger.info(f"Received advance from dapp relay")
        rollup_address = data["payload"]
        #response = requests.post(rollup_server + "/report", json={"payload": str_to_hex(f"Set rollup_address {rollup_address}")})
        print(f"Relayed dapp address: {rollup_address}")
        return "accept"

    payload = hex_to_str(data["payload"])
    logger.info(f"Payload: {payload}")
    payload = json.loads(payload)
    method = payload.get("method", {})

    if method == "set_nft_address": # {"method":"set_nft_address", "nftaddress":"0x1234..."}
        global nftaddress
        nftaddress = payload.get("nftaddress", {})
        print(f"nft address set as: {nftaddress}")
        return "accept"

    if method == "identicon":
        img_output = generate_identicon(sender) #update in case for portals
        print(f"Generated identicon: {img_output}")
        response = requests.post(rollup_server + "/report", json={"payload": str_to_hex(img_output)})
        MINT_TO_FUNCTION_SELECTOR = b'u^\xdd\x17\xdc\xc4t\x0f\x04w\xcc\xcd\x9e\xfc\xc1\xa5\x07f!\xad\x86\x95\x8f\xfay\xfe\xef\xea\xee\xbf`\xc6'[:4]
        data = encode(['address'], [sender])
        logger.info(f"data encoded :{data}")
        voucher_payload = binary2hex(MINT_TO_FUNCTION_SELECTOR + data)
        #destination = "0x68E3Ee84Bcb7543268D361Bb92D3bBB17e90b838"
        voucher_response = requests.post(rollup_server + "/voucher", json={"destination": nftaddress, "payload": voucher_payload})
        logger.info(f"Voucher Created: {voucher_response}")
        return "accept"


    width = 600
    height = 600

    # Check inputs: define max width, height
    # Extract information from the data
    
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
    elif equation == "julia_set":
        fractal = generate_julia_set(width, height, max_iterations, xmin, xmax, ymin, ymax, C=-0.8 + 0.35j, R=5)
    else:
        logger.error("Invalid fractal equation selected")
        return "reject"

    # Generate base64 from fractal
    fractal_base64 = generate_base64_from_fractal(fractal, xmin, xmax, ymin, ymax, background_color, fractal_colors, fractal_cmap)
    logger.info(f"Mandelbrot base64 data: {fractal_base64}")

    # Generate report with base64 data
    response = requests.post(rollup_server + "/report", json={"payload": str_to_hex(fractal_base64)})

    # store & map hash of the image to creator
    base64_obj = base64.b64decode(fractal_base64)
    image_hash = hashlib.sha256(base64_obj).hexdigest()
    logger.info(f"Image hash:  {image_hash}")
    map_image_to_creator(sender, image_hash)

    # create voucher to mint NFT
    MINT_TO_FUNCTION_SELECTOR = b'u^\xdd\x17\xdc\xc4t\x0f\x04w\xcc\xcd\x9e\xfc\xc1\xa5\x07f!\xad\x86\x95\x8f\xfay\xfe\xef\xea\xee\xbf`\xc6'[:4]
    data = encode(['address'], [sender])
    logger.info(f"data encoded :{data}")
    voucher_payload = binary2hex(MINT_TO_FUNCTION_SELECTOR + data)
    destination = nftaddress
    voucher_response = requests.post(rollup_server + "/voucher", json={"destination": destination, "payload": voucher_payload})
    logger.info(f"Voucher Created: {voucher_response}")
    return "accept"


def handle_inspect(data):
    logger.info(f"Received inspect request data {data}")
    try:
        url = urlparse(hex_to_str(data["payload"]))
        print(f"url: {url}")
        if url.path.startswith("balance/"):
            print("Inspecting balance/")
            info = url.path.replace("balance/", "").split("/")
            token_type, account = info[0].lower(), info[1].lower()
            token_address, token_id, amount = "", 0, 0

            if (token_type == "ether"):
                print("checking ether balance")
                amount = wallet.balance_get(account).ether_get()
            elif (token_type == "erc20"):
                token_address = info[2]
                amount = wallet.balance_get(account).erc20_get(token_address.lower())
            elif (token_type == "erc721"):
                token_address, token_id = info[2], info[3]
                amount = 1 if token_id in wallet.balance_get(account).erc721_get(token_address.lower()) else 0
            
            report = {"payload": encode_json({"token_id": token_id, "amount": amount, "token_type": token_type})}
            response = requests.post(rollup_server + "/report", json=report)
            logger.info(f"Received report status {response.status_code} body {response.content}")
        return "accept"
    except Exception as error:
        error_msg = f"Failed to process inspect request. {error}"
        logger.debug(error_msg, exc_info=True)
        return "reject"


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
