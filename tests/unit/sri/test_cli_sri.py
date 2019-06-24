import os
import pytest

from piperci.cli import sri


test_file = os.path.join(os.path.dirname(__file__), 'tst_file.txt')

cases = [
    (['sritool', 'generate', test_file],
     'sha256-BoZM0Ehx2L5aErZiq2qVDZaAN3vhmoN4OKCmIuN/Vy8='),
    (['sritool', 'verify', test_file,
      'sha256-BoZM0Ehx2L5aErZiq2qVDZaAN3vhmoN4OKCmIuN/Vy8='],
     'sha256-BoZM0Ehx2L5aErZiq2qVDZaAN3vhmoN4OKCmIuN/Vy8=\n'
     'urlsafeb64: c2hhMjU2LUJvWk0wRWh4Mkw1YUVyWmlxMnFWRFphQU4zdmhtb040T0tDbUl1Ti9WeTg9'),
    (['sritool', '--url-safe', 'verify', test_file,
      'c2hhMjU2LUJvWk0wRWh4Mkw1YUVyWmlxMnFWRFphQU4zdmhtb040T0tDbUl1Ti9WeTg9'],
     'sha256-BoZM0Ehx2L5aErZiq2qVDZaAN3vhmoN4OKCmIuN/Vy8=\n'
     'urlsafeb64: c2hhMjU2LUJvWk0wRWh4Mkw1YUVyWmlxMnFWRFphQU4zdmhtb040T0tDbUl1Ti9WeTg9'
     ),
    (['sritool', 'decode',
      'c2hhMjU2LUJvWk0wRWh4Mkw1YUVyWmlxMnFWRFphQU4zdmhtb040T0tDbUl1Ti9WeTg9'],
     'sha256-BoZM0Ehx2L5aErZiq2qVDZaAN3vhmoN4OKCmIuN/Vy8=')
]

fail_cases = [
    (['sritool'], 'error: the following arguments are required'),
    (['sritool', 'verify', test_file,
      'sha256-CXS0O7OjESVro+DicbpxpvZPeBy2jTJ/CuQJnScABWs='],
     '!='
     ),
]


@pytest.mark.parametrize('argv,stdout_val', cases)
def test_cli_valid(argv, stdout_val, capsys, monkeypatch):

    monkeypatch.setattr('sys.argv', argv)

    sri.main()
    captured = capsys.readouterr()

    assert stdout_val in captured.out


@pytest.mark.parametrize('argv,stderr_val', fail_cases)
def test_usage_errors(argv, stderr_val, capsys, monkeypatch):
    monkeypatch.setattr('sys.argv', argv)

    with pytest.raises(SystemExit):
        sri.main()
    captured = capsys.readouterr()

    assert stderr_val in captured.err
