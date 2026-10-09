"""Check repository content without printing matched secret values."""
import argparse
import hashlib
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
PUBLIC_VISUALS={'assets/portfolio-cover.png','assets/workflow.png','assets/workflow.gif'}


def visual_approvals(text):
    """A fingerprint records a reviewed asset; it does not inspect pixels."""
    try:
        manifest=json.loads(text)
    except (ValueError,TypeError):
        return {}
    if not isinstance(manifest,dict) or manifest.get('synthetic') is not True:
        return {}
    result={}
    assets=manifest.get('assets',[])
    if not isinstance(assets,list):return {}
    for asset in assets:
        if not isinstance(asset,dict):continue
        name=asset.get('path');digest=asset.get('sha256');size=asset.get('bytes')
        if (name in PUBLIC_VISUALS and isinstance(digest,str) and
                re.fullmatch(r'[a-f0-9]{64}',digest) and type(size) is int and
                0<size<=6*1024*1024):
            result.setdefault(name,set()).add((digest,size))
    return result


def visual_findings(name,data,approved):
    if Path(name).suffix not in {'.png','.gif'}:return None
    def issue(category):return [dict(path=name,category=category)]
    if name not in PUBLIC_VISUALS or name not in approved:
        return issue('unapproved_visual')
    if (hashlib.sha256(data).hexdigest(),len(data)) not in approved[name]:
        return issue('visual_fingerprint_mismatch')
    if name.endswith('.png'):
        valid=(len(data)>=33 and data.startswith(b'\x89PNG\r\n\x1a\n') and
               data[12:16]==b'IHDR' and data[-8:-4]==b'IEND')
        width=int.from_bytes(data[16:20],'big');height=int.from_bytes(data[20:24],'big')
    else:
        valid=len(data)>=14 and data[:6] in {b'GIF87a',b'GIF89a'} and data.endswith(b';')
        width=int.from_bytes(data[6:8],'little');height=int.from_bytes(data[8:10],'little')
    if not valid or not 0<width*height<=16_000_000:
        return issue('invalid_visual_format')
    return []


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
    manifest=root/'assets/manifest.json'
    approved=visual_approvals(manifest.read_text()) if manifest.is_file() and not manifest.is_symlink() else {}
    for name in sorted(set(paths)):
        p=root/name
        category=path_category(name)
        if category:
            result.append(dict(path=name,category=category));continue
        if p.is_symlink():
            result.append(dict(path=name,category='symlink'));continue
        try:
            data=p.read_bytes()
            visual=visual_findings(name,data,approved)
            if visual is not None:
                result.extend(visual);continue
            text=data.decode('utf-8')
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
    objects=[];approved={}
    for line in git(root,'rev-list','--objects','--all').decode().splitlines():
        fields=line.split(' ',1)
        if len(fields)!=2:continue
        object_id,name=fields
        if git(root,'cat-file','-t',object_id).strip()!=b'blob':continue
        objects.append((object_id,name))
        if name=='assets/manifest.json':
            for path,values in visual_approvals(git(root,'cat-file','blob',object_id).decode()).items():
                approved.setdefault(path,set()).update(values)
    for object_id,name in objects:
        count+=1
        category=path_category(name)
        if category:result.append(dict(path=name,category=category));continue
        data=git(root,'cat-file','blob',object_id)
        visual=visual_findings(name,data,approved)
        if visual is not None:
            result.extend(visual);continue
        try:text=data.decode('utf-8')
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
