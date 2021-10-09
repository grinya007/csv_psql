create extension plpython3u;

create function d() returns text as $$
    import subprocess
    return subprocess.check_output([
        "python", "/src/dump.py", "--no-confirm"
    ], universal_newlines=True)
$$ language plpython3u;

create function d(tbl text) returns text as $$
    import subprocess
    return subprocess.check_output([
        "python", "/src/dump.py", "--no-confirm", "--table", tbl
    ], universal_newlines=True)
$$ language plpython3u;
