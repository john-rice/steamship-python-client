import os
import shutil
import tempfile
from pathlib import Path

from steamship import Space
from steamship.data.space import SignedUrl
from steamship.utils.signed_urls import download_from_signed_url, upload_to_signed_url
from steamship.utils.zip_archives import zip_folder
from tests import TEST_ASSETS_PATH
from tests.utils.client import get_steamship_client
from tests.utils.random import random_name


def test_upload_download_text():
    tempbase = Path(tempfile.mkdtemp())
    upfile = tempbase / "up.txt"
    downfile = tempbase / "down.txt"

    with open(upfile, "w") as f:
        f.write("Hello")

    # Grab a Steamship client and generate an upload url
    client = get_steamship_client()
    space = Space.get(client=client).data
    upload_name = random_name()
    url_resp = space.create_signed_url(
        SignedUrl.Request(
            bucket=SignedUrl.Bucket.PLUGIN_DATA,
            filepath=upload_name,
            operation=SignedUrl.Operation.WRITE,
        )
    )
    assert url_resp is not None
    assert url_resp.data is not None
    assert url_resp.data.signedUrl is not None

    # Upload the zip file to the URL
    upload_to_signed_url(url_resp.data.signedUrl, filepath=upfile)

    # Now create a download signed URL
    download_resp = space.create_signed_url(
        SignedUrl.Request(
            bucket=SignedUrl.Bucket.PLUGIN_DATA,
            filepath=upload_name,
            operation=SignedUrl.Operation.READ,
        )
    )
    assert download_resp is not None
    assert download_resp.data is not None
    assert download_resp.data.signedUrl is not None

    # Verify that we get an exception when downloading something that doesn't exist
    # TODO: Follow up after we get a firmer understaing of the failure semantics of Localstack 404 errors with
    # pre-signed URLs versus AWS Actual errors with pre-signed URLs. Localstack seems to reply with an HTTP 200
    # containing an XML string that contains an error message.

    # url = download_resp.data.signedUrl
    # parsed_url = urlparse(url)
    # bad_url = urlunparse(parsed_url._replace(path=f"{parsed_url.path}BOOGA"))
    # bad_download_path = tempbase / Path("bad.zip")
    # with pytest.raises(Exception):
    #     download_from_signed_url(download_resp.data.signedUrl, to_file=bad_download_path)

    # Download the zip file to the URL
    download_from_signed_url(download_resp.data.signedUrl, to_file=downfile)

    # Verify the download URL is there
    assert os.path.exists(downfile) == True

    # Verify the zip files are the same
    with open(downfile, "r") as f1:
        with open(upfile, "r") as f2:
            f1c = f1.read()
            f2c = f2.read()
            assert f1c == f2c


def test_upload_download():
    """This test simulates some of the operations models must do when trainable/loading.

    It performs the following steps:

    1. Zips up a folder
    2. Creates a signed-url with Write access in the "model" bucket of a space
    3. Uploads the zip file
    4. Creates a signed-url with Read access in the "model" bucket of a space, pointing to the same file
    5. Downloads the file
    6. Verifies that they are the same file

    """
    # Copy the test assets to a temp folder
    tempbase = Path(tempfile.mkdtemp())
    shutil.copytree(TEST_ASSETS_PATH, os.path.join(tempbase, "src"))

    # Zip that folder
    zip_path = tempbase / Path("src.zip")
    zip_folder(tempbase / Path("src"), into_file=zip_path)

    # Verify that on disk, src.zip exists
    assert os.path.exists(zip_path) == True

    # Grab a Steamship client and generate an upload url
    client = get_steamship_client()
    space = Space.get(client=client).data
    upload_name = random_name()
    url_resp = space.create_signed_url(
        SignedUrl.Request(
            bucket=SignedUrl.Bucket.PLUGIN_DATA,
            filepath=upload_name,
            operation=SignedUrl.Operation.WRITE,
        )
    )
    assert url_resp is not None
    assert url_resp.data is not None
    assert url_resp.data.signedUrl is not None

    # Upload the zip file to the URL
    upload_to_signed_url(url_resp.data.signedUrl, filepath=zip_path)

    # Now create a download signed URL
    download_resp = space.create_signed_url(
        SignedUrl.Request(
            bucket=SignedUrl.Bucket.PLUGIN_DATA,
            filepath=upload_name,
            operation=SignedUrl.Operation.READ,
        )
    )
    assert download_resp is not None
    assert download_resp.data is not None
    assert download_resp.data.signedUrl is not None

    # Verify that we get an exception when downloading something that doesn't exist
    # TODO: Follow up after we get a firmer understaing of the failure semantics of Localstack 404 errors with
    # pre-signed URLs versus AWS Actual errors with pre-signed URLs. Localstack seems to reply with an HTTP 200
    # containing an XML string that contains an error message.

    # url = download_resp.data.signedUrl
    # parsed_url = urlparse(url)
    # bad_url = urlunparse(parsed_url._replace(path=f"{parsed_url.path}BOOGA"))
    # bad_download_path = tempbase / Path("bad.zip")
    # with pytest.raises(Exception):
    #     download_from_signed_url(download_resp.data.signedUrl, to_file=bad_download_path)

    # Download the zip file to the URL
    download_path = tempbase / Path("out.zip")
    download_from_signed_url(download_resp.data.signedUrl, to_file=download_path)

    # Verify the download URL is there
    assert os.path.exists(download_path) == True

    # Verify the zip files are the same
    with open(download_path, "rb") as f1:
        with open(zip_path, "rb") as f2:
            f1c = f1.read()
            f2c = f2.read()
            assert f1c == f2c
