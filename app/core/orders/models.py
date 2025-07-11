from decimal import Decimal
from app.core.orders.constants import OrderStatusEnum
from app.infra.postgres.base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import BIGINT, INTEGER, ENUM, TEXT, FLOAT
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    name: Mapped[str] = mapped_column(TEXT, unique=True)
    price: Mapped[Decimal] = mapped_column(FLOAT, nullable=False)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    user_id: Mapped[int] = mapped_column(BIGINT, nullable=False)
    status: Mapped[OrderStatusEnum] = mapped_column(
        ENUM(*[str(member) for member in OrderStatusEnum], name="order_status")
    )
    products: Mapped[list["OrderedProduct"]] = relationship()


class OrderedProduct(Base):
    __tablename__ = "orders_products"

    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), primary_key=True)
    amount: Mapped[int] = mapped_column(INTEGER, nullable=False)

    product: Mapped[Product] = relationship()


