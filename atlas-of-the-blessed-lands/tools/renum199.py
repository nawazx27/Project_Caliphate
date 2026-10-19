"""Version 199: renames version names V1-V9 in reader-visible text only (JS string/template/regex literals, HTML outside comments and scripts, caliph.json strings), all at once: old V8->V1, V1->V2, V2->V3, V3->V4, V4->V5, V9->V6, V5->V7, V6->V8 (V7, India, deleted). Used once from a script; not safe to rerun."""
import re, sys, json
MAP = {'8': '1', '1': '2', '2': '3', '3': '4', '4': '5', '9': '6', '5': '7', '6': '8', '7': '7?'}
TOK = re.compile(r'\bV([1-9])\b')
log = []
def ren(t, where):
    def f(m):
        log.append((where, m.group(0)))
        return 'V' + MAP[m.group(1)]
    return TOK.sub(f, t)

def js(src, where):
    out = []; i = 0; n = len(src); stack = []  # stack of template-literal brace depths
    depth = 0; prev = ''  # last significant code char
    def regex_ok():
        return prev == '' or prev in '(,=:[!&|?{};+-*%<>~^' or re.search(r'(return|typeof|case)$', ''.join(out)[-8:]) is not None
    while i < n:
        c = src[i]
        if c == '/' and src[i:i+2] == '//':
            j = src.find('\n', i); j = n if j < 0 else j
            out.append(src[i:j]); i = j; continue
        if c == '/' and src[i:i+2] == '/*':
            j = src.find('*/', i) + 2; out.append(src[i:j]); i = j; continue
        if c in '\'"':
            j = i + 1
            while src[j] != c:
                j += 2 if src[j] == '\\' else 1
            out.append(c + ren(src[i+1:j], where) + c); i = j + 1; prev = c; continue
        if c == '/' and regex_ok():
            j = i + 1; cls = False
            while True:
                ch = src[j]
                if ch == '\\': j += 2; continue
                if ch == '[': cls = True
                elif ch == ']': cls = False
                elif ch == '/' and not cls: break
                elif ch == '\n': raise Exception('regex parse at %d' % i)
                j += 1
            out.append('/' + ren(src[i+1:j], where) + '/'); i = j + 1; prev = '/x'; prev = ')'; continue
        if c == '`' or (c == '}' and stack and stack[-1] == depth):
            if c == '}': stack.pop()
            # template text until ` or ${
            j = i + 1; buf = []
            while True:
                ch = src[j]
                if ch == '\\': buf.append(src[j:j+2]); j += 2; continue
                if ch == '`': out.append(c + ren(''.join(buf), where) + '`'); i = j + 1; prev = '`'; break
                if ch == '$' and src[j+1] == '{':
                    out.append(c + ren(''.join(buf), where) + '${'); stack.append(depth); i = j + 2; prev = '{'; break
                buf.append(ch); j += 1
            continue
        if c == '{': depth += 1
        elif c == '}': depth -= 1
        out.append(c)
        if not c.isspace(): prev = c
        i += 1
    return ''.join(out)

def html(src, where):
    parts = re.split(r'(<!--.*?-->|<script\b.*?</script>)', src, flags=re.S)
    return ''.join(p if p.startswith('<!--') or p.startswith('<script') else ren(p, where) for p in parts)

def jsonwalk(o, where):
    if isinstance(o, str): return ren(o, where)
    if isinstance(o, list): return [jsonwalk(x, where) for x in o]
    if isinstance(o, dict): return {k: jsonwalk(v, where) for k, v in o.items()}
    return o
