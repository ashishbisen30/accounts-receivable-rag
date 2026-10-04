import os
from datetime import date, timedelta
from sqlalchemy import (
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# -----------------------------------------------------------------------------
# 1. Database Setup (Creates finance.db file locally)
# -----------------------------------------------------------------------------
DB_FILE = "data/finance.db"
os.makedirs("data", exist_ok=True)

ENGINE = create_engine(f"sqlite:///{DB_FILE}", echo=False)
Base = declarative_base()


# -----------------------------------------------------------------------------
# 2. Define Models (Customers, Invoices, Payments)
# -----------------------------------------------------------------------------
class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    credit_limit = Column(Float, nullable=False)
    payment_terms = Column(String(20), default="Net 30")

    invoices = relationship(
        "Invoice", back_populates="customer", cascade="all, delete-orphan"
    )


class Invoice(Base):
    __tablename__ = "invoices"

    invoice_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    amount = Column(Float, nullable=False)
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(String(20), default="Unpaid")  # Paid, Unpaid, Partially Paid

    customer = relationship("Customer", back_populates="invoices")
    payments = relationship(
        "Payment", back_populates="invoice", cascade="all, delete-orphan"
    )


class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("invoices.invoice_id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(Date, nullable=False)

    invoice = relationship("Invoice", back_populates="payments")


# -----------------------------------------------------------------------------
# 3. Create Tables & Seed Data
# -----------------------------------------------------------------------------
def init_db():
    Base.metadata.create_all(ENGINE)
    Session = sessionmaker(bind=ENGINE)
    session = Session()

    # Prevent duplicate seeding
    if session.query(Customer).count() > 0:
        print("Database already populated!")
        session.close()
        return

    # Seed 10 Customers
    customers = [
        Customer(
            customer_id=101 + i,
            name=f"Client {chr(65+i)} Corp",
            email=f"billing@client{chr(97+i)}.com",
            credit_limit=10000.0 + (i * 2000),
            payment_terms="Net 30",
        )
        for i in range(10)
    ]
    session.add_all(customers)
    session.commit()

    # Seed 20 Invoices
    today = date.today()
    invoices = [
        Invoice(
            invoice_id=1001 + i,
            customer_id=101 + (i % 10),
            amount=1500.0 + (i * 350.0),
            issue_date=today - timedelta(days=60 - (i * 2)),
            due_date=today - timedelta(days=30 - (i * 2)),
            status="Paid" if i < 8 else ("Partially Paid" if i < 11 else "Unpaid"),
        )
        for i in range(20)
    ]
    session.add_all(invoices)
    session.commit()

    # Seed 15 Payments
    payments = []
    for i in range(15):
        inv = invoices[i % 11]  # Connect to paid or partially paid invoices
        payment_amount = inv.amount if inv.status == "Paid" else inv.amount / 2
        payments.append(
            Payment(
                payment_id=5001 + i,
                invoice_id=inv.invoice_id,
                amount=round(payment_amount, 2),
                payment_date=inv.issue_date + timedelta(days=10),
            )
        )
    session.add_all(payments)
    session.commit()

    print(
        f"Database successfully initialized at '{DB_FILE}' with 10 Customers, 20 Invoices, and 15 Payments!"
    )
    session.close()


if __name__ == "__main__":
    init_db()