#!/usr/bin/env python3
import argparse, hashlib, json, re, shutil, subprocess, tempfile
from pathlib import Path
from urllib.parse import urlparse
import requests
from PIL import Image, ImageOps
MAX_BYTES=12*1024*1024
ALLOWED={"image/jpeg","image/png","image/webp"}
def run(cmd):
 p=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 if p.returncode: raise RuntimeError(p.stdout[-5000:])
 return p.stdout
def download(url,dest):
 import socket,ipaddress
 u=urlparse(url)
 if u.scheme!="https" or not u.hostname or u.username or u.password: raise ValueError("Only public HTTPS image URLs accepted")
 for info in socket.getaddrinfo(u.hostname,None):
  if not ipaddress.ip_address(info[4][0]).is_global: raise ValueError("Image host resolves to non-public IP")
 with requests.get(url,stream=True,timeout=(15,45),headers={"User-Agent":"ProductVideoRenderer/1.0"}) as r:
  r.raise_for_status()
  ctype=r.headers.get("Content-Type","").split(";")[0].lower()
  if ctype not in ALLOWED: raise ValueError("Unsupported image content type: "+ctype)
  total=0
  with open(dest,"wb") as f:
   for chunk in r.iter_content(131072):
    if not chunk: continue
    total+=len(chunk)
    if total>MAX_BYTES: raise ValueError("Image exceeds 12 MB")
    f.write(chunk)
 with Image.open(dest) as im: im.verify()
 return total,ctype
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--title",required=True); ap.add_argument("--subtitle",default="Premium sound. Refined design.")
 ap.add_argument("--images",required=True); ap.add_argument("--output",default="output/product-video.mp4")
 a=ap.parse_args(); urls=json.loads(a.images)
 if not isinstance(urls,list) or not 2<=len(urls)<=5: raise ValueError("Provide 2–5 image URLs")
 out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True)
 work=Path(tempfile.mkdtemp(prefix="product-render-")); report=[]; segments=[]
 try:
  for i,url in enumerate(urls,1):
   src=work/f"source-{i}.img"; size,ctype=download(url,src)
   with Image.open(src) as im:
    im=ImageOps.exif_transpose(im).convert("RGB"); im.thumbnail((940,1120),Image.Resampling.LANCZOS)
    canvas=Image.new("RGB",(1080,1920),(10,12,18)); canvas.paste(im,((1080-im.width)//2,430+(1120-im.height)//2))
    still=work/f"shot-{i}.jpg"; canvas.save(still,quality=94)
   report.append(f"image_{i}: downloaded={size}; type={ctype}; validated=true")
   title=re.sub(r"[^A-Za-z0-9 .,&'()-]","",a.title)[:64]
   sub=re.sub(r"[^A-Za-z0-9 .,&'()-]","",a.subtitle)[:90]
   txt=title if i==1 else (sub if i==len(urls) else "DETAILS THAT MAKE THE DIFFERENCE")
   txt=txt.replace(":","\\:").replace("'","\\'")
   vf=f"zoompan=z='min(zoom+0.0007,1.035)':d=1:s=1080x1920:fps=30,drawbox=x=0:y=0:w=1080:h=360:color=black@0.45:t=fill,drawtext=text='{txt}':fontcolor=white:fontsize=54:x=(w-text_w)/2:y=170:borderw=2:bordercolor=black@0.35"
   seg=work/f"segment-{i}.mp4"
   run(["ffmpeg","-y","-loop","1","-i",str(still),"-t",str(10/len(urls)),"-vf",vf,"-r","30","-c:v","libx264","-preset","medium","-crf","19","-pix_fmt","yuv420p","-an",str(seg)])
   segments.append(seg)
  concat=work/"concat.txt"; concat.write_text("".join(f"file '{p.as_posix()}'\n" for p in segments))
  run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(concat),"-t","10","-c:v","libx264","-preset","medium","-crf","19","-pix_fmt","yuv420p","-movflags","+faststart",str(out)])
  probe=json.loads(run(["ffprobe","-v","error","-show_entries","format=duration,size","-show_entries","stream=codec_type,width,height,codec_name","-of","json",str(out)]))
  duration=float(probe["format"]["duration"]); video=next(s for s in probe["streams"] if s["codec_type"]=="video")
  if abs(duration-10)>0.15 or video.get("width")!=1080 or video.get("height")!=1920: raise RuntimeError("MP4 verification failed")
  report += ["mp4_verified=true",f"duration_seconds={duration:.3f}",f"resolution={video['width']}x{video['height']}",f"codec={video.get('codec_name')}",f"size_bytes={out.stat().st_size}",f"sha256={hashlib.sha256(out.read_bytes()).hexdigest()}"]
  Path("output/build-report.txt").write_text("\n".join(report)+"\n"); print("\n".join(report))
 finally: shutil.rmtree(work,ignore_errors=True)
if __name__=="__main__": main()
