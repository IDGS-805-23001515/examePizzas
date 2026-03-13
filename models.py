from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class Cliente(db.Model):
    __tablename__ = "clientes"

    id_cliente = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(20))

    pedidos = db.relationship("Pedido", backref="cliente", lazy=True)


class Pizza(db.Model):
    __tablename__ = "pizza"

    id_pizza = db.Column(db.Integer, primary_key=True)
    tamano = db.Column(db.String(50), nullable=False)
    ingredientes = db.Column(db.String(255), nullable=False)
    precio = db.Column(db.Float, nullable=False)


class Pedido(db.Model):
    __tablename__ = "pedidos"

    id_pedido = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey("clientes.id_cliente"), nullable=False)
    fecha = db.Column(db.Date)
    total = db.Column(db.Numeric(10, 2))

    detalles = db.relationship("DetallePedido", backref="pedido", lazy=True)


class DetallePedido(db.Model):
    __tablename__ = "detalle_pedido"

    id_detalle = db.Column(db.Integer, primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey("pedidos.id_pedido"), nullable=False)
    id_pizza = db.Column(db.Integer, db.ForeignKey("pizza.id_pizza"), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

    pizza = db.relationship("Pizza", backref="detalles")