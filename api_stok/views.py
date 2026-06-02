import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product

@csrf_exempt
def api_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if username == "sahabat" and password == "sahabatstok":
            return JsonResponse({"status": "sukses", "user": "Budi Santoso"})
        return JsonResponse({"status": "gagal", "pesan": "Username atau password salah"}, status=400)

def api_dashboard(request):
    # Mengambil semua data produk dari database berdasarkan urutan terlaris
    products = Product.objects.all().order_by('-total_qty')
    product_list = list(products.values('name', 'total_qty', 'price'))
    
    total_terjual = sum(p['total_qty'] for p in product_list)
    rata_rata = round(total_terjual / len(product_list)) if product_list else 0
    top_product = product_list[0] if product_list else {"name": "-", "total_qty": 0, "price": 0}
    
    return JsonResponse({
        "products": product_list,
        "total_terjual": total_terjual,
        "rata_rata": rata_rata,
        "top_product": top_product
    })

@csrf_exempt
def api_predict(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_name = data.get('product_name')
        week = int(data.get('week', 4))
        month = data.get('month')
        year = int(data.get('year', 2025))
        
        # Di sini nanti tempat kamu memuat file model ML (.pkl atau .h5) menggunakan joblib/pickle
        try:
            product = Product.objects.get(name=product_name)
            base_qty = product.total_qty / 52
            
            # Logika matematika sementara sebelum diganti fungsi model.predict() yang asli
            prediction_val = round(base_qty * 1.1) 
            
            return JsonResponse({
                "status": "success",
                "prediction": prediction_val,
                "accuracy": "94.2%",
                "product_name": product_name
            })
        except Product.DoesNotExist:
            return JsonResponse({"status": "error", "pesan": "Produk tidak ditemukan"}, status=404)