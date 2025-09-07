## BotFsub

Script ini dirancang oleh ***Kaisar Udin*** sehingga tinggal menjalankannya, bot ini juga memiliki beberapa fitur diantaranya adalah Fsub dan Broadcast.

### Cara menjalankan Script

Sebelum menjalankan script, install dulu paket dasarnya:

```bash
pkg update
pkg upgrade
pkg install python
pkg install git
pkg install python-pip
pip install telethon 
```

Setelah semuanya terinstall, sekarang langkah-langkah untuk menjalankan scriptnya:

1. Klone repository:
   ```bash
   git clone https://github.com/hackermbrebed/botfsub
   ```

2. Masuk ke direktory:
   ```bash
   cd botfsub
   ```

3. Konfigurasi file .env:
   ```bash
   nano .env
   ```
   Setelah masuk ke tampilan file .env silahkan isi *API_ID, API_HUSH, BOT_TOKEN, CHANNEL_ID, CHANNEL_LINK, ADMIN_ID* dengan punya kalian.
   Untuk keluar dari file .env tekan Crtl+O lalu enter, tekan lagi Ctrl+X

5. Install requirement:
   ```bash
   pip install -r requirements.txt
   ```

   ```bash
   git pull origin main
   ```
6. Jalankan bot.
   ```bash
   python main.py
   ```
Jika sudah muncul tulisan ***Connecting*** pada terminal, maka bot sudah berhasil dijalankan.
<blockquote>
<b>   

   Bayanganmu menutupi singgasanaku

Kau terlalu tinggi

Menunduklah padaku!
</b>
</blockquote>
