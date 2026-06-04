import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product

@csrf_exempt
def api_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        u = data.get('username')
        p = data.get('password')
        
        # Logika login dipindah ke sini
        if u == "sahabat" and p == "sahabatstok":
            return JsonResponse({"status": "sukses", "user": "Budi Santoso"})
        return JsonResponse({"status": "gagal", "pesan": "Username atau password salah!"}, status=401)

def api_dashboard(request):
    # Mengambil semua produk dari database (yang sebelumnya kamu input di Admin)
    products = list(Product.objects.all().values('name', 'total_qty', 'price'))
    
    if not products:
        return JsonResponse({"products": [], "total_terjual": 0, "rata_rata": 0, "top_product": None})

    total_terjual = sum(p['total_qty'] for p in products)
    rata_rata = round(total_terjual / len(products))
    # Mengurutkan untuk mencari top product
    top_product = sorted(products, key=lambda x: x['total_qty'], reverse=True)[0]

    return JsonResponse({
        "products": products,
        "total_terjual": total_terjual,
        "rata_rata": rata_rata,
        "top_product": top_product
    })

@csrf_exempt
def api_predict(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        nama_produk = data.get('product_name')
        week = int(data.get('week'))
        month = data.get('month')
        year = int(data.get('year'))
        
        try:
            prod = Product.objects.get(name=nama_produk)
            base = prod.total_qty / 52
            
            # Rumus matematika prediksi dipindah ke sini (sebelum diganti model ML nanti)
            factors = {
                "Januari": 0.92, "Februari": 0.94, "Maret": 0.97, "April": 1.02,
                "Mei": 1.06, "Juni": 1.05, "Juli": 1.0, "Agustus": 0.98,
                "September": 1.02, "Oktober": 1.09, "November": 1.15, "Desember": 1.22
            }
            factor = factors.get(month, 1.0)
            yearBonus = (year - 2024) * 0.018
            val = round(base * (factor + yearBonus))
            if week >= 3:
                val = round(val * 1.01)
            pred_val = max(10, val)

            return JsonResponse({
                "status": "sukses",
                "prediction": pred_val,
                "product": {"name": prod.name, "totalQty": prod.total_qty, "price": prod.price}
            })
        except Product.DoesNotExist:
            return JsonResponse({"status": "gagal", "pesan": "Produk tidak ditemukan"}, status=404)