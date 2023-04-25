from dataclasses import dataclass


@dataclass
class Signature:
    name: str
    extra: int
    relative: bool
    module: str
    offsets: list[int]
    pattern: str


@dataclass
class Netvar:
    name: str
    prop: str
    offset: int
    table: str


@dataclass
class ScanConfig:
    executable: str
    filename: str
    signatures: list[Signature]
    netvars: list[Netvar]


# TODO: do sigscan
