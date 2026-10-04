import sys
from financial_metrics import Session, generate_followup_list, get_customer_outstanding_summary
from rag import generate_rag_answer


def display_menu():
    """Displays the main terminal menu options."""
    print("\n" + "=" * 60)
    print("      ACCOUNTS RECEIVABLE (AR) AI ASSISTANT")
    print("=" * 60)
    print("1. Ask a Finance/AR Policy Question (Vector RAG)")
    print("2. View Customers Requiring Payment Follow-Up (SQL)")
    print("3. Check Customer Account Balance (SQL)")
    print("4. Exit")
    print("=" * 60)


def handle_policy_query():
    """Handles natural language questions using ChromaDB + LLM RAG pipeline."""
    query = input("\nEnter your policy question: ").strip()
    if not query:
        print("Question cannot be empty.")
        return

    print("\n[Retrieving policy context & generating response...]")
    try:
        result = generate_rag_answer(query)

        print("\n" + "-" * 50)
        print("ANSWER:")
        print(result["answer"])
        print("\nSUPPORTING SOURCES:")
        for src in result["sources"]:
            print(f" - Document: {src['source']} | Section: {src['title']}")
        print("-" * 50)
    except Exception as e:
        print(f"\nError retrieving answer: {e}")


def handle_followup_list():
    """Retrieves and displays high-priority overdue accounts from the database."""
    session = Session()
    print("\n[Fetching overdue accounts from financial database...]")
    followups = generate_followup_list(session)
    session.close()

    print("\n" + "-" * 60)
    print(f"FOUND {len(followups)} CUSTOMER(S) REQUIRING PAYMENT FOLLOW-UP:\n")
    if not followups:
        print("No overdue accounts requiring follow-up.")
    else:
        for cust in followups:
            print(
                f"• {cust['name']} | Overdue: ${cust['total_overdue']} | "
                f"Overdue Invoices: {cust['overdue_invoice_count']} | Email: {cust['email']}"
            )
    print("-" * 60)


def handle_customer_balance():
    """Searches for a specific customer and displays their account metrics."""
    session = Session()
    summaries = get_customer_outstanding_summary(session)
    session.close()

    search_term = input("\nEnter customer name to search (e.g., 'Client A'): ").strip().lower()
    if not search_term:
        print("Search term cannot be empty.")
        return

    matches = [c for c in summaries if search_term in c["name"].lower()]

    print("\n" + "-" * 50)
    if not matches:
        print(f"No customers found matching '{search_term}'.")
    else:
        for c in matches:
            print(f"Customer Name     : {c['name']} (ID: {c['customer_id']})")
            print(f"Email             : {c['email']}")
            print(f"Credit Limit      : ${c['credit_limit']}")
            print(f"Total Outstanding : ${c['total_outstanding']}")
            print(f"Total Overdue     : ${c['total_overdue']}")
            print(f"Overdue Invoices  : {c['overdue_invoice_count']}")
            print("-" * 50)


def main():
    """Main application loop."""
    while True:
        display_menu()
        choice = input("Select an option (1-4): ").strip()

        if choice == "1":
            handle_policy_query()
        elif choice == "2":
            handle_followup_list()
        elif choice == "3":
            handle_customer_balance()
        elif choice == "4":
            print("\nExiting Accounts Receivable Assistant. Goodbye!")
            sys.exit(0)
        else:
            print("\nInvalid option. Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()