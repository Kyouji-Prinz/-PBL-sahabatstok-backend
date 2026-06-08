import os
import django
import pandas as pd

# 1. Menghubungkan skrip dengan Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistem_backend.settings')
django.setup()

from api_stok.models import Product

# 2. BACA KEDUA FAIL DATASET SEKALIGUS
path_mingguan = os.path.join('data', 'processed', 'data_proses_mingguan.csv')
path_bulanan = os.path.join('data', 'processed', 'data_proses_bulanan.csv')

df_mingguan = pd.read_csv(path_mingguan)
df_bulanan = pd.read_csv(path_bulanan)

# 3. Hitung total masing-masing
agg_mingguan = df_mingguan.groupby('Sub-Category').agg({'Quantity': 'sum', 'Sales': 'sum'}).reset_index()
agg_bulanan = df_bulanan.groupby('Sub-Category').agg({'Quantity': 'sum', 'Sales': 'sum'}).reset_index()

# 4. GABUNGKAN KEDUA DATA (15 Mingguan + 2 Bulanan = 17 Total)
# Menggunakan pd.concat untuk menyatukan baris dari kedua dataframe
agg_gabungan = pd.concat([agg_mingguan, agg_bulanan], ignore_index=True)

# 5. Kosongkan database sebelum diisi ulang
Product.objects.all().delete()

# 6. Suntikkan 17 nama kategori gabungan ke database Django
for index, row in agg_gabungan.iterrows():
    sub_cat = row['Sub-Category']
    qty = int(row['Quantity'])
    price = int(row['Sales'] / qty) if qty > 0 else 0 
    
    Product.objects.create(name=sub_cat, total_qty=qty, price=price)
    print(f"Sukses sinkronisasi: {sub_cat} (Kuantitas: {qty} pcs)")

print("✅ SINKRONISASI GABUNGAN BERHASIL! (Kini genap 17 Kategori)")