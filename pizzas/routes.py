from flask import render_template, request, redirect, url_for, session, flash
from datetime import date
from . import pizzas
from forms import PizzaForm
from models import db, Cliente, Pedido, DetallePedido, Pizza
from sqlalchemy import extract
from datetime import datetime


PRECIOS_TAMANO = {
    "Chica": 40,
    "Mediana": 80,
    "Grande": 120
}

PRECIOS_INGREDIENTES = {
    "Jamon": 10,
    "Pina": 10,
    "Champinones": 10
}




@pizzas.route("/", methods=["GET"])
@pizzas.route("/index", methods=["GET"])
def index():
    form = PizzaForm()

    if "detalle_pedido" not in session:
        session["detalle_pedido"] = []

    detalle_pedido = session["detalle_pedido"]

    if detalle_pedido:
        primer_item = detalle_pedido[0]
        form.nombre.data = primer_item["nombre"]
        form.direccion.data = primer_item["direccion"]
        form.telefono.data = primer_item["telefono"]
        form.fecha.data = datetime.strptime(primer_item["fecha"], "%Y-%m-%d").date()

    pedidos_hoy = Pedido.query.filter(Pedido.fecha == date.today()).all()

    ventas_dia = []
    total_dia = 0

    for pedido in pedidos_hoy:
        ventas_dia.append({
            "nombre": pedido.cliente.nombre,
            "total": float(pedido.total)
        })
        total_dia += float(pedido.total)

    return render_template(
        "Pizzas/index.html",
        form=form,
        pizzas=detalle_pedido,
        ventas_dia=ventas_dia,
        total_dia=total_dia
    )

@pizzas.route("/agregar", methods=["POST"])
def agregar():
    form = PizzaForm()

    if "detalle_pedido" not in session:
        session["detalle_pedido"] = []

    if not form.validate_on_submit():
        flash("Completa correctamente el formulario.", "danger")
        return redirect(url_for("pizzas.index"))

    tamano = form.tamano.data
    ingredientes = form.ingredientes.data
    cantidad = form.cantidad.data
    fecha = form.fecha.data

    precio_tamano = PRECIOS_TAMANO.get(tamano, 0)
    total_ingredientes = sum(PRECIOS_INGREDIENTES.get(i, 0) for i in ingredientes)

    precio_unitario = precio_tamano + total_ingredientes
    subtotal = precio_unitario * cantidad

    detalle_pedido = session["detalle_pedido"]

    detalle_pedido.append({
        "tamano": tamano,
        "ingredientes": ", ".join(ingredientes) if ingredientes else "Sin ingredientes",
        "cantidad": cantidad,
        "precio_unitario": precio_unitario,
        "subtotal": subtotal,
        "nombre": form.nombre.data,
        "direccion": form.direccion.data,
        "telefono": form.telefono.data,
        "fecha": str(fecha)
    })

    session["detalle_pedido"] = detalle_pedido
    session.modified = True

    flash("Pizza agregada correctamente.", "success")
    return redirect(url_for("pizzas.index"))


@pizzas.route("/quitar", methods=["POST"])
def quitar():
    indice = int(request.form.get("indice"))

    if "detalle_pedido" in session:
        detalle_pedido = session["detalle_pedido"]

        if 0 <= indice < len(detalle_pedido):
            detalle_pedido.pop(indice)
            session["detalle_pedido"] = detalle_pedido
            session.modified = True
            flash("Pizza eliminada correctamente.", "info")

    return redirect(url_for("pizzas.index"))


@pizzas.route("/terminar", methods=["POST"])
def terminar():
    if "detalle_pedido" not in session or not session["detalle_pedido"]:
        flash("No hay productos en el pedido.", "danger")
        return redirect(url_for("pizzas.index"))

    detalle_pedido = session["detalle_pedido"]
    primer_item = detalle_pedido[0]

    nombre = primer_item["nombre"]
    direccion = primer_item["direccion"]
    telefono = primer_item["telefono"]
    fecha_pedido = primer_item.get("fecha")

    if not nombre or not direccion or not telefono:
        flash("Faltan datos del cliente.", "danger")
        return redirect(url_for("pizzas.index"))

    if not fecha_pedido:
        flash("Falta la fecha del pedido.", "danger")
        return redirect(url_for("pizzas.index"))

    try:
        cliente = Cliente(
            nombre=nombre,
            direccion=direccion,
            telefono=telefono
        )
        db.session.add(cliente)
        db.session.flush()

        total_pedido = sum(item["subtotal"] for item in detalle_pedido)

        fecha_convertida = datetime.strptime(fecha_pedido, "%Y-%m-%d").date()

        pedido = Pedido(
            id_cliente=cliente.id_cliente,
            fecha=fecha_convertida,
            total=total_pedido
        )
        db.session.add(pedido)
        db.session.flush()

        for item in detalle_pedido:
            pizza = Pizza(
                tamano=item["tamano"],
                ingredientes=item["ingredientes"],
                precio=item["precio_unitario"]
            )
            db.session.add(pizza)
            db.session.flush()

            detalle = DetallePedido(
                id_pedido=pedido.id_pedido,
                id_pizza=pizza.id_pizza,
                cantidad=item["cantidad"],
                subtotal=item["subtotal"]
            )
            db.session.add(detalle)

        db.session.commit()

        session["detalle_pedido"] = []
        session.modified = True

        flash("Pedido guardado correctamente.", "success")

    except Exception as e:
        db.session.rollback()
        flash(f"Error al guardar el pedido: {str(e)}", "danger")

    return redirect(url_for("pizzas.index"))


@pizzas.route("/historial")
def historial():
    buscar = request.args.get("buscar", "").strip()
    fecha_inicio = request.args.get("fecha_inicio", "").strip()
    fecha_fin = request.args.get("fecha_fin", "").strip()

    query = (
        db.session.query(Pedido, Cliente)
        .join(Cliente, Pedido.id_cliente == Cliente.id_cliente)
    )


    if buscar:
        query = query.filter(Cliente.nombre.ilike(f"%{buscar}%"))

    
    if fecha_inicio:
        fecha_inicio_obj = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        query = query.filter(Pedido.fecha >= fecha_inicio_obj)


    if fecha_fin:
        fecha_fin_obj = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        query = query.filter(Pedido.fecha <= fecha_fin_obj)

    pedidos = query.order_by(Pedido.id_pedido.desc()).all()

    return render_template(
        "Pizzas/historial.html",
        pedidos=pedidos,
        buscar=buscar,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )

@pizzas.route("/detalle_venta/<int:id_pedido>")
def detalle_venta(id_pedido):

    pedido = Pedido.query.get_or_404(id_pedido)
    cliente = Cliente.query.get(pedido.id_cliente)

    detalles = (
        db.session.query(DetallePedido, Pizza)
        .join(Pizza, DetallePedido.id_pizza == Pizza.id_pizza)
        .filter(DetallePedido.id_pedido == id_pedido)
        .all()
    )

    return render_template(
        "Pizzas/detalle_venta.html",
        pedido=pedido,
        cliente=cliente,
        detalles=detalles
    )