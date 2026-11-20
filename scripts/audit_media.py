"""Audit deployed media references, English locale assignments and unused assets."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import argparse,json,re
ROOT=Path(__file__).resolve().parents[1];IMAGE_ROOT=(ROOT/'assets/images').resolve()
class MediaParser(HTMLParser):
 def __init__(self):super().__init__();self.refs=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  for key in ('src','poster'):
   if key in a:self.refs.append(a[key])
  if tag=='link' and 'href' in a:self.refs.append(a['href'])
  if tag=='meta' and a.get('property')=='og:image':self.refs.append(a.get('content',''))

def audit():
 used=set();missing=[];wrong_locale=[];per_page={}
 for p in ROOT.rglob('*.html'):
  parsed=MediaParser();parsed.feed(p.read_text(encoding='utf8'));media=[]
  for ref in parsed.refs:
   u=urlsplit(ref)
   if u.netloc and u.netloc!='kolik.co':continue
   if not u.path.startswith('/assets/images/'):continue
   target=(ROOT/unquote(u.path).lstrip('/')).resolve();used.add(target);media.append(u.path)
   if not target.is_file():missing.append([p.relative_to(ROOT).as_posix(),ref])
   if p.is_relative_to(ROOT/'en') and target.name!='kolik-icon.svg' and not re.search(r'-en\.(?:png|jpe?g|webp|mp4)$',target.name):wrong_locale.append([p.relative_to(ROOT).as_posix(),ref])
  per_page[p.relative_to(ROOT).as_posix()]=sorted(set(media))
 for pattern in ('*.css','*.js','*.svg'):
  for p in ROOT.rglob(pattern):
   for relative in re.findall(r'/assets/images/([^\s\"\'<>\)?]+)',p.read_text(encoding='utf8')):
    target=(IMAGE_ROOT/relative).resolve();used.add(target)
    if not target.is_file():missing.append([p.relative_to(ROOT).as_posix(),relative])
 files={p.resolve() for p in IMAGE_ROOT.rglob('*') if p.is_file() and p.suffix.lower() in {'.png','.jpg','.jpeg','.svg','.webp','.gif','.mp4'}}
 unused=sorted(files-used)
 return {'html_pages':len(per_page),'english_pages':sum(p.startswith('en/') for p in per_page),'used_files':len(used),'missing':missing,'wrong_english_locale':wrong_locale,'unused':[p.relative_to(ROOT).as_posix() for p in unused],'unused_bytes':sum(p.stat().st_size for p in unused),'per_page':per_page}

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--prune',action='store_true');ap.add_argument('--details',action='store_true');args=ap.parse_args();result=audit()
 if result['missing'] or result['wrong_english_locale']:print(json.dumps(result,indent=2));raise SystemExit(1)
 if args.prune:
  removed=result['unused'];removed_bytes=result['unused_bytes']
  for name in removed:
   target=(ROOT/name).resolve()
   if not target.is_relative_to(IMAGE_ROOT) or target==IMAGE_ROOT:raise RuntimeError('Refusing out-of-tree deletion')
   target.unlink()
  result=audit();result['removed']=removed;result['removed_bytes']=removed_bytes
 if not args.details:result.pop('per_page',None)
 print(json.dumps(result,indent=2,ensure_ascii=False))
