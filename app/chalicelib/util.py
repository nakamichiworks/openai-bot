import io
from typing import Optional, Union
from urllib.request import Request, urlopen

from PIL import Image


def download_file(url: str, file: str, access_token: Optional[str] = None):
    """Download a file from `url` and save it to `file`"""
    req = Request(url)
    if access_token is not None:
        req.add_header("Authorization", f"Bearer {access_token}")
    content = urlopen(req).read()
    with open(file, "wb") as f:
        f.write(content)


def crop_and_resize_image(
    infile: Union[str, io.BytesIO],
    outfile: Union[str, io.BytesIO],
    size: tuple[int, int] = (512, 512),
    format: str = "png",
):
    im = Image.open(infile)
    xlen, ylen = im.size
    if xlen > ylen:
        im.crop((0, 0, ylen, ylen)).resize(size).save(outfile, format=format)
    elif xlen < ylen:
        im.crop((0, 0, xlen, xlen)).resize(size).save(outfile, format=format)
    else:
        im.resize(size).save(outfile, format=format)
