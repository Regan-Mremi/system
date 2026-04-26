from django.shortcuts import render, redirect
from django.utils.timezone import now
from datetime import timedelta, datetime

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse, JsonResponse

from openpyxl import Workbook
import json

from .models import Item, Order, OrderItem
from .printer import print_order


# =========================
# 🔐 AUTH CHECK
# =========================
def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def reports_page(request):
    return render(request, "menu/reports.html")
# =========================
# 🍔 MENU
# =========================
def menu_view(request):
    items = Item.objects.all()
    return render(request, 'menu/menu.html', {'items': items})


# =========================
# 🧾 CREATE ORDER
# =========================
def create_order(request):
    if request.method == 'POST':

        order = Order.objects.create(status="Pending")

        for key, value in request.POST.items():
            if key.startswith('item_') and int(value) > 0:
                item_id = key.split('_')[1]
                item = Item.objects.get(id=item_id)

                OrderItem.objects.create(
                    order=order,
                    item=item,
                    quantity=int(value)
                )

        print_order(order)
        return redirect('menu')

    return redirect('menu')


# =========================
# 👨‍🍳 KITCHEN
# =========================
def kitchen_view(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'menu/kitchen.html', {'orders': orders})


# =========================
# 📊 DASHBOARD (FIXED)
# =========================
@login_required
@user_passes_test(is_admin)
def dashboard_view(request):
    today = now().date()

    daily_orders = Order.objects.filter(created_at__date=today)
    daily_total = sum(o.total_price() for o in daily_orders)

    monthly_orders = Order.objects.filter(
        created_at__year=today.year,
        created_at__month=today.month
    )
    monthly_total = sum(o.total_price() for o in monthly_orders)

    yearly_orders = Order.objects.filter(created_at__year=today.year)
    yearly_total = sum(o.total_price() for o in yearly_orders)

    labels = []
    data = []

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        orders = Order.objects.filter(created_at__date=day)
        total = sum(o.total_price() for o in orders)

        labels.append(day.strftime("%d %b"))
        data.append(float(total))

    return render(request, 'menu/dashboard.html', {
        'daily_total': daily_total,
        'monthly_total': monthly_total,
        'yearly_total': yearly_total,
        'labels': json.dumps(labels),
        'data': json.dumps(data),
    })


# =========================
# 📥 EXPORT EXCEL (FIXED - NO SALE MODEL)
# =========================
@login_required
@user_passes_test(is_admin)
def export_excel(request):

    period = request.GET.get("period", "daily")

    wb = Workbook()
    ws = wb.active
    ws.title = "Sales Report"

    ws.append(["Order ID", "Date", "Total Amount"])

    today = datetime.now().date()

    # =======================
    # USE ORDERS ONLY (FIXED)
    # =======================

    if period == "daily":
        orders = Order.objects.filter(created_at__date=today)

    elif period == "monthly":
        orders = Order.objects.filter(
            created_at__year=today.year,
            created_at__month=today.month
        )

    elif period == "yearly":
        orders = Order.objects.filter(created_at__year=today.year)

    else:
        orders = Order.objects.all()

    total = 0

    for order in orders:
        price = float(order.total_price())

        ws.append([
            order.id,
            order.created_at.strftime("%Y-%m-%d %H:%M"),
            price
        ])

        total += price

    ws.append([])
    ws.append(["TOTAL", "", total])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    filename = f"orders_{period}.xlsx"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    wb.save(response)
    return response


# =========================
# 🔑 LOGIN
# =========================
def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Wrong username or password")

    return render(request, 'menu/login.html')


# =========================
# 🚪 LOGOUT
# =========================
def logout_view(request):
    logout(request)
    return redirect('login')


# =========================
# 📊 CHART API
# =========================
def chart_data(request):
    return JsonResponse({
        "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "data": [14, 22, 18, 35, 28, 30, 45]
    })