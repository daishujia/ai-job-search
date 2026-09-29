"""Anonymous listing of public S3 buckets (AWS Open Data) via ListObjectsV2 over HTTPS.

No AWS account or boto3 needed; downloads go to aria2 as plain HTTPS URLs.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from urllib.parse import quote

from .. import NasError
from ..manifest import FileEntry
from .base import Listing, require

NS = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}


def endpoint(bucket: str, region: str) -> str:
    return f"https://{bucket}.s3.{region}.amazonaws.com"


def list_prefixes(http, bucket: str, region: str, prefix: str) -> list[str]:
    """One level of 'folders' under prefix (for browsing before planning)."""
    xml = http.get_text(endpoint(bucket, region) + "/",
                        params={"list-type": "2", "prefix": prefix, "delimiter": "/", "max-keys": "1000"})
    root = ET.fromstring(xml)
    return [e.text for e in root.findall("s3:CommonPrefixes/s3:Prefix", NS) if e.text]


def list_files(params: dict, http, cfg) -> Listing:
    bucket = require(params, "bucket", r"[a-z0-9][a-z0-9.\-]{1,61}[a-z0-9]", "sea-ad-single-cell-profiling")
    region = str(params.get("region") or "us-east-1")
    if not re.fullmatch(r"[a-z]{2}-[a-z]+-\d", region):
        raise NasError(f"Bad region {region!r}")
    prefix = str(params.get("prefix") or "").lstrip("/")
    cap = int(params.get("max_keys") or cfg.max_plan_files)
    base = endpoint(bucket, region)
    files: list[FileEntry] = []
    token = None
    while True:
        q = {"list-type": "2", "prefix": prefix, "max-keys": "1000"}
        if token:
            q["continuation-token"] = token
        root = ET.fromstring(http.get_text(base + "/", params=q))
        for c in root.findall("s3:Contents", NS):
            key = c.findtext("s3:Key", default="", namespaces=NS)
            if not key or key.endswith("/"):
                continue
            etag = (c.findtext("s3:ETag", default="", namespaces=NS) or "").strip('"').lower()
            # Single-part ETags equal the MD5 only for unencrypted/SSE-S3 objects (not SSE-KMS; never
            # for multipart), so they are advisory: not enforced by aria2, reported softly by deep verify.
            md5 = etag if re.fullmatch(r"[0-9a-f]{32}", etag) else None
            files.append(FileEntry(
                url=f"{base}/{quote(key)}", relpath=key,  # full key: pulls of different prefixes never collide
                size=int(c.findtext("s3:Size", default="0", namespaces=NS)),
                checksum_type="md5" if md5 else None, checksum=md5,
                attrs={"advisory_checksum": True} if md5 else {},
            ))
            if len(files) >= cap:
                raise NasError(
                    f"Listing under s3://{bucket}/{prefix} exceeds {cap} files. Narrow 'prefix' "
                    "(use nas_browse_source to see sub-folders) or raise params.max_keys."
                )
        if root.findtext("s3:IsTruncated", namespaces=NS) != "true":
            break
        token = root.findtext("s3:NextContinuationToken", namespaces=NS)
    return Listing(files=files, record={"bucket": bucket, "region": region, "prefix": prefix},
                   meta={"source_url": f"s3://{bucket}/{prefix}", "region": region})
