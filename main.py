import datetime
import io
import os
import re

VAULT_NAME = 'tameshi-vault'

def ql_range_check(lines: list) -> tuple:
    # returns (0,0) if no quicklink section is found

    start, end = 0, 0
    found = False
    
    ln = 0
    for line in lines:
        if not found:
            if re.match('^#.*$', line) and re.match('.*quicklink.*', line.lower()):
                start = ln
                found = True
        else:
            if re.match('^#.*$', line):
                end = ln-1
                return (start, end)
        ln += 1

    return (start, end)

def generate_ql(lines: list) -> list[str]:
    ql = ['# Quicklink\n']
    hdrs = get_headings(lines)

    for hdr in hdrs:
        ql.append('- [{}]({})\n'.format(hdr, hdr_to_anchor(hdr)))
    
    return ql

def update_md(file: io.TextIOWrapper, lines: str, ql_range: tuple, ql_cnt: list) -> None:
    if ql_range[0] == 0 and ql_range[1] == 0:
        non_ql_dat = []
    else:
        non_ql_dat = lines[ql_range[1]+1:]

    file.write(''.join(ql_cnt + non_ql_dat))
    
def get_headings(lines: list) -> list[str]:
    hdrs = []

    for line in lines:
        if re.match('^#.*$', line) and not re.match('.*quicklink.*', line.lower()):
            hdrs.append(line.replace('#', '').strip())

    return hdrs

def hdr_to_anchor(header: str) -> str:
    anchor = '#' + header.lower() \
        .replace(' ','-') \
        .replace(':;\"\',<.>/?[]{}|\\!@#$%^&*()_=+','')

    return anchor

if __name__ == '__main__':
    print('Running script at {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    for root, dirs, files in os.walk(VAULT_NAME, topdown=True):
        dirs[:] = [d for d in dirs if d not in ['.obsidian']]
        print('In root: {}, files = [{}]'.format(root, files))
        
        notes = [note for note in files if note not in ['00.md']]
        for note in notes:
            with open(os.path.join(root, note)) as nf:
                nfl = nf.readlines()
                qlr = ql_range_check(nfl)
                ql_cnt = generate_ql(nfl)

            with open(os.path.join(root, note), 'w') as nf:
                update_md(nf, nfl, qlr, ql_cnt)

        if '00.md' not in files:
            with open(os.path.join(root, '00.md'), 'w') as f:
                f.writelines(['- [[{}]]\n'.format(note.replace('.md', '')) for note in notes])
