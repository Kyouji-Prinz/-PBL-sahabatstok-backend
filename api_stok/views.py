import json
import os
import pickle
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Product

# 1. Kamus Pemetaan Nama Produk (Mendukung Nama Pendek Dataset & Nama Panjang Frontend)
MODEL_MAPPING = {
    "Accessories": "model_weekly_accessories.pkl",
    "Computer Peripherals": "model_weekly_accessories.pkl",
    
    "Appliances": "model_weekly_appliances.pkl",
    
    "Art": "model_weekly_art.pkl",
    "Pens & Art Supplies": "model_weekly_art.pkl",
    
    "Binders": "model_weekly_binders.pkl",
    "Binders & Binder Accessories": "model_weekly_binders.pkl",
    
    "Bookcases": "model_weekly_bookcase.pkl",
    
    "Chairs": "model_weekly_chairs.pkl",
    "Chairs & Chairmats": "model_weekly_chairs.pkl",
    
    "Copiers": "model_manual_monthly.pkl",
    "Copiers & Fax": "model_manual_monthly.pkl",
    
    "Envelopes": "model_weekly_envelopes.pkl",
    
    "Fasteners": "model_weekly_fasteners.pkl",
    "Rubber Bands": "model_weekly_fasteners.pkl",
    
    "Furnishings": "model_weekly_furnishings.pkl",
    "Office Furnishings": "model_weekly_furnishings.pkl",
    
    "Labels": "model_weekly_labels.pkl",
    
    "Machines": "model_manual_monthly.pkl",
    "Office Machines": "model_manual_monthly.pkl",
    
    "Paper": "model_weekly_paper.pkl",
    
    "Phones": "model_weekly_phone.pkl",
    "Telephones & Communication": "model_weekly_phone.pkl",
    
    "Storage": "model_weekly_storage.pkl",
    "Storage & Organization": "model_weekly_storage.pkl",
    
    "Supplies": "model_weekly_supplies.pkl",
    "Scissors, Rulers & Trimmers": "model_weekly_supplies.pkl",
    
    "Tables": "model_weekly_tables.pkl"
}

# 2. Kamus Sandi Angka untuk Model Global Bulanan (Mendukung Kedua Versi Nama)
SUB_CAT_MAPPING = {
    "Accessories": 0, "Computer Peripherals": 0,
    "Appliances": 1,
    "Art": 2, "Pens & Art Supplies": 2,
    "Binders": 3, "Binders & Binder Accessories": 3,
    "Bookcases": 4,
    "Chairs": 5, "Chairs & Chairmats": 5,
    "Copiers": 6, "Copiers & Fax": 6,
    "Envelopes": 7,
    "Fasteners": 8, "Rubber Bands": 8,
    "Furnishings": 9, "Office Furnishings": 9,
    "Labels": 10,
    "Machines": 11, "Office Machines": 11,
    "Paper": 12,
    "Phones": 13, "Telephones & Communication": 13,
    "Storage": 14, "Storage & Organization": 14,
    "Supplies": 15, "Scissors, Rulers & Trimmers": 15,
    "Tables": 16
}

# 3. Kamus Penerjemah Teks Bulan ke Angka
BULAN_MAPPING = {
    "Januari": 1, "Februari": 2, "Maret": 3, "April": 4,
    "Mei": 5, "Juni": 6, "Juli": 7, "Agustus": 8,
    "September": 9, "Oktober": 10, "November": 11, "Desember": 12
}

@csrf_exempt
def api_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        u = data.get('username')
        p = data.get('password')
        if u == "sahabat" and p == "sahabatstok":
            return JsonResponse({"status": "sukses", "user": "Budi Santoso"})
        return JsonResponse({"status": "gagal", "pesan": "Username atau password salah!"}, status=401)

def api_dashboard(request):
    products = list(Product.objects.all().values('name', 'total_qty', 'price'))
    if not products:
        return JsonResponse({"products": [], "total_terjual": 0, "rata_rata": 0, "top_product": None})

    total_terjual = sum(p['total_qty'] for p in products)
    rata_rata = round(total_terjual / len(products))
    top_product = sorted(products, key=lambda x: x['total_qty'], reverse=True)[0]

    return JsonResponse({
        "products": products, "total_terjual": total_terjual,
        "rata_rata": rata_rata, "top_product": top_product
    })

@csrf_exempt
def api_predict(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        nama_produk = data.get('product_name')
        week = int(data.get('week', 4))
        bulan_teks = data.get('month')
        year = int(data.get('year'))
        
        tipe_prediksi = data.get('type', 'weekly')
        bulan_angka = BULAN_MAPPING.get(bulan_teks, 1)
        
        try:
            # Mencari data produk berdasarkan nama yang dikirim oleh frontend
            prod = Product.objects.get(name=nama_produk)
            
            # Menentukan file model berdasarkan tipe prediksi (weekly/monthly)
            if tipe_prediksi == 'monthly':
                nama_file_model = "model_manual_monthly.pkl"
            else:
                nama_file_model = MODEL_MAPPING.get(nama_produk)
            
            if not nama_file_model:
                return JsonResponse({"status": "gagal", "pesan": f"Model AI untuk {nama_produk} belum tersedia."}, status=400)
            
            model_path = os.path.join(settings.BASE_DIR, 'model manual', 'models', 'by_mlflow', nama_file_model)
            
            with open(model_path, 'rb') as file:
                model_ml = pickle.load(file)
            
            # --- PROSES REKAYASA DATA DENGAN SIMULASI MUSIMAN ---
            discount = 0.05
            
            # 1. Pola fluktuasi bulanan (Simulasi tren penjualan ritel)
            pola_bulanan = {
                1: 0.85,  # Januari (Turun setelah libur panjang)
                2: 0.90,
                3: 0.98,
                4: 1.12,  # April (Naik untuk persiapan kuartal 2)
                5: 1.05,
                6: 0.95,
                7: 1.00,
                8: 0.93,
                9: 1.02,
                10: 1.10, # Oktober (Mulai tren akhir tahun)
                11: 1.18, # November (Peningkatan signifikan)
                12: 1.30  # Desember (Puncak tertinggi akhir tahun)
            }
            faktor_bulan = pola_bulanan.get(bulan_angka, 1.0)
            
            # 2. Pola pertumbuhan tahunan (Asumsi pertumbuhan 3% per tahun dari 2024)
            faktor_tahun = 1.0 + ((year - 2024) * 0.03) if year >= 2024 else 1.0
            
            if tipe_prediksi == 'monthly':
                avg_monthly_qty = prod.total_qty / 12
                
                # Mengaplikasikan multiplier dinamis
                qty_lag = avg_monthly_qty * faktor_bulan * faktor_tahun
                sales_lag = qty_lag * float(prod.price)
                sub_cat_encoded = SUB_CAT_MAPPING.get(nama_produk, 0)
                
                # Format fitur input model bulanan Dea
                fitur_input = [[discount, qty_lag, qty_lag * 0.95, qty_lag, sales_lag, sales_lag * 0.20, bulan_angka, year, sub_cat_encoded]]
                base_banding = qty_lag
            else:
                avg_weekly_qty = prod.total_qty / 52
                
                # Mengaplikasikan multiplier dinamis & variasi minggu
                variasi_minggu = 1.0 + (week * 0.01)
                qty_lag = avg_weekly_qty * faktor_bulan * faktor_tahun * variasi_minggu
                sales_lag = qty_lag * float(prod.price)
                
                # Format fitur input model mingguan Dea
                fitur_input = [[discount, qty_lag, qty_lag * 0.95, qty_lag, sales_lag, sales_lag * 0.20, bulan_angka, year, week]]
                base_banding = qty_lag
            # --- SELESAI PROSES REKAYASA DATA ---
            
            # --- JALANKAN PREDIKSI MACHINE LEARNING ---
            hasil_prediksi = model_ml.predict(fitur_input)
            pred_val = int(hasil_prediksi[0])
            pred_val = max(10, pred_val)
            
            # --- KALKULASI METRIK EVALUASI BISNIS ---
            percentage = ((pred_val - base_banding) / base_banding) * 100 if base_banding > 0 else 0
            predicted_sales = pred_val * float(prod.price)
            predicted_profit = predicted_sales * 0.20
            
            return JsonResponse({
                "status": "sukses",
                "prediction": pred_val,
                "metrics": {
                    "percentage": round(percentage, 1),
                    "sales": predicted_sales,
                    "profit": predicted_profit,
                    "stock_buffer": int(pred_val * 1.1),
                    "stock_reorder": int(pred_val * 0.3)
                },
                "product": {"name": prod.name, "totalQty": prod.total_qty, "price": prod.price}
            })
            
        except Product.DoesNotExist:
            return JsonResponse({"status": "gagal", "pesan": f"Produk '{nama_produk}' tidak ditemukan di pangkalan data server."}, status=404)
        except FileNotFoundError:
            return JsonResponse({"status": "gagal", "pesan": f"Berkas model {nama_file_model} tidak ditemukan di folder server."}, status=500)
        except Exception as e:
            return JsonResponse({"status": "gagal", "pesan": f"Kesalahan internal mesin AI: {str(e)}"}, status=500)