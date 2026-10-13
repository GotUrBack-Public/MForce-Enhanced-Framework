#!/usr/bin/env python3
"""MForce OSINT. Authorized, bounded public-data inspection for Termux/Linux."""
import argparse, ipaddress, json, os, re, shutil, socket, ssl, subprocess, sys, time
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, urlunsplit, parse_qsl
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError, URLError

USER_AGENT = "MForce-OSINT/1.0 (educational and authorized professional inspection)"
MAX_BYTES = 512*1024
SENSITIVE = {'key','apikey','api_key','token','access_token','secret','password','auth','authorization'}
RATE_HEADERS = ('ratelimit','ratelimit-policy','ratelimit-limit','ratelimit-remaining','ratelimit-reset','retry-after','x-ratelimit-limit','x-ratelimit-remaining','x-ratelimit-reset','x-rate-limit-limit')
DOM = {
 'innerHTML':r'\.\s*innerHTML\s*(?:\+?=|\b)',
 'outerHTML':r'\.\s*outerHTML\s*(?:\+?=|\b)',
 'insertAdjacentHTML':r'\.\s*insertAdjacentHTML\s*\(',
 'document.write':r'\bdocument\s*\.\s*write(?:ln)?\s*\(',
 'eval':r'\beval\s*\(',
 'new Function':r'\bnew\s+Function\s*\(',
 'srcdoc':r'\.\s*srcdoc\s*(?:\+?=|\b)',
 'dangerouslySetInnerHTML':r'\bdangerouslySetInnerHTML\b',
}
class Error(Exception): pass
def safe(x, maximum=140):
    value = re.sub(r'[\x00-\x1f\x7f-\x9f\u202a-\u202e\u2066-\u2069]', ' ', str(x)).strip()
    return value[:maximum]+('…' if len(value)>maximum else '')
def line(name, value):
    print('  '+safe(name,25).ljust(25)+safe(value,105))
def section(name):
    print('\n  '+name.upper()+'\n  '+'─'*min(72,max(28,shutil.get_terminal_size((80,24)).columns-4)))
def note(value): print('  • '+safe(value,125))
def warning(value): print('  ! '+safe(value,125))
def banner():
    print('\n  __  __ _____ ___  ____   ____ _____')
    print(r' |  \/  |  ___/ _ \|  _ \ / ___| ____|')
    print(r' | |\/| | |_ | | | | |_) | |   |  _|')
    print(r' | |  | |  _|| |_| |  _ <| |___| |___')
    print(r' |_|  |_|_|   \___/|_| \_\\____|_____|')
    print('  E N H A N C E D   F R A M E W O R K')
def host(value):
    val=value.strip()
    val=urlsplit(val).hostname if '://' in val else val.strip('[]').split('/')[0]
    if not val or len(val)>253 or not re.fullmatch(r'[A-Za-z0-9:._-]+',val): raise Error('Invalid public hostname / IP.')
    return val.lower().rstrip('.')
def url(value):
    value=value.strip()
    if '://' not in value: value='https://'+value
    try: parsed=urlsplit(value); port=parsed.port
    except ValueError: raise Error('Invalid URL or port.')
    if parsed.scheme not in ('http','https') or not parsed.hostname or parsed.username or parsed.password:
        raise Error('Only HTTP(S) without embedded credentials is supported.')
    if not ('.' in parsed.hostname or ':' in parsed.hostname): raise Error('Use a fully qualified public hostname.')
    if port not in (None,80,443,8080,8443): raise Error('Unsupported port.')
    if len(value)>2000 or any(k.lower() in SENSITIVE for k,v in parse_qsl(parsed.query)):
        raise Error('Remove sensitive query parameters / overly long URLs.')
    return urlunsplit((parsed.scheme,parsed.netloc,parsed.path,parsed.query,''))
def public(hostname,port):
    try: answers=socket.getaddrinfo(hostname,port,type=socket.SOCK_STREAM)
    except OSError as e: raise Error('Host lookup failed: '+safe(e))
    if not answers or any(not ipaddress.ip_address(a[4][0]).is_global for a in answers):
        raise Error('Private, local or non-public targets are blocked.')
class StopRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl): return None
def request(target, limit=MAX_BYTES):
    target=url(target)
    opener=build_opener(StopRedirect())
    start=time.monotonic()
    original=urlsplit(target).scheme
    for hop in range(4):
        p=urlsplit(target)
        public(p.hostname,p.port or (443 if p.scheme=='https' else 80))
        try: r=opener.open(Request(target,headers={'User-Agent':USER_AGENT,'Accept':'text/html,application/json,*/*'}),timeout=8)
        except HTTPError as e: r=e
        except (URLError,OSError,ValueError) as e: raise Error('HTTP request failed: '+safe(e))
        with r:
            code=getattr(r,'status',getattr(r,'code',0))
            h={k.lower():v for k,v in r.headers.items()}
            if 300<=code<400 and h.get('location'):
                nxt=url(urljoin(target,h['location']))
                if original=='https' and urlsplit(nxt).scheme!='https': raise Error('HTTPS downgrade redirected; stopped.')
                target=nxt; continue
            data=r.read(limit+1)
        if len(data)>limit: raise Error('Response exceeds read size limit.')
        return {'url':target,'code':code,'headers':h,'body':data,'elapsed':time.monotonic()-start}
    raise Error('Maximum redirect count exceeded.')
def redacted(target):
    p=urlsplit(target)
    q='&'.join(k+'=[redacted]' if k.lower() in SENSITIVE else k+'='+safe(v,35) for k,v in parse_qsl(p.query))
    return urlunsplit((p.scheme,p.netloc,p.path,q,''))
def rate(r):
    section('Rate-limit evidence')
    observed={key:safe(r['headers'][key],85) for key in RATE_HEADERS if r['headers'].get(key)}
    if r['code']==429: outcome='OBSERVED / HTTP 429'
    elif observed: outcome='HEADERS PRESENT / ENFORCEMENT UNVERIFIED'
    else: outcome='UNKNOWN / NO LIMIT INFORMATION OBSERVED'
    line('Assessment',outcome)
    for k,v in observed.items(): line(k,v)
    note('Missing headers do NOT establish that no rate limits exist.')
    note('No repeated load tests, bypasses or probing of thresholds.')
def http(r):
    section('Public HTTP overview')
    line('Final URL',redacted(r['url']))
    line('HTTP status',r['code'])
    line('Response time',str(round(r['elapsed']*1000))+' ms')
    for k in ('content-type','server','cache-control','access-control-allow-origin'):
        if r['headers'].get(k):line(k,r['headers'][k])
    section('Security header indications')
    for k in ('content-security-policy','strict-transport-security','x-content-type-options','referrer-policy','permissions-policy','x-frame-options'):
        if k=='strict-transport-security' and not r['url'].startswith('https://'): value='Not applicable (not HTTPS)'
        else: value='Present' if r['headers'].get(k) else 'Not observed'
        line(k,value)
    line('Cookies', 'Set-Cookie observed; values suppressed' if r['headers'].get('set-cookie') else 'Not observed')
    note('Header absence is a review hint, not an exploitable finding.')
    rate(r)
class HTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.title='';self.description='';self.generator='';self.forms=[];self.links=0;self.images=0;self.scripts=[];self.inline=[];self._script=False;self._title=False;self._buf=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=='title':self._title=True
        if tag=='meta':
            n=(d.get('name') or '').lower()
            if n=='description':self.description=d.get('content') or ''
            if n=='generator':self.generator=d.get('content') or ''
        if tag=='form':self.forms.append(((d.get('method') or 'GET').upper(),(d.get('action') or '(current page)').split('?')[0]))
        if tag=='a':self.links+=1
        if tag=='img':self.images+=1
        if tag=='script':
            self._script=True;self._buf=[]
            if d.get('src'):self.scripts.append(d['src'])
    def handle_endtag(self,tag):
        if tag=='title':self._title=False
        if tag=='script' and self._script:
            self._script=False
            if self._buf:self.inline.append(''.join(self._buf))
    def handle_data(self,data):
        if self._title:self.title+=data
        if self._script:self._buf.append(data)
def parse_html(r):
    if 'html' not in r['headers'].get('content-type','') and not r['body'].lstrip().lower().startswith((b'<html',b'<!doctype')):return None
    p=HTML();p.feed(r['body'].decode('utf-8','replace'));p.close();return p
def js_check(r,p):
    section('JavaScript / DOM patterns')
    line('Script references',len(p.scripts));line('Inline scripts',len(p.inline))
    samples=[('inline #'+str(i),x) for i,x in enumerate(p.inline[:8],1)]
    if r['code']!=429 and not r['headers'].get('retry-after'):
        attempts=0; seen=set()
        for name in p.scripts:
            if attempts>=3:break
            try: absolute=urljoin(r['url'],name); parsed=urlsplit(absolute); origin=urlsplit(r['url'])
            except ValueError:continue
            if (parsed.scheme,parsed.hostname,parsed.port)!=(origin.scheme,origin.hostname,origin.port) or absolute in seen:continue
            if any(k.lower() in SENSITIVE for k,v in parse_qsl(parsed.query)):continue
            seen.add(absolute);attempts+=1
            try: source=request(absolute,160*1024)
            except Error:continue
            if source['code']==429: break
            if source['code']!=200:continue
            if 'javascript' not in source['headers'].get('content-type','') and not parsed.path.endswith(('.js','.mjs')):continue
            samples.append((parsed.path or 'same-origin asset',source['body'].decode('utf-8','replace')))
    line('Sources reviewed',len(samples))
    findings=[]
    for name,source in samples:
        for label,pattern in DOM.items():
            for m in list(re.finditer(pattern,source,re.I))[:7]:
                findings.append((label,name,source.count('\n',0,m.start())+1))
    if not findings:note('No listed patterns in sampled sources; coverage is limited.')
    else:
        counts={}
        for label,_,_ in findings:counts[label]=counts.get(label,0)+1
        for label,num in counts.items():line(label,str(num)+' potential occurrence(s)')
        for label,file,line_num in findings[:12]:note(label+' / '+safe(file,58)+' / line '+str(line_num))
    note('innerHTML / DOM sinks are STATIC hints, never confirmed XSS.')
    note('No code execution, injection, form submission or crawling.')
def web(r,include_js=True):
    http(r);section('Public page information')
    p=parse_html(r)
    if p is None: warning('HTML not observed; cannot inspect DOM.');return
    line('Title',p.title or 'Not observed')
    line('Description',p.description or 'Not observed')
    if p.generator:line('Generator (claimed)',p.generator)
    line('Links / Images',str(p.links)+' / '+str(p.images))
    line('Forms',len(p.forms))
    for i,(method,action) in enumerate(p.forms[:5],1):note('Form '+str(i)+' / '+method+' / '+action)
    if include_js:js_check(r,p)
def api(r):
    http(r);section('API response / schema')
    if 'json' not in r['headers'].get('content-type','') and not r['body'].lstrip().startswith((b'{',b'[')):
        warning('JSON response not observed.');return
    try:obj=json.loads(r['body'])
    except (ValueError,UnicodeDecodeError):warning('JSON parsing failed.');return
    line('Top-level type',type(obj).__name__)
    if isinstance(obj,dict):
        line('Keys',len(obj))
        for k,v in list(obj.items())[:18]:line('Field',safe(k,50)+' / '+type(v).__name__)
    elif isinstance(obj,list):line('Array items',len(obj))
    note('Only field names/types shown. Response values remain hidden.')
def dns(target):
    name=host(target);section('DNS / public resolver');line('Hostname',name)
    try:records=socket.getaddrinfo(name,None,type=socket.SOCK_STREAM)
    except OSError as e:raise Error('DNS error: '+safe(e))
    for fam,label in ((socket.AF_INET,'A'),(socket.AF_INET6,'AAAA')):
        vals=sorted({a[4][0] for a in records if a[0]==fam})
        line(label,', '.join(vals[:6]) if vals else 'Not observed')
    if shutil.which('dig'):
        for typ in ('MX','NS','TXT','CAA','CNAME','SOA'):
            try:result=subprocess.run(['dig','+short','+time=2','+tries=1',name,typ],capture_output=True,text=True,timeout=5,check=False)
            except (OSError,subprocess.TimeoutExpired):line(typ,'Unavailable');continue
            vals=[safe(s,100) for s in result.stdout.splitlines() if s.strip()]
            line(typ,str(len(vals))+' records')
            for val in vals[:3]:note(val)
    else:note('Optional: install dig for MX, NS, TXT, CAA, CNAME, SOA records.')
def ip(target):
    name=host(target);section('IP / network intelligence')
    try:ips=[ipaddress.ip_address(name)]
    except ValueError:
        try:ips=[ipaddress.ip_address(a[4][0]) for a in socket.getaddrinfo(name,None,type=socket.SOCK_STREAM)]
        except OSError as e:raise Error('IP resolution failed: '+safe(e))
    for address in sorted(set(ips),key=lambda x:(x.version,int(x)))[:10]:
        line('Address',address);line('Family / scope','IPv'+str(address.version)+' / '+('PUBLIC' if address.is_global else 'NON-PUBLIC'))
        if address.is_global:
            try:line('PTR',socket.gethostbyaddr(str(address))[0])
            except OSError:line('PTR','Not observed')
    note('Use RDAP for public registration and allocation information.')
def tls(target):
    dest=url(target);p=urlsplit(dest);hostname=p.hostname;port=p.port or 443
    public(hostname,port);section('TLS / verified handshake')
    try:
        with socket.create_connection((hostname,port),timeout=7) as conn:
            with ssl.create_default_context().wrap_socket(conn,server_hostname=hostname) as s:
                c=s.getpeercert();line('Trust','Verified against system CA store');line('TLS',s.version())
                line('Cipher',(s.cipher() or ('unknown',))[0])
    except (OSError,ssl.SSLError) as e:raise Error('TLS verification / connection failed: '+safe(e))
    for label,val in c.get('subjectAltName',())[:8]:
        if label=='DNS':note('SAN / '+val)
    if c.get('notAfter'):
        try:line('Expiry UTC',datetime.fromtimestamp(ssl.cert_time_to_seconds(c['notAfter']),timezone.utc).strftime('%Y-%m-%d'))
        except ValueError:pass
def robots(target):
    dest=url(target);p=urlsplit(dest)
    base=urlunsplit((p.scheme,p.netloc,'/','',''))
    section('robots.txt / sitemap.xml')
    for path in ('robots.txt','sitemap.xml'):
        resp=request(urljoin(base,path),256*1024);line(path,'HTTP '+str(resp['code']))
        if resp['code']==429:warning('Rate limit observed; stopped further requests.');break
        if resp['code']!=200:continue
        body=resp['body'].decode('utf-8','replace')
        if path=='robots.txt':
            for tag in ('User-agent:','Disallow:','Allow:','Sitemap:'):
                line(tag,sum(x.strip().lower().startswith(tag.lower()) for x in body.splitlines()))
        else:line('URL entries',len(re.findall(r'<loc(?:\s|>)',body,re.I)))
    note('No sitemap paths or disallowed URLs are visited.')
def rdap(target):
    name=host(target)
    try:
        address=ipaddress.ip_address(name)
        if not address.is_global:raise Error('Only public IPs supported for RDAP.')
        endpoint='https://rdap.org/ip/'+str(address)
    except ValueError:
        if '.' not in name:raise Error('Expected public domain or IP.')
        endpoint='https://rdap.org/domain/'+name
    section('RDAP / registry metadata')
    note('Your target is sent to external RDAP referral provider rdap.org.')
    response=request(endpoint,180*1024);line('HTTP',response['code'])
    if response['code']!=200:warning('Registry data unavailable.');return
    try:data=json.loads(response['body'])
    except ValueError:raise Error('Invalid registry JSON.')
    for key in ('objectClassName','name','handle','startAddress','endAddress','country'):
        if data.get(key):line(key,data[key])
    if isinstance(data.get('status'),list):line('Status',', '.join(data['status'][:5]))
    for evt in data.get('events',[])[:8]:
        if evt.get('eventAction') in ('registration','expiration','last changed'):
            line(evt['eventAction'],evt.get('eventDate',''))
    note('Registry data may be incomplete or out of date.')
def run(mode,target):
    banner();section('MForce / OSINT / '+mode)
    note('EDUCATIONAL PURPOSE / PROFESSIONAL USAGE / authorized targets only.')
    note('GDPR-conscious use requires legal basis, purpose and data minimization.')
    note('No automatic storage. Providers and shell history may retain data.')
    if mode=='dns':dns(target)
    elif mode=='ip':ip(target)
    elif mode=='tls':tls(target)
    elif mode=='rdap':rdap(target)
    elif mode=='robots':robots(target)
    else:
        response=request(target,256*1024 if mode=='api' else MAX_BYTES)
        if mode=='rate':line('HTTP status',response['code']);rate(response)
        elif mode=='headers':http(response)
        elif mode=='api':api(response)
        elif mode=='web':web(response)
        elif mode=='js':
            page=parse_html(response)
            if page:js_check(response,page)
            else:warning('No HTML response; no scripts to review.')
def main():
    parser=argparse.ArgumentParser(description='MForce OSINT / Educational Purpose / Professional Usage')
    parser.add_argument('mode',choices=('dns','ip','tls','headers','web','api','rate','js','robots','rdap'))
    parser.add_argument('target',nargs='?',help='Public URL, domain or IP; authorized scope only')
    args=parser.parse_args()
    target=args.target
    interactive=target is None
    if interactive:
        try:target=input('\n  Public target (owned or authorized): ').strip()
        except EOFError:return 0
    try:run(args.mode,target);status=0
    except Error as e:print('  [NOTICE] '+safe(e),file=sys.stderr);status=2
    except KeyboardInterrupt:print('  Cancelled.',file=sys.stderr);status=130
    if interactive:
        try:input('\n  Press ENTER to return to MForce... ')
        except EOFError:pass
    return status
if __name__=='__main__':sys.exit(main())
