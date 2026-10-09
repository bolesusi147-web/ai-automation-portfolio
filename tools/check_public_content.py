"""Check repository content without printing matched secret values."""
import argparse
import ipaddress
import json
from pathlib import Path
import re
import subprocess


ALLOWED_EMAILS={'bolesusi147@gmail.com'}
ALLOWED_HOSTS={'github.com','docs.github.com','docs.n8n.io','elevenlabs.io','docs.elevenlabs.io'}
PATTERNS={
    'private_key':r'-----BEGIN [A-Z ]*PRIVATE KEY-----',
    'api_token':r'\bsk-[A-Za-z0-9_-]{20,}',
    'github_token':r'\bgh[pousr]_[A-Za-z0-9]{20,}',
    'aws_key':r'\bAKIA[A-Z0-9]{16}\b',
    'jwt':r'\beyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}',
    'credential_literal':r'''(?i)(?:api[_-]?key|password|access[_-]?token|client[_-]?secret)\s*[:=]\s*["']([^"'\n]{8,})''',
    'local_path':r'/(?:root|home)/[A-Za-z0-9_.-]+',
}
FORBIDDEN_SUFFIXES={'.wav','.mp3','.mp4','.sqlite','.db','.pem','.key','.pub','.log','.zip'}


def findings(path: str,text: str) -> list[dict]:
    result=[]
    def report(category,start):
        result.append(dict(path=path,line=text.count('\n',0,start)+1,category=category))
    for category,pattern in PATTERNS.items():
        for match in re.finditer(pattern,text): report(category,match.start())
    for match in re.finditer(r'\b(?:\d{1,3}\.){3}\d{1,3}\b',text):
        try:
            ipaddress.ip_address(match.group())
        except ValueError:
            continue
        report('network_address',match.start())
    for match in re.finditer(r'\b[A-Za-z0-9._+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',text):
        if match.group().lower() not in ALLOWED_EMAILS: report('unexpected_email',match.start())
    for match in re.finditer(r'https?://([A-Za-z0-9.-]+)',text):
        if match.group(1).lower() not in ALLOWED_HOSTS: report('unapproved_url',match.start())
    return result


def path_category(name: str):
    p=Path(name)
    if p.name.startswith('.env') or p.name.startswith('id_') or p.suffix in {'.pem','.key','.pub'}:
        return 'forbidden_file'
    if p.suffix in FORBIDDEN_SUFFIXES:
        return 'binary_or_media'
    return None


def scan_paths(root: Path,paths: list[str]) -> list[dict]:
    result=[]
    for name in sorted(set(paths)):
        p=root/name
        category=path_category(name)
        if category:
            result.append(dict(path=name,category=category));continue
        if p.is_symlink():
            result.append(dict(path=name,category='symlink'));continue
        try:
            text=p.read_text(encoding='utf-8')
        except (OSError,UnicodeError):
            result.append(dict(path=name,category='unreadable_file'));continue
        if '\x00' in text:
            result.append(dict(path=name,category='binary_or_media'));continue
        result.extend(findings(name,text))
    return result


def git(root,*args):
    return subprocess.check_output(['git','-C',str(root),*args])


def history_findings(root):
    result=[];count=0
    for line in git(root,'rev-list','--objects','--all').decode().splitlines():
        fields=line.split(' ',1)
        if len(fields)!=2:continue
        object_id,name=fields
        if git(root,'cat-file','-t',object_id).strip()!=b'blob':continue
        count+=1
        category=path_category(name)
        if category:result.append(dict(path=name,category=category));continue
        try:text=git(root,'cat-file','blob',object_id).decode('utf-8')
        except UnicodeError:result.append(dict(path=name,category='binary_or_media'));continue
        result.extend(findings(name,text))
    return result,count


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--history',action='store_true')
    args=parser.parse_args();root=Path(__file__).resolve().parent.parent
    paths=git(root,'ls-files','--cached','--others','--exclude-standard','-z').decode().split('\0')
    paths=[p for p in paths if p]
    result=scan_paths(root,paths);count=0
    if args.history:
        history,count=history_findings(root);result.extend(history)
    print(json.dumps(dict(checked_files=len(set(paths)),checked_history_blobs=count,findings=result),indent=2))
    raise SystemExit(bool(result))


if __name__=='__main__':main()
