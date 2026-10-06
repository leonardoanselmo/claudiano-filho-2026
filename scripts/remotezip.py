"""Lê um arquivo de dentro de um zip remoto por pedaços (HTTP Range), sem baixar o zip inteiro."""
import io, urllib.request, zipfile
class Remoto(io.RawIOBase):
    def __init__(s,url):
        s.url=url; s.pos=0
        r=urllib.request.urlopen(urllib.request.Request(url,method='HEAD')); s.size=int(r.headers['Content-Length'])
    def seekable(s): return True
    def readable(s): return True
    def tell(s): return s.pos
    def seek(s,o,w=0):
        s.pos={0:o,1:s.pos+o,2:s.size+o}[w]; return s.pos
    def readinto(s,b):
        n=len(b)
        if s.pos>=s.size or n==0: return 0
        end=min(s.pos+n,s.size)-1
        data=urllib.request.urlopen(urllib.request.Request(s.url,headers={'Range':f'bytes={s.pos}-{end}'})).read()
        b[:len(data)]=data; s.pos+=len(data); return len(data)
def extrair(url,filtro,destino):
    z=zipfile.ZipFile(io.BufferedReader(Remoto(url),buffer_size=8*1024*1024))
    nomes=[i.filename for i in z.infolist() if filtro(i.filename)]
    for n in nomes:
        with z.open(n) as src, open(destino,'wb') as out:
            while True:
                b=src.read(16*1024*1024)
                if not b: break
                out.write(b)
    return nomes
