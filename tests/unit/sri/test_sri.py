import base64
import os

from pytest import raises

from piedpiper import sri as sritool


test_file = os.path.join(os.path.dirname(__file__), 'tst_file.txt')


def test_hash_to_urlsafeb64(sri_obj, sri_urlsafe):

    assert sritool.hash_to_urlsafeb64(sri_obj) == sri_urlsafe


def test_hash_to_urlsafeb64_bad_input():

    with raises(AssertionError):
        sritool.hash_to_urlsafeb64('abcde')


def test_urlsafe_to_hash(sri_obj, sri_urlsafe):

    assert str(sritool.urlsafe_to_hash(sri_urlsafe)) == str(sri_obj)


def test_urlsafe_to_hash_bytes_input(sri_obj, sri_urlsafe):
    bencoded = sri_urlsafe.encode('ascii')
    assert str(sritool.urlsafe_to_hash(bencoded)) == str(sri_obj)


def test_urlsafe_to_hash_bad_input_type():
    with raises(AssertionError):
        sritool.urlsafe_to_hash(1234)


def test_urlsafe_to_hash_notb64():

    with raises(Exception) as e:
        sritool.urlsafe_to_hash('adfasdfasdfsad')

    assert 'binascii.Error' in str(e.type)


def test_hash_to_sri_hash(sri_obj, sri):
    parts = sri.split('-')
    hash = base64.b64decode(parts[1].encode('ascii'))
    assert str(sritool.hash_to_sri_hash(parts[0], hash)) == str(sri_obj)


def test_hash_to_sri_hash_str_input(sri_obj, sri):
    parts = sri.split('-')
    hash = 'random value'
    with raises(ValueError):
        sritool.hash_to_sri_hash(parts[0], hash)


def test_hash_file():

    assert isinstance(sritool.hash_file('sha256', test_file), bytes)


def test_hash_file_bad_path():

    with raises(IOError):
        sritool.hash_file('sha256', './tst_none.txt')


def test_hash_file_bad_dgst():
    with raises(ValueError):
        sritool.hash_file('sha3245455', test_file)


def test_b64_hash(sri):

    parts = sri.split('-')
    assert sritool.b64_hash(base64.b64decode(parts[1])).decode('utf-8') == parts[1]


def test_generate_sri():
    hash = 'sha256-BoZM0Ehx2L5aErZiq2qVDZaAN3vhmoN4OKCmIuN/Vy8='
    assert str(sritool.generate_sri(test_file,
                                    dgst='sha256',
                                    url_safe=False)) == hash


def test_generate_sri_url_safe():
    hash = 'c2hhMjU2LUJvWk0wRWh4Mkw1YUVyWmlxMnFWRFphQU4zdmhtb040T0tDbUl1Ti9WeTg9'
    assert str(sritool.generate_sri(test_file,
                                    dgst='sha256',
                                    url_safe=True)) == hash


def test_sri_to_hash(sri):

    assert str(sritool.sri_to_hash(sri)) == sri
