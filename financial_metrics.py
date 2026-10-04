from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import database models created in Task 1
from create_db import Customer, Invoice, Payment

# -----------------------------------------------------------------------------
# Database Connection Setup
# -----------------------------------------------------------------------------
DB_FILE = "data/finance.db"
ENGINE = create_engine(f"sqlite:///{DB_FILE}", echo=False)
Session = sessionmaker(bind=ENGINE)


# -----------------------------------------------------------------------------
# 1. Invoice Level Calculations
# -----------------------------------------------------------------------------
def get_invoice_financial_summary(session, target_date=None):
    """
    Calculates outstanding balance and overdue status for every invoice.
    
    Args:
        session: SQLAlchemy session object.
        target_date: The reference date for calculating overdue days (defaults to today).
        
    Returns:
        List of dictionaries containing detailed financial metrics per invoice.
    """
    if target_date is None:
        target_date = date.today()

    invoices = session.query(Invoice).all()
    invoice_summary = []

    for inv in invoices:
        # Calculate total payments received for this invoice
        total_paid = sum(p.amount for p in inv.payments)

        # Outstanding balance = Total invoice amount - Payments received
        outstanding_balance = round(inv.amount - total_paid, 2)

        # An invoice is overdue if the balance is > 0 and the current date is past the due date
        days_overdue = 0
        is_overdue = False

        if outstanding_balance > 0 and target_date > inv.due_date:
            is_overdue = True
            days_overdue = (target_date - inv.due_date).days

        invoice_summary.append({
            "invoice_id": inv.invoice_id,
            "customer_id": inv.customer_id,
            "total_amount": inv.amount,
            "total_paid": total_paid,
            "outstanding_balance": outstanding_balance,
            "due_date": inv.due_date,
            "status": inv.status,
            "is_overdue": is_overdue,
            "days_overdue": days_overdue
        })

    return invoice_summary


# -----------------------------------------------------------------------------
# 2. Customer Level Aggregations
# -----------------------------------------------------------------------------
def get_customer_outstanding_summary(session, target_date=None):
    """
    Aggregates total outstanding amounts and overdue metrics for each customer.
    
    Returns:
        List of dictionaries containing summary financial metrics per customer.
    """
    invoice_data = get_invoice_financial_summary(session, target_date)
    customers = session.query(Customer).all()
    customer_summary = []

    for cust in customers:
        # Filter all invoices belonging to this specific customer
        cust_invoices = [i for i in invoice_data if i["customer_id"] == cust.customer_id]

        # Calculate total outstanding and overdue balances across all invoices
        total_outstanding = round(sum(i["outstanding_balance"] for i in cust_invoices), 2)
        total_overdue = round(sum(i["outstanding_balance"] for i in cust_invoices if i["is_overdue"]), 2)
        
        # Count total overdue invoices
        overdue_invoice_count = sum(1 for i in cust_invoices if i["is_overdue"])

        customer_summary.append({
            "customer_id": cust.customer_id,
            "name": cust.name,
            "email": cust.email,
            "credit_limit": cust.credit_limit,
            "total_outstanding": total_outstanding,
            "total_overdue": total_overdue,
            "overdue_invoice_count": overdue_invoice_count
        })

    return customer_summary


# -----------------------------------------------------------------------------
# 3. Customer Follow-up List Generator
# -----------------------------------------------------------------------------
def generate_followup_list(session, target_date=None):
    """
    Identifies customers requiring urgent payment follow-ups based on 
    active overdue invoices.
    
    Returns:
        List of customers needing follow-up, along with their overdue details.
    """
    cust_summaries = get_customer_outstanding_summary(session, target_date)
    
    # Filter customers who have at least one overdue invoice with a non-zero balance
    followup_list = [
        cust for cust in cust_summaries 
        if cust["overdue_invoice_count"] > 0 and cust["total_overdue"] > 0
    ]

    # Sort high-priority customers by highest overdue amount first
    followup_list = sorted(followup_list, key=lambda x: x["total_overdue"], reverse=True)
    
    return followup_list


# -----------------------------------------------------------------------------
# Verification Output Execution
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    session = Session()

    print("=" * 60)
    print("TASK 2: FINANCIAL CALCULATIONS SUMMARY")
    print("=" * 60)

    # 1. Display sample invoice calculations
    print("\n--- [1] Sample Overdue Invoices ---")
    invoices = get_invoice_financial_summary(session)
    overdue_invoices = [i for i in invoices if i["is_overdue"]]
    for inv in overdue_invoices[:3]:
        print(f"Invoice ID: {inv['invoice_id']} | Customer ID: {inv['customer_id']} | "
              f"Balance: ${inv['outstanding_balance']} | Days Overdue: {inv['days_overdue']} days")

    # 2. Display customer follow-up list
    print("\n--- [2] Customers Requiring Payment Follow-Up ---")
    followups = generate_followup_list(session)
    for cust in followups:
        print(f"Customer: {cust['name']} ({cust['email']}) | "
              f"Total Overdue: ${cust['total_overdue']} | Overdue Invoices: {cust['overdue_invoice_count']}")

    session.close()