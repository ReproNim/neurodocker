"""Utilites to compare files on Dropbox with local files.

There should be a mapping between paths to Dockerfiles on Dropbox and Docker
images on DockerHub.

Implementation
--------------
- Store generated Dockerfiles on Dropbox.
- Compare hash of generated Dockerfile with hash of file on Dropbox.
    - Commented lines and empty lines are removed from the Dockerfiles before
      computing hash values.
- If hashes do not match:
    - Replace existing file with generated file.
    - Build Docker image.
- If hashes match:
    - Pull Docker image.
"""
from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

import logging

logger = logging.getLogger(__name__)


class Dropbox(object):
    """Object to interact with the Dropbox API."""
    def __init__(self, access_token):
        import dropbox
        self.client = dropbox.Dropbox(access_token)

    def download(self, path, return_metadata=False, **kwargs):
        """Return metadata and bytes of file. If file does not exist, return
        None.

        Copied parts from:
        https://github.com/dropbox/dropbox-sdk-python/blob/master/example/updown.py#L147
        """
        import dropbox

        try:
            metadata, response = self.client.files_download(path, **kwargs)
            content = response.content
            response.close()
            if return_metadata:
                return metadata, content
            else:
                return content
        except dropbox.exceptions.ApiError as err:
            # Raise the error if it is something other than file not existing.
            try:
                if err.error.get_path().is_not_found():
                    return None
            except Exception:
                raise

    def upload(self, bytestring, path, overwrite=False, **kwargs):
        """Save `bytestring` to `path` on Dropbox."""
        import dropbox

        if overwrite:
            mode = dropbox.files.WriteMode.overwrite
        else:
            mode = dropbox.files.WriteMode.add
        self.client.files_upload(bytestring, path, mode=mode, **kwargs)


def _prune_dockerfile(string, comment_char="#"):
    """Remove comments, emptylines, and last layer (serialize to JSON)."""
    string = string.strip()  # trim white space on both ends.
    json_removed = '\n\n'.join(string.split('\n\n')[:-1])
    return '\n'.join(
        row for row in json_removed.split('\n') if not
        row.startswith(comment_char) and row
    )


def _get_hash(bytestring):
    """Get sha256 hash of `bytestring`."""
    import hashlib
    return hashlib.sha256(bytestring).hexdigest()


def _dockerfiles_equivalent(df_a, df_b):
    """Return True if unicode strings `df_a` and `df_b` are equivalent. Does
    not consider comments or empty lines.
    """
    df_a_clean = _prune_dockerfile(df_a)
    hash_a = _get_hash(df_a_clean.encode())

    df_b_clean = _prune_dockerfile(df_b)
    hash_b = _get_hash(df_b_clean.encode())

    print(df_a_clean)
    print(df_b_clean)

    return hash_a == hash_b


def should_build_image(local_df, remote_path, remote_object):
    """Return True if image should be built. Return False if image should be
    pulled.

    Parameters
    ----------
    local_df : str
        Unicode string representation of locally generated Dockerfile.
    remote_path : path-like
        Path on remote to the Dockerfile.
    remote_object : custom
        Object to interact with the remote (e.g., Dropbox). This object must
        (1) implement a `download` method that takes the `path` to the file on
        remote, returns the bytes of the file, and returns None if the file
        does not exist; and (2) implement an `upload` method that takes a
        bytestring to upload, path on remote, and option to overwrite.
    """
    logger.info("Attempting to download Dockerfile ...")
    remote_df_bytes = remote_object.download(remote_path)

    if remote_df_bytes is None:
        logger.info("File not found on remote. Uploading Dockerfile.")
        remote_object.upload(local_df.encode(), remote_path)
        return True
    else:
        if _dockerfiles_equivalent(local_df, remote_df_bytes.decode('utf-8')):
            logger.info("Files are the same. Image should be pulled.")
            return False
        else:
            logger.info("Files are different. Updating remote Dockerfile.")
            remote_object.upload(
                local_df.encode(), remote_path, overwrite=True
            )
            return True
