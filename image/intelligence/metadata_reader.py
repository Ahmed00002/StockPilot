# image/intelligence/metadata_reader.py
import subprocess
import json
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class EXIFData:
    camera: str = ""
    lens: str = ""
    exposure: str = ""
    iso: str = ""
    aperture: str = ""
    shutter_speed: str = ""
    focal_length: str = ""
    capture_date: str = ""
    gps: str = ""
    software: str = ""
    flash: str = ""
    white_balance: str = ""

@dataclass
class IPTCData:
    keywords: list[str] = field(default_factory=list)
    caption: str = ""
    headline: str = ""
    copyright: str = ""
    creator: str = ""

@dataclass
class XMPData:
    raw_namespaces: dict = field(default_factory=dict)

@dataclass
class ImageMetadata:
    exif: EXIFData
    iptc: IPTCData
    xmp: XMPData

class MetadataReader:
    @staticmethod
    def extract(file_path: Path) -> ImageMetadata:
        try:
            result = subprocess.run(
                ['exiftool', '-json', '-G', str(file_path)],
                capture_output=True,
                text=True,
                check=True
            )
            data = json.loads(result.stdout)[0]
        except (subprocess.CalledProcessError, FileNotFoundError, IndexError):
            return ImageMetadata(EXIFData(), IPTCData(), XMPData())

        exif = EXIFData(
            camera=data.get("EXIF:Model", ""),
            lens=data.get("EXIF:LensModel", ""),
            exposure=data.get("EXIF:ExposureTime", ""),
            iso=str(data.get("EXIF:ISO", "")),
            aperture=str(data.get("EXIF:FNumber", "")),
            shutter_speed=str(data.get("EXIF:ExposureTime", "")),
            focal_length=str(data.get("EXIF:FocalLength", "")),
            capture_date=data.get("EXIF:DateTimeOriginal", ""),
            gps=data.get("EXIF:GPSPosition", ""),
            software=data.get("EXIF:Software", ""),
            flash=str(data.get("EXIF:Flash", "")),
            white_balance=str(data.get("EXIF:WhiteBalance", ""))
        )

        iptc = IPTCData(
            keywords=data.get("IPTC:Keywords", []),
            caption=data.get("IPTC:Caption-Abstract", ""),
            headline=data.get("IPTC:Headline", ""),
            copyright=data.get("IPTC:CopyrightNotice", ""),
            creator=data.get("IPTC:By-line", "")
        )
        if isinstance(iptc.keywords, str):
            iptc.keywords = [iptc.keywords]

        xmp_raw = {k: v for k, v in data.items() if k.startswith("XMP:")}
        xmp = XMPData(raw_namespaces=xmp_raw)

        return ImageMetadata(exif=exif, iptc=iptc, xmp=xmp)