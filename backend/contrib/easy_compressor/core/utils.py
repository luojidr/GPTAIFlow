import base64
import hashlib
from typing import Union, Dict, Any, NewType

import mmh3

MyDict = NewType("MyDict", Dict[str, Any])


def encode_base64_str(s: Union[str, bytes]) -> str:
	if isinstance(s, str):
		s = s.encode("utf-8")

	return base64.b64encode(s).decode("utf-8")


def decode_base64_bytes(s: Union[str, bytes]) -> bytes:
	return base64.b64decode(s, validate=True)


def encode_bytes(s: Union[str, bytes]) -> bytes:
	if isinstance(s, str):
		s = s.encode('utf-8')

	return s


def get_md5(s: Union[str, bytes]) -> str:
	s = encode_bytes(s)
	md5_hash = hashlib.md5()
	md5_hash.update(s)

	return md5_hash.hexdigest()


def get_hash(s):
	# mmh3 哈希分布相对均匀(有小概率的哈希冲突)
	return abs(mmh3.hash(s))

