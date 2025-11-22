# Setup our Project MasBroww
**the Step's ister**

pertama2 masse clone dulu repo aing :
```https://github.com/dayattt111/reCaptcha_bypass.git```

baru abis tu ngana install juga `ffmpeg` untuk bypass audio na nanti masbrow.
caranya tuh gini masse :
```https://www.gyan.dev/ffmpeg/builds/```

di link diatas jadi folder yang ada `*.7z` na kalau `windows` sih. kalau `linux/mac` cari aja ndiri ada2 ji itu.

setelah di clone ada 1 folder dan 1 file itu.
nah masuk mi ke folder na brow , nu tauji cara na toh? nda tau ? berhanti mako jadi programmer do', ternak lele mako.
gini eh :
```cd {Nama_Folder}```

implementasi na tu gini di repo aing teh :
```cd GoogleRecaptchaBypass```

gitu.
nah terus ada tuh kan file requirentmt.txt maap klo typo namana jga manusiya.
nah perhatikan ini sy menggunakan python, jadi harus install python dlu.

bikin virtual .env dlu biar pkg dan lib na nda bentrok hehe.
carana gampan ugha (`windows`) :

`py -m venv {nama_env}` / `py -m venv .env` 

nah jadi mi. kalau linux cari mako sendiri do' banyak ji carana,  ka ku tahu inisial Akmal ji mau coba heheee...
lanjut.
install req text na 

```pip -r req.txt``` !sesuai nama na yh txt na.

baru masuk ke file `test.py` disitu ada :
```driver.get("https://patrickhlauke.github.io/recaptcha/")```
disitu nu ubah mi ke url mu yg mau di byPass.

jadi deh.

jdi nnti ada captcha awal puzzel yang bakal deteksi apakah dari script/bot, jika iya akan lanjut ke captcha audio, tpi di script` RecaptchaSolver.py` sudah saya atur 10 detik, jadi butuh waktu 10 detik untuk bypass itu masbrow.

oh iyo itu `index.html` bukan contoh na nah, kah generate gpt ji.