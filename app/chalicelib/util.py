from typing import Optional
from urllib.request import Request, urlopen


def download_file(url: str, file: str, access_token: Optional[str] = None):
    """Download a file from `url` and save it to `file`"""
    req = Request(url)
    if access_token is not None:
        req.add_header("Authorization", f"Bearer {access_token}")
    content = urlopen(req).read()
    with open(file, "wb") as f:
        f.write(content)
