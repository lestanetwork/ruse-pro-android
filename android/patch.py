#!/usr/bin/env python3
"""PojavLauncher kaynagini ruse.pro'ya cevirir. Kullanim: patch.py <pojav_dir> <android_dir>"""
import glob, os, re, shutil, subprocess, sys


def resize(src, dst, px):
    if shutil.which('convert') or shutil.which('magick'):
        exe = 'magick' if shutil.which('magick') else 'convert'
        subprocess.check_call([exe, src, '-resize', f'{px}x{px}', dst])
    else:
        from PIL import Image
        Image.open(src).convert('RGBA').resize((px, px), Image.LANCZOS).save(dst)


pj, ad = sys.argv[1], sys.argv[2]
main = os.path.join(pj, 'app_pojavlauncher/src/main')

# 1) uygulama kimligi
gp = os.path.join(pj, 'app_pojavlauncher/build.gradle')
s = open(gp, encoding='utf-8').read()
s = s.replace('applicationId "net.kdt.pojavlaunch"', 'applicationId "pro.ruse.mobile"')
out = []
for line in s.split('\n'):
    if 'resValue' in line and 'net.kdt.pojavlaunch' in line:
        line = line.replace('net.kdt.pojavlaunch', 'pro.ruse.mobile')
    out.append(line)
open(gp, 'w', encoding='utf-8').write('\n'.join(out))

# 2) isim
for f in glob.glob(os.path.join(main, 'res/values*/strings.xml')):
    t = open(f, encoding='utf-8').read()
    t = re.sub(r'(<string name="app_name"[^>]*>)[^<]*(</string>)', r'\1ruse.pro\2', t)
    t = re.sub(r'(<string name="app_short_name"[^>]*>)[^<]*(</string>)', r'\1ruse.pro\2', t)
    open(f, 'w', encoding='utf-8').write(t)

# 3) ikon: SADECE ic_launcher ve ic_launcher_round dosyalarina dokun, baskasini silme
logo = os.path.join(ad, 'logo.png')
sizes = {'mdpi': 48, 'hdpi': 72, 'xhdpi': 96, 'xxhdpi': 144, 'xxxhdpi': 192}
for d in glob.glob(os.path.join(main, 'res/mipmap-*')):
    base = os.path.basename(d)
    for name in ('ic_launcher', 'ic_launcher_round'):
        for ext in ('png', 'webp', 'jpg', 'xml'):
            p = os.path.join(d, name + '.' + ext)
            if os.path.exists(p):
                os.remove(p)
    for dens, px in sizes.items():
        if base == 'mipmap-' + dens:
            for name in ('ic_launcher.png', 'ic_launcher_round.png'):
                resize(logo, os.path.join(d, name), px)
fb = os.path.join(main, 'res/mipmap-xxxhdpi')
os.makedirs(fb, exist_ok=True)
for name in ('ic_launcher.png', 'ic_launcher_round.png'):
    p = os.path.join(fb, name)
    if not os.path.exists(p):
        resize(logo, p, 192)
# varsayilan mipmap bossa (anydpi silindiyse) ana klasore de koy
for name in ('ic_launcher.png', 'ic_launcher_round.png'):
    dd = os.path.join(main, 'res/mipmap-mdpi')
    os.makedirs(dd, exist_ok=True)
    if not os.path.exists(os.path.join(dd, name)):
        resize(logo, os.path.join(dd, name), 48)

# 4) kurulum sinifi + acilis kancasi
dst = os.path.join(main, 'java/net/kdt/pojavlaunch')
shutil.copy(os.path.join(ad, 'RuseSetup.java'), dst)
la = os.path.join(dst, 'LauncherActivity.java')
s = open(la, encoding='utf-8').read()
hook = 'setContentView(R.layout.activity_pojav_launcher);'
assert hook in s, 'LauncherActivity kancasi bulunamadi'
s = s.replace(hook, hook + '\n        RuseSetup.start(this);', 1)
open(la, 'w', encoding='utf-8').write(s)
print('ruse.pro yamasi uygulandi')
