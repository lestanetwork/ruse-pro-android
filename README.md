# ruse.pro mobil (Android APK)

Bu klasör, PojavLauncher'ı **ruse.pro** adı/ikonu ile derleyen GitHub Actions kurulumudur. Uygulama her açıldığında Fabric 1.21.4'ü,
Fabric API'yi ve modu (`lestanetwork/ruse-pro.github.io/rusepro.jar`) kendisi indirir/günceller ve "ruse.pro" profilini hazırlar.

## APK'yı derleme
1. Yeni **herkese açık** bir GitHub deposu aç (örn. `ruse-pro-android`) ve bu klasörün içeriğini (`.github`, `android`) olduğu gibi yükle.
2. Depoda **Actions** sekmesi → "Build ruse.pro APK" → **Run workflow**. (~20-40 dk sürer.)
3. Bitince çalışmanın altındaki **Artifacts → ruse-pro-apk** dosyasını indir, zip'ten çıkan `ruse-pro.apk`'yı telefona kur
   ("bilinmeyen kaynaklardan yükleme" izni gerekir).

## Telefonda ilk kullanım
1. Uygulamayı aç; "ruse.pro kuruldu" yazısını bekle, **uygulamayı kapatıp tekrar aç**, profil olarak **ruse.pro** seçili gelir.
2. Hesap: "offline" ile bir isim gir (Microsoft girişi istersen premium hesabınla da girebilirsin).
3. **OYNA.** İlk açılışta oyun dosyaları iner (birkaç dakika).
4. Menü: ruse.pro menüsünü açmak için sohbete `.gui` yaz (ya da Pojav'ın kontrol düzenleyicisinde bir tuşa **Right Shift** ata).

## Notlar
- Test edemediğim bir kurulum: ilk derlemede hata çıkarsa Actions günlüğünü yapıştır, düzeltiriz.
- JRE dosyaları Pojav ekibinin Actions artifact'larından gelir; süresi dolmuşsa JRE adımı hata verir.
- Mod güncellemesi: GitHub'daki `rusepro.jar`'ı değiştirmen yeter, uygulama bir sonraki açılışta çeker.

## Android Studio ile yerelde derleme (Windows)
Gerekenler: Git, Python 3 (`pip install pillow`), Android Studio (SDK Manager'dan **NDK 25.2.9519653** ve SDK 34 kur).
```
git clone --recursive -b v3_openjdk https://github.com/PojavLauncherTeam/PojavLauncher pojav
python android\patch.py pojav android
```
Sonra elle: (a) `https://github.com/PojavLauncherTeam/LTW/releases/latest/download/ltw-release.aar` dosyasını `pojav\app_pojavlauncher\libs\` içine koy;
(b) JRE'ler: github.com/PojavLauncherTeam/android-openjdk-build-multiarch -> Actions -> `buildjre8` dalındaki son yeşil çalışmadan `jre8-pojav`,
`buildjre17-21` dalından `jre17-pojav` ve `jre21-pojav` artifact'larını indir (GitHub girişi ister); zip içeriklerini sırayla
`pojav\app_pojavlauncher\src\main\assets\components\jre`, `...\jre-new`, `...\jre-21` klasörlerine aç;
(c) Git Bash'te `cd pojav && ./scripts/languagelist_updater.sh`. Sonra Android Studio ile `pojav` klasörünü aç, Build -> Build APK(s) (debug).
APK: `pojav\app_pojavlauncher\build\outputs\apk\debug\`.
