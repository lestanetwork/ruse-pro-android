package net.kdt.pojavlaunch;

import android.app.Activity;
import android.util.Log;
import android.widget.Toast;

import net.kdt.pojavlaunch.prefs.LauncherPreferences;
import net.kdt.pojavlaunch.value.launcherprofiles.LauncherProfiles;
import net.kdt.pojavlaunch.value.launcherprofiles.MinecraftProfile;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Map;

public final class RuseSetup {
    private static final String TAG = "ruse.pro";
    private static final String MC = "1.21.4";
    private static final String MOD_URL = "https://raw.githubusercontent.com/lestanetwork/ruse-pro.github.io/main/rusepro.jar";
    private static boolean started;

    private RuseSetup() {}

    public static synchronized void start(final Activity act) {
        if (started) return;
        started = true;
        new Thread(new Runnable() {
            @Override public void run() {
                String msg;
                try {
                    boolean newProfile = setup();
                    msg = newProfile
                            ? "ruse.pro kuruldu! Launcher'i kapatip tekrar ac, sonra OYNA."
                            : "ruse.pro guncel.";
                } catch (Throwable t) {
                    Log.e(TAG, "setup failed", t);
                    msg = "ruse.pro kurulum hatasi: " + t.getMessage();
                }
                final String m = msg;
                act.runOnUiThread(new Runnable() {
                    @Override public void run() { Toast.makeText(act, m, Toast.LENGTH_LONG).show(); }
                });
            }
        }, "ruse-setup").start();
    }

    private static boolean setup() throws Exception {
        File versions = new File(Tools.DIR_HOME_VERSION);
        File mods = new File(Tools.DIR_GAME_NEW, "mods");
        mods.mkdirs();

        File vj = new File(versions, MC + "/" + MC + ".json");
        if (!vj.exists()) {
            JSONObject manifest = new JSONObject(getString("https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"));
            JSONArray vs = manifest.getJSONArray("versions");
            String url = null;
            for (int i = 0; i < vs.length(); i++) {
                if (MC.equals(vs.getJSONObject(i).getString("id"))) { url = vs.getJSONObject(i).getString("url"); break; }
            }
            if (url == null) throw new Exception("Minecraft " + MC + " bulunamadi");
            writeFile(vj, getBytes(url));
        }

        JSONArray loaders = new JSONArray(getString("https://meta.fabricmc.net/v2/versions/loader/" + MC));
        String loaderVer = null;
        for (int i = 0; i < loaders.length() && loaderVer == null; i++) {
            JSONObject l = loaders.getJSONObject(i).getJSONObject("loader");
            if (l.optBoolean("stable", false)) loaderVer = l.getString("version");
        }
        if (loaderVer == null) loaderVer = loaders.getJSONObject(0).getJSONObject("loader").getString("version");
        String fabricId = "fabric-loader-" + loaderVer + "-" + MC;
        File fj = new File(versions, fabricId + "/" + fabricId + ".json");
        if (!fj.exists()) {
            writeFile(fj, getBytes("https://meta.fabricmc.net/v2/versions/loader/" + MC + "/" + loaderVer + "/profile/json"));
        }

        boolean hasApi = false;
        File[] existing = mods.listFiles();
        if (existing != null) for (File f : existing) if (f.getName().toLowerCase().startsWith("fabric-api")) hasApi = true;
        if (!hasApi) {
            String q = "?game_versions=%5B%22" + MC + "%22%5D&loaders=%5B%22fabric%22%5D";
            JSONArray vers = new JSONArray(getString("https://api.modrinth.com/v2/project/fabric-api/version" + q));
            JSONArray files = vers.getJSONObject(0).getJSONArray("files");
            JSONObject pick = files.getJSONObject(0);
            for (int i = 0; i < files.length(); i++) if (files.getJSONObject(i).optBoolean("primary")) pick = files.getJSONObject(i);
            writeFile(new File(mods, pick.getString("filename")), getBytes(pick.getString("url")));
        }

        File jar = new File(mods, "ruse-pro.jar");
        try {
            byte[] b = getBytes(MOD_URL + "?t=" + System.currentTimeMillis());
            if (b.length < 4 || b[0] != 'P' || b[1] != 'K') throw new Exception("gecersiz jar");
            writeFile(jar, b);
        } catch (Exception e) {
            if (!jar.exists()) throw new Exception("Mod indirilemedi: " + e.getMessage());
            Log.w(TAG, "mod guncellenemedi, eski surum kullaniliyor", e);
        }

        synchronized (RuseSetup.class) {
            LauncherProfiles.load();
            String key = null;
            for (Map.Entry<String, MinecraftProfile> e : LauncherProfiles.mainProfileJson.profiles.entrySet()) {
                if ("ruse.pro".equals(e.getValue().name)) { key = e.getKey(); break; }
            }
            boolean created = key == null;
            if (created) {
                MinecraftProfile p = new MinecraftProfile();
                p.name = "ruse.pro";
                p.lastVersionId = fabricId;
                key = LauncherProfiles.getFreeProfileKey();
                LauncherProfiles.mainProfileJson.profiles.put(key, p);
                LauncherPreferences.DEFAULT_PREF.edit().putString(LauncherPreferences.PREF_KEY_CURRENT_PROFILE, key).apply();
            } else {
                LauncherProfiles.mainProfileJson.profiles.get(key).lastVersionId = fabricId;
            }
            LauncherProfiles.write();
            return created;
        }
    }

    private static byte[] getBytes(String u) throws Exception {
        HttpURLConnection c = (HttpURLConnection) new URL(u).openConnection();
        c.setConnectTimeout(15000);
        c.setReadTimeout(60000);
        c.setRequestProperty("User-Agent", "ruse-pro-mobile/1.0");
        if (c.getResponseCode() != 200) throw new Exception(u + " -> HTTP " + c.getResponseCode());
        InputStream in = c.getInputStream();
        try {
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            byte[] buf = new byte[16384];
            int n;
            while ((n = in.read(buf)) > 0) out.write(buf, 0, n);
            return out.toByteArray();
        } finally {
            in.close();
        }
    }

    private static String getString(String u) throws Exception { return new String(getBytes(u), "UTF-8"); }

    private static void writeFile(File f, byte[] data) throws Exception {
        f.getParentFile().mkdirs();
        File tmp = new File(f.getPath() + ".part");
        FileOutputStream o = new FileOutputStream(tmp);
        try { o.write(data); } finally { o.close(); }
        if (f.exists()) f.delete();
        if (!tmp.renameTo(f)) throw new Exception("yazilamadi: " + f.getName());
    }
}
