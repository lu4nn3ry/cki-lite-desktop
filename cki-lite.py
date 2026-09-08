#!/usr/bin/env python3
"""Minimal NVIDIA NIM terminal agent for Alpine and other Unix-like systems."""
import argparse, getpass, json, os, subprocess, time, urllib.request, urllib.error, uuid, hashlib, re, sys

COLOR = False

def clean_terminal(text):
    # Preserve text and line breaks, but not provider-controlled terminal escapes.
    text = re.sub(r'\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)', '', str(text))
    text = re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]', '', text)
    return re.sub(r'[\x00-\x08\x0b-\x1f\x7f]', '', text)

def paint(text, style):
    return '\x1b[' + style + 'm' + text + '\x1b[0m' if COLOR else text

def command_text(command):
    command = clean_terminal(command)
    # Highlight executable positions; arguments and results have separate styles.
    return re.sub(r'(^|[;|&]\s*|\n)(\s*)([^\s;|&]+)',
                  lambda m: m[1]+m[2]+paint(m[3], '1;36'), command)

def inline_markdown(text):
    pattern = r'(`+)(.+?)\1|\*\*(.+?)\*\*|__(.+?)__|\[([^\]]+)\]\(([^)]+)\)|(?<!\w)\*([^*\n]+)\*(?!\w)'
    def replace(m):
        if m[2] is not None: return paint(m[2], '36')
        if m[3] is not None or m[4] is not None: return paint(m[3] or m[4], '1')
        if m[5] is not None: return paint(m[5], '4;34')+' ('+m[6]+')'
        return paint(m[7], '3')
    return re.sub(pattern, replace, text)

def markdown(text):
    lines=[]; fence=None; language=''
    for line in clean_terminal(text).splitlines():
        marker=re.match(r'^\s*(`{3,}|~{3,})(.*)$',line)
        if marker and (fence is None or marker[1][0]==fence):
            if fence is None:
                fence=marker[1][0]; language=marker[2].strip().lower()
                lines.append(paint('  [code'+(': '+language if language else '')+']','2'))
            else: fence=None
            continue
        if fence:
            lines.append('  '+(command_text(line) if language in ('sh','shell','bash','ash','console') else paint(line,'36')))
            continue
        heading=re.match(r'^#{1,6}\s+(.+?)(?:\s+#+)?$',line)
        if heading: lines.append(paint(inline_markdown(heading[1]),'1;35')); continue
        if re.match(r'^\s*(?:---+|\*\*\*+)\s*$',line): lines.append(paint('─'*32,'2')); continue
        line=re.sub(r'^(\s*)[-*+]\s+',r'\1• ',line)
        if line.startswith('> '): line='│ '+line[2:]
        lines.append(inline_markdown(line))
    return '\n'.join(lines)

def show_output(output):
    for field,label,style in [('stdout','stdout','32'),('stderr','stderr','31')]:
        if output.get(field):
            print(paint('['+label+']',style))
            print(paint(clean_terminal(output[field]).rstrip('\n'),style))
    print(paint('[exit %s]' % output['code'],'2' if output['code']==0 else '1;31'))

def show_command(command):
    print(paint('[terminal] ','1;33')+command_text(command),flush=True)

TOOL = {'type':'function','function':{'name':'terminal','description':'Execute shell commands on this host for the user request.','parameters':{'type':'object','properties':{'command':{'type':'string'},'cwd':{'type':'string'},'timeout':{'type':'integer'}},'required':['command']}}}

def api(base, key, path, data=None, method='POST'):
    raw = None if data is None else json.dumps(data).encode()
    req = urllib.request.Request(base.rstrip('/') + path, raw, method=method, headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as error:
        detail = error.read().decode('utf-8','replace').replace(key,'[REDACTED]')
        failure = RuntimeError('HTTP %s: %s' % (error.code, detail[:500]))
        failure.code = error.code
        raise failure from None

def is_rate_limit(error):
    return getattr(error, 'code', None) == 429 or 'rate limit' in str(error).lower() or 'too many requests' in str(error).lower()

def trace(enabled, message):
    if enabled: print('[trace] ' + message, flush=True)

def session_dir():
    path = os.path.expanduser(os.getenv('CKI_LITE_HOME','~/.cki-lite'))
    os.makedirs(path, exist_ok=True)
    return path

def load_dotenv():
    paths = [os.path.join(os.path.dirname(os.path.realpath(__file__)), '.env'), os.path.join(session_dir(), '.env'), os.path.join(os.getcwd(), '.env')]
    for path in paths:
        if not os.path.exists(path): continue
        with open(path, encoding='utf-8') as env_file:
            for line in env_file:
                line=line.strip()
                if not line or line.startswith('#'): continue
                if line.startswith('export '): line=line[7:].strip()
                if '=' not in line: continue
                name,value=line.split('=',1); value=value.strip().strip('"').strip("'")
                if name.strip() and name.strip() not in os.environ: os.environ[name.strip()]=value

def save_session(session_id, model, history, started):
    with open(os.path.join(session_dir(), session_id+'.json'),'w',encoding='utf-8') as f:
        json.dump({'session_id':session_id,'started_at':started,'updated_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'model':model,'messages':history},f,ensure_ascii=False,indent=2)

def load_session(session_id):
    path=os.path.join(session_dir(),session_id+'.json')
    if not os.path.exists(path): return None
    with open(path,encoding='utf-8') as f: return json.load(f)

def export_sessions(target, session_id=None):
    names=[session_id+'.json'] if session_id else sorted(x for x in os.listdir(session_dir()) if x.endswith('.json'))
    data=[]
    for name in names:
        item=load_session(name[:-5])
        if item: data.append(item)
    with open(target,'w',encoding='utf-8') as f: json.dump(data[0] if session_id and data else data,f,ensure_ascii=False,indent=2)
    print('Exportado: %s (%d sessão(ões))' % (target,len(data)))

def shell(args, verbose=False):
    command = args.get('command',''); cwd = args.get('cwd') or os.getcwd(); timeout = min(int(args.get('timeout',120)),900)
    started = time.time(); trace(verbose, 'terminal start cwd=%s timeout=%ss' % (cwd, timeout))
    try:
        p = subprocess.run(['/bin/sh','-lc',command], cwd=cwd, text=True, capture_output=True, timeout=timeout)
        trace(verbose, 'terminal done exit=%s elapsed=%.2fs' % (p.returncode, time.time()-started))
        return {'code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
    except subprocess.TimeoutExpired:
        trace(verbose, 'terminal timeout elapsed=%.2fs' % (time.time()-started))
        return {'code':124,'stdout':'','stderr':'command timeout'}

def visible_models(base, key, refresh=False):
    cache_dir=os.path.join(session_dir(),'cache'); os.makedirs(cache_dir,exist_ok=True)
    cache=os.path.join(cache_dir,hashlib.sha256(base.encode()).hexdigest()[:16]+'.json')
    models=None
    if not refresh and os.path.exists(cache):
        try:
            with open(cache) as f: models=json.load(f)
        except (ValueError,OSError): pass
    if models is None:
        models = api(base, key, '/models', method='GET').get('data', [])
        with open(cache+'.tmp','w') as f: json.dump(models,f)
        os.replace(cache+'.tmp',cache)
    selected=os.path.join(cache_dir,'selected.json')
    if os.path.exists(selected):
        with open(selected) as f: ranked=json.load(f)
        available={m['id'] for m in models}
        return [m for m in ranked if m in available]
    def agent_model(model_id):
        name = model_id.lower()
        if any(x in name for x in ('embed','vision','safety','content-safety','parse','reward','diffusion','recurrent','omni')):
            return False
        return ('gemma-3-' in name or 'gemma-4-' in name or
                'gpt-oss' in name or
                'nemotron' in name and any(x in name for x in ('instruct','super','ultra','lightning','nano-3')))
    return [m['id'] for m in models if m.get('id') and agent_model(m['id'])]

def choose_model(models):
    for number, model in enumerate(models, 1): print('%3d %s' % (number, model))
    selected = input('Modelo [1]: ').strip() or '1'
    return models[int(selected)-1]

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(prog='cki-lite')
    parser.add_argument('--base-url', default=os.getenv('NIM_BASE_URL','https://integrate.api.nvidia.com/v1'))
    parser.add_argument('--key', help='NVIDIA API key; prefer NVIDIA_API_KEY instead')
    parser.add_argument('--model')
    parser.add_argument('--list-models', action='store_true')
    parser.add_argument('--refresh-models', action='store_true', help='refresh cached NVIDIA catalog')
    parser.add_argument('--verbose', action='store_true', help='show agent loop and tool execution trace')
    parser.add_argument('--color', choices=('auto','always','never'), default='auto', help='terminal colors (default: auto)')
    parser.add_argument('--session', help='resume a saved session')
    parser.add_argument('--export', metavar='FILE', help='export saved session(s) to JSON')
    args = parser.parse_args()
    global COLOR
    COLOR = args.color == 'always' or (args.color == 'auto' and sys.stdout.isatty() and 'NO_COLOR' not in os.environ and os.getenv('TERM') != 'dumb')
    if args.export:
        export_sessions(args.export, args.session); return
    key = args.key or os.getenv('NVIDIA_API_KEY') or getpass.getpass('NVIDIA API key: ')
    models = visible_models(args.base_url, key, args.refresh_models)
    if args.list_models:
        print('\n'.join(models)); return
    session_id = args.session or time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:6]
    saved = load_session(session_id) if args.session else None
    model = (saved or {}).get('model') or args.model or choose_model(models)
    print('cki-lite | %s | terminal agent enabled' % model)
    history = (saved or {}).get('messages', [])
    started_at = (saved or {}).get('started_at') or time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
    print('session: '+session_id)
    while True:
        try: prompt = input('\nVocê> ').strip()
        except (EOFError, KeyboardInterrupt): break
        if prompt in ('/quit','/exit'): save_session(session_id,model,history,started_at); break
        if prompt == '/clear': history = []; save_session(session_id,model,history,started_at); continue
        if prompt == '/save': save_session(session_id,model,history,started_at); print('Sessão salva: '+session_id); continue
        if prompt == '/export': export_sessions(session_id+'.json',session_id); continue
        if prompt == '/terminal':
            command=input('shell> '); show_command(command)
            show_output(shell({'command':command},args.verbose)); continue
        history.append({'role':'user','content':prompt})
        for loop in range(8):
            trace(args.verbose, 'agent loop=%d model=%s messages=%d' % (loop+1, model, len(history)))
            started = time.time()
            retries = 0; result = None; last_error = None
            while True:
                try:
                    result = api(args.base_url, key, '/chat/completions', {'model':model,'messages':history,'tools':[TOOL],'tool_choice':'auto','temperature':.2,'max_tokens':4096})
                    break
                except Exception as request_error:
                    last_error = request_error
                    if is_rate_limit(request_error):
                        retries += 1; delay = retries * 5
                        trace(args.verbose, 'rate limit; retry=%d wait=%ss model=%s' % (retries, delay, model))
                        print('[rate-limit] %s; retrying in %ss (attempt %d)' % (model, delay, retries), flush=True)
                        time.sleep(delay); continue
                    break
            if not isinstance(result, dict):
                trace(args.verbose, 'model error elapsed=%.2fs' % (time.time()-started))
                print('\nNIM error on %s: %s' % (model, last_error)); switched = False
                for candidate in models:
                    if candidate == model: continue
                    try:
                        result = api(args.base_url, key, '/chat/completions', {'model':candidate,'messages':history,'tools':[TOOL],'tool_choice':'auto','temperature':.2,'max_tokens':4096})
                        model = candidate; switched = True; print('[auto] continuing with %s' % model); break
                    except Exception as fallback_error: print('[auto] %s failed: %s' % (candidate, fallback_error))
                if not switched: print('[auto] no available Gemma/Nemotron model; task paused.'); break
            message = result['choices'][0]['message']; history.append(message); calls = message.get('tool_calls', [])
            trace(args.verbose, 'model response elapsed=%.2fs tool_calls=%d' % (time.time()-started, len(calls)))
            if not calls:
                save_session(session_id,model,history,started_at)
                print('\n'+paint('NIM>','1;35')+'\n'+markdown(message.get('content') or '')); break
            if message.get('content'): print(markdown(message['content']))
            for call in calls:
                try: arguments = json.loads(call['function']['arguments'])
                except Exception: arguments = {'command':'echo invalid tool arguments'}
                show_command(arguments.get('command','')); output = shell(arguments, args.verbose); show_output(output)
                history.append({'role':'tool','tool_call_id':call['id'],'content':json.dumps(output)})
            save_session(session_id,model,history,started_at)

if __name__ == '__main__': main()
