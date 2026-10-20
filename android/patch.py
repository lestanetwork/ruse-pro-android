#!/usr/bin/env python3
"""PojavLauncher kaynagini ruse.pro'ya cevirir. Kullanim: patch.py <pojav_dir> <android_dir>"""
import glob, os, re, shutil, subprocess, sys


def resize(src, dst, px):
    if shutil.which('convert') or shutil.which('magick'):
        exe = 'magick' if shutil.which('magick') else 'convert'
        subprocess.check_call([exe, src, '-resize', f'{px}x{px}', dst])
    else:
        from PIL import Image  # pip install pillow
        Image.open(src).convert('RGBA').resize((px, px), Image.LANCZOS).save(dst)


pj, ad = sys.argv[1], sys.argv[2]
RUSE_UI = r'''package net.kdt.pojavlaunch;

import android.app.Activity;
import android.app.ActivityManager;
import android.content.Context;
import android.content.SharedPreferences;
import android.view.View;
import android.widget.EditText;
import android.widget.SeekBar;
import android.widget.TextView;
import android.widget.Toast;


import net.kdt.pojavlaunch.extra.ExtraConstants;
import net.kdt.pojavlaunch.extra.ExtraCore;
import net.kdt.pojavlaunch.prefs.LauncherPreferences;
import net.kdt.pojavlaunch.value.MinecraftAccount;

import java.io.File;
import java.util.Random;

/** ruse.pro launcher ekrani: kullanici adi + RAM + OYNA. */
public final class RuseUi {
    private static final String KEY_NICK = "ruse_nick";
    private static final String NICK_RE = "[A-Za-z0-9_]{3,16}";

    private RuseUi() {}

    private static SharedPreferences prefs(Context c) {
        if (LauncherPreferences.DEFAULT_PREF == null) LauncherPreferences.loadPreferences(c.getApplicationContext());
        return LauncherPreferences.DEFAULT_PREF;
    }

    public static String nick(Context c) {
        String n = prefs(c).getString(KEY_NICK, "");
        if (n == null || !n.matches(NICK_RE)) {
            n = "Ruse" + (1000 + new Random().nextInt(9000));
            prefs(c).edit().putString(KEY_NICK, n).apply();
        }
        return n;
    }

    /** Oyun hesabi: sadece isimden olusan cevrimdisi hesap. LauncherActivity acilirken cagrilir. */
    public static void ensureAccount(Context c) {
        try {
            new File(Tools.DIR_ACCOUNT_NEW).mkdirs();
            MinecraftAccount a = new MinecraftAccount();
            a.username = nick(c);
            a.save();
            PojavProfile.setCurrentProfile(c, a.username);
        } catch (Throwable ignored) {
        }
    }

    private static String label(int mb) {
        return "Bellek (RAM): " + (mb % 1024 == 0 ? String.valueOf(mb / 1024) : String.format("%.1f", mb / 1024.0)) + " GB";
    }

    public static void bind(final View root) {
        final Context c = root.getContext();
        EditText nick = (EditText) root.findViewById(R.id.ruse_nick);
        final TextView ramText = (TextView) root.findViewById(R.id.ruse_ram_text);
        SeekBar ram = (SeekBar) root.findViewById(R.id.ruse_ram);
        if (nick == null || ramText == null || ram == null) return;
        nick.setText(nick(c));

        ActivityManager am = (ActivityManager) c.getSystemService(Context.ACTIVITY_SERVICE);
        ActivityManager.MemoryInfo mi = new ActivityManager.MemoryInfo();
        am.getMemoryInfo(mi);
        int deviceMb = (int) (mi.totalMem / (1024L * 1024L));
        int maxMb = Math.max(1536, Math.min(8192, deviceMb - 1280));
        int steps = (maxMb - 1024) / 512;
        ram.setMax(steps);
        int cur = prefs(c).getInt("allocation", 3072);
        cur = Math.max(1024, Math.min(1024 + steps * 512, cur));
        ram.setProgress((cur - 1024) / 512);
        ramText.setText(label(cur));
        ram.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override public void onProgressChanged(SeekBar s, int p, boolean user) { ramText.setText(label(1024 + p * 512)); }
            @Override public void onStartTrackingTouch(SeekBar s) {}
            @Override public void onStopTrackingTouch(SeekBar s) {}
        });
    }

    public static void play(Activity act, View root) {
        EditText nick = (EditText) root.findViewById(R.id.ruse_nick);
        SeekBar ram = (SeekBar) root.findViewById(R.id.ruse_ram);
        if (nick == null || ram == null) return;
        String n = nick.getText().toString().trim();
        if (!n.matches(NICK_RE)) {
            Toast.makeText(act, "Kullanici adi 3-16 karakter olmali (harf, rakam, _)", Toast.LENGTH_LONG).show();
            return;
        }
        if (!RuseSetup.ready) {
            RuseSetup.start(act);
            Toast.makeText(act, "ruse.pro kuruluyor, birkac saniye sonra tekrar OYNA'ya bas", Toast.LENGTH_LONG).show();
            return;
        }
        int mb = 1024 + ram.getProgress() * 512;
        prefs(act).edit().putString(KEY_NICK, n).putInt("allocation", mb).apply();
        LauncherPreferences.PREF_RAM_ALLOCATION = mb;
        if (LauncherActivity.RUSE_SPINNER != null) LauncherActivity.RUSE_SPINNER.useLocalAccount(n);
        ExtraCore.setValue(ExtraConstants.LAUNCH_GAME, true);
    }
}
'''
RUSE_LAYOUT = r'''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout
	xmlns:android="http://schemas.android.com/apk/res/android"
	xmlns:app="http://schemas.android.com/apk/res-auto"
	android:id="@+id/fragment_menu_main"
	android:layout_width="match_parent"
	android:layout_height="match_parent"
	android:orientation="vertical"
	android:background="@color/background_app">

	<ScrollView
		android:layout_width="match_parent"
		android:layout_height="0dp"
		android:layout_weight="1"
		android:fillViewport="true">

		<LinearLayout
			android:layout_width="match_parent"
			android:layout_height="wrap_content"
			android:orientation="vertical"
			android:padding="20dp">

			<ImageView
				android:id="@+id/ruse_logo"
				android:layout_width="match_parent"
				android:layout_height="130dp"
				android:scaleType="fitCenter"
				android:src="@drawable/ruse_logo" />

			<TextView
				android:layout_width="match_parent"
				android:layout_height="wrap_content"
				android:gravity="center"
				android:text="Fabric 1.21.4 · hybrid client"
				android:textColor="@color/secondary_text"
				android:textSize="12sp" />

			<TextView
				android:layout_width="wrap_content"
				android:layout_height="wrap_content"
				android:layout_marginTop="18dp"
				android:text="KULLANICI ADI"
				android:textColor="@color/secondary_text"
				android:textSize="11sp" />

			<EditText
				android:id="@+id/ruse_nick"
				android:layout_width="match_parent"
				android:layout_height="wrap_content"
				android:layout_marginTop="6dp"
				android:background="@drawable/ruse_input"
				android:hint="Nick"
				android:imeOptions="actionDone"
				android:inputType="textVisiblePassword"
				android:maxLength="16"
				android:singleLine="true"
				android:padding="12dp"
				android:textColor="@color/primary_text"
				android:textColorHint="@color/secondary_text"
				android:textSize="16sp" />

			<TextView
				android:id="@+id/ruse_ram_text"
				android:layout_width="wrap_content"
				android:layout_height="wrap_content"
				android:layout_marginTop="18dp"
				android:text="Bellek (RAM)"
				android:textColor="@color/secondary_text"
				android:textSize="12sp" />

			<SeekBar
				android:id="@+id/ruse_ram"
				android:layout_width="match_parent"
				android:layout_height="wrap_content"
				android:layout_marginTop="6dp" />

			<LinearLayout
				android:layout_width="match_parent"
				android:layout_height="wrap_content"
				android:layout_marginTop="14dp"
				android:orientation="horizontal">

				<com.kdt.mcgui.LauncherMenuButton
					android:id="@+id/discord_button"
					style="@style/LauncherMenuButton.Universal"
					android:layout_width="0dp"
					android:layout_weight="1"
					android:text="Discord"
					android:drawableStart="@drawable/ic_discord" />

				<com.kdt.mcgui.LauncherMenuButton
					android:id="@+id/custom_control_button"
					style="@style/LauncherMenuButton.Universal"
					android:layout_width="0dp"
					android:layout_weight="1"
					android:text="Kontroller"
					android:drawableStart="@drawable/ic_menu_custom_controls" />

				<com.kdt.mcgui.LauncherMenuButton
					android:id="@+id/open_files_button"
					style="@style/LauncherMenuButton.Universal"
					android:layout_width="0dp"
					android:layout_weight="1"
					android:text="Klasör"
					android:drawableStart="@drawable/ic_folder" />
			</LinearLayout>

			<!-- ruse.pro arayuzunde gorunmeyen ama kodun bekledigi ogeler -->
			<com.kdt.mcgui.LauncherMenuButton
				android:id="@+id/news_button"
				style="@style/LauncherMenuButton.Universal"
				android:layout_width="match_parent"
				android:visibility="gone" />
			<com.kdt.mcgui.LauncherMenuButton
				android:id="@+id/install_jar_button"
				style="@style/LauncherMenuButton.Universal"
				android:layout_width="match_parent"
				android:visibility="gone" />
			<com.kdt.mcgui.LauncherMenuButton
				android:id="@+id/share_logs_button"
				style="@style/LauncherMenuButton.Universal"
				android:layout_width="match_parent"
				android:visibility="gone" />
			<com.kdt.mcgui.mcVersionSpinner
				android:id="@+id/mc_version_spinner"
				android:layout_width="match_parent"
				android:layout_height="wrap_content"
				android:visibility="gone" />
			<ImageButton
				android:id="@+id/edit_profile_button"
				android:layout_width="wrap_content"
				android:layout_height="wrap_content"
				android:visibility="gone" />
		</LinearLayout>
	</ScrollView>

	<com.kdt.mcgui.MineButton
		android:id="@+id/play_button"
		android:layout_width="match_parent"
		android:layout_height="64dp"
		android:layout_marginHorizontal="20dp"
		android:layout_marginVertical="14dp"
		android:textAllCaps="true"
		android:text="OYNA" />
</LinearLayout>
'''
RUSE_INPUT = r'''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
	<solid android:color="#0C0C11" />
	<stroke android:width="1dp" android:color="#2A2A33" />
	<corners android:radius="10dp" />
</shape>
'''

main = os.path.join(pj, 'app_pojavlauncher/src/main')

# 1) uygulama kimligi (resmi Pojav ile yan yana kurulabilsin) + provider/authority metinleri
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

# 3) ikon
logo = os.path.join(ad, 'logo.png')
sizes = {'mdpi': 48, 'hdpi': 72, 'xhdpi': 96, 'xxhdpi': 144, 'xxxhdpi': 192}
for d in glob.glob(os.path.join(main, 'res/mipmap-*')):
    base = os.path.basename(d)
    for f in glob.glob(os.path.join(d, 'ic_launcher*')):
        os.remove(f)
    for dens, px in sizes.items():
        if base == 'mipmap-' + dens:
            for name in ('ic_launcher.png', 'ic_launcher_round.png'):
                resize(logo, os.path.join(d, name), px)
# densite klasoru olmayan durumlar icin yedek
fb = os.path.join(main, 'res/mipmap-xxxhdpi')
os.makedirs(fb, exist_ok=True)
for name in ('ic_launcher.png', 'ic_launcher_round.png'):
    p = os.path.join(fb, name)
    if not os.path.exists(p):
        resize(logo, p, 192)


# 5) ruse.pro gorunumu: siyah tema, logo, metinler
res = os.path.join(main, 'res')
cf = os.path.join(res, 'values/colors.xml')
t = open(cf, encoding='utf-8').read()
for name, val in (('background_app', '#000000'), ('background_status_bar', '#000000'),
                  ('background_bottom_bar', '#0A0A0F'), ('background_overlay', '#2A2A33'),
                  ('minebutton_color', '#B39DFF')):
    t = re.sub(r'(<color name="%s">)[^<]*(</color>)' % name, r'\g<1>%s\g<2>' % val, t)
open(cf, 'w', encoding='utf-8').write(t)

os.makedirs(os.path.join(res, 'drawable-nodpi'), exist_ok=True)
resize(logo, os.path.join(res, 'drawable-nodpi/ruse_logo.png'), 512)

fl = os.path.join(res, 'layout/fragment_launcher.xml')
t = open(fl, encoding='utf-8').read()
banner = """<ImageView
				android:id="@+id/ruse_logo"
				android:layout_width="match_parent"
				android:layout_height="140dp"
				android:padding="12dp"
				android:scaleType="fitCenter"
				android:src="@drawable/ruse_logo"
				app:layout_constraintTop_toTopOf="parent" />
			"""
anchor = '<com.kdt.mcgui.LauncherMenuButton\n\t\t\t\tandroid:id="@+id/news_button"'
if anchor in t:
    t = t.replace(anchor, banner + anchor, 1)
    # news / discord / divider artik logonun altindan baslasin
    for vid in ('news_button', 'discord_button'):
        i = t.index('android:id="@+id/' + vid + '"')
        j = t.index('/>', i)
        seg = t[i:j].replace('app:layout_constraintTop_toTopOf="parent"', 'app:layout_constraintTop_toBottomOf="@id/ruse_logo"')
        t = t[:i] + seg + t[j:]
    i = t.index('android:id="@+id/social_divider"')
    j = t.index('/>', i)
    seg = t[i:j].replace('app:layout_constraintTop_toTopOf="parent"', 'app:layout_constraintTop_toBottomOf="@id/ruse_logo"')
    t = t[:i] + seg + t[j:]
    open(fl, 'w', encoding='utf-8').write(t)
else:
    print('UYARI: ana menu duzeni degismis, logo eklenmedi')

for f in glob.glob(os.path.join(res, 'values*/strings.xml')):
    out = []
    for line in open(f, encoding='utf-8').read().split('\n'):
        if 'http' not in line and 'translatable="false"' not in line:
            line = re.sub(r'(?<![/\w.])PojavLauncher(?!Team)', 'ruse.pro', line)
            line = line.replace('Pojav Foreground Service', 'ruse.pro Service').replace('Pojav Modpack Installer', 'ruse.pro Modpack Installer')
        line = re.sub(r'(<string name="discord_invite"[^>]*>)[^<]*(</string>)', r'\1https://discord.gg/rusepro\2', line)
        out.append(line)
    open(f, 'w', encoding='utf-8').write('\n'.join(out))

# 4) kurulum sinifi + ruse.pro arayuzu + kancalar
def rep(path, old, new, count=1):
    t = open(path, encoding='utf-8').read()
    assert old in t, 'bulunamadi: %s in %s' % (old[:50], path)
    t = t.replace(old, new, count)
    open(path, 'w', encoding='utf-8').write(t)

dst = os.path.join(main, 'java/net/kdt/pojavlaunch')
shutil.copy(os.path.join(ad, 'RuseSetup.java'), dst)
rs = os.path.join(dst, 'RuseSetup.java')
t = open(rs, encoding='utf-8').read()
if 'volatile boolean ready' not in t:
    t = t.replace('private static boolean started;', 'private static boolean started;\n    public static volatile boolean ready;')
    a = t.index('boolean newProfile = setup();')
    b = t.index(': "ruse.pro guncel.";') + len(': "ruse.pro guncel.";')
    t = t[:a] + 'setup();\n                    ready = true;\n                    msg = "ruse.pro hazir, OYNA basabilirsin.";' + t[b:]
    t = t.replace('msg = "ruse.pro kurulum hatasi: " + t.getMessage();', 'msg = "ruse.pro kurulum hatasi: " + t.getMessage();\n                    synchronized (RuseSetup.class) { started = false; }')
    open(rs, 'w', encoding='utf-8').write(t)
open(os.path.join(dst, 'RuseUi.java'), 'w', encoding='utf-8').write(RUSE_UI)

# yeni ana ekran + girdi arka plani
open(fl, 'w', encoding='utf-8').write(RUSE_LAYOUT)
os.makedirs(os.path.join(res, 'drawable'), exist_ok=True)
open(os.path.join(res, 'drawable/ruse_input.xml'), 'w', encoding='utf-8').write(RUSE_INPUT)

# hesap secici gizli (hesap = nick)
rep(os.path.join(res, 'layout/activity_pojav_launcher.xml'),
    'android:id="@+id/account_spinner"', 'android:id="@+id/account_spinner"\n        android:visibility="gone"')

la = os.path.join(dst, 'LauncherActivity.java')
hook = 'setContentView(R.layout.activity_pojav_launcher);'
rep(la, hook, 'RuseUi.ensureAccount(this);\n        ' + hook + '\n        RuseSetup.start(this);')
rep(la, 'private mcAccountSpinner mAccountSpinner;',
    'private mcAccountSpinner mAccountSpinner;\n    public static mcAccountSpinner RUSE_SPINNER;')
rep(la, 'mAccountSpinner = findViewById(R.id.account_spinner);',
    'mAccountSpinner = findViewById(R.id.account_spinner);\n        RUSE_SPINNER = mAccountSpinner;')

sp = os.path.join(main, 'java/com/kdt/mcgui/mcAccountSpinner.java')
rep(sp, 'private void reloadAccounts(', """public void useLocalAccount(String nick) {
        try {
            MinecraftAccount acc = new MinecraftAccount();
            acc.username = nick;
            acc.save();
            PojavProfile.setCurrentProfile(getContext(), nick);
            mSelectecAccount = acc;
            if (!mAccountList.contains(nick)) mAccountList.add(nick);
        } catch (IOException e) {
            Log.e("ruse.pro", "hesap yazilamadi", e);
        }
    }

    private void reloadAccounts(""")

mf = os.path.join(main, 'java/net/kdt/pojavlaunch/fragments/MainMenuFragment.java')
rep(mf, 'mPlayButton.setOnClickListener(v -> ExtraCore.setValue(ExtraConstants.LAUNCH_GAME, true));',
    'RuseUi.bind(view);\n        mPlayButton.setOnClickListener(v -> RuseUi.play(requireActivity(), view));')
rep(mf, 'import net.kdt.pojavlaunch.R;', 'import net.kdt.pojavlaunch.R;\nimport net.kdt.pojavlaunch.RuseUi;')
print('ruse.pro yamasi uygulandi')
