# Platform Data Model SDI

Platform ini adalah aplikasi berbasis web untuk manajemen ontologi menggunakan Gradio. Dengan Platform ini, pengguna dapat:
- Mengunggah file ontologi (`.owl`)
- Mengonversi file `.csv` atau `.xlsx` ke dalam format `.owl`
- Membandingkan dua ontologi dan menganalisis kesamaan serta perbedaannya
- Menggabungkan dua ontologi
- Melihat isi file ontologi

## Fitur
1. **Upload Ontologi**: Mengunggah file `.owl` dan menyimpan metadata-nya.
2. **Konversi Model Data ke Ontologi**: Mengubah file `.csv` atau `.xlsx` menjadi format ontologi.
3. **Perbandingan Ontologi**: Membandingkan dua ontologi berdasarkan kelas, relasi, dan properti.
4. **Merge Ontologi**: Menggabungkan dua file ontologi menjadi satu.
5. **Daftar Ontologi**: Melihat isi dari file ontologi yang telah diunggah.

## Instalasi
1. Clone repositori ini:
   ```bash
   git clone <repository_url>
   cd <repository_directory>

2. Install dependency
   pip install -r requirements.txt

## Jalankan Aplikasi 
python app.py
