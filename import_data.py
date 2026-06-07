import os
import django
import pandas as pd

# 1. Menghubungkan skrip dengan Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistem_backend.settings')
django.setup()

from api_stok.models import Product

# 2. Membaca langsung file proses mingguan murni
path_csv = os.path.join('data', 'processed', 'data_proses_mingguan.csv')
df = pd.read_csv(path_csv)

# 3. Menghitung total historis berdasarkan Sub-Category asli dataset
agg = df.groupby('Sub-Category').agg({'Quantity': 'sum', 'Sales': 'sum'}).reset_index()

# 4. Kosongkan database dari sisa-sisa data lama
Product.objects.all().delete()

# 5. Suntikkan nama asli kategori ke database Django
for index, row in agg.iterrows():
    sub_cat = row['Sub-Category']
    qty = int(row['Quantity'])
    price = int(row['Sales'] / qty) if qty > 0 else 0 
    
    Product.objects.create(name=sub_cat, total_qty=qty, price=price)
    print(f"Sukses sinkronisasi: {sub_cat} (Kuantitas: {qty} pcs)")

print("✅ SINKRONISASI DATASET BERHASIL SEPENUHNYA!")