from supabase import create_client
import uuid
import random

import os
from dotenv import load_dotenv 
SUPABASE_URL = os.getenv("SUPABASE_URL") 

SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# =====================================
# USERS
# =====================================

def create_user(
        email,
        full_name,
        phone,
        address,
        pan,
        password
):


    account_number = str(random.randint(100000000000,999999999999))

    user = {
        "id": str(uuid.uuid4()),
        "email": email,
        "full_name":full_name,
        "phone": phone,
        "address": address,
        "pan": pan,
        "password": password,
        "account_number": account_number,
        "balance": 10000,
        "status": "pending"
    }
    supabase.table(
        "users"
    ).insert(
        user
    ).execute()


def get_user_by_email(email):

    result = supabase.table(
        "users"
    ).select(
        "*"
    ).eq(
        "email",
        email
    ).execute()

    if len(result.data) == 0:
        return None

    return result.data[0]

def get_user_by_id(user_id):

    result = (
        supabase
        .table("users")
        .select("*")
        .eq("id", user_id)
        .execute()
    )

    if not result.data:
        return None

    return result.data[0]

def user_exists(email, phone, pan):

    email_check = (
        supabase
        .table("users")
        .select("*")
        .eq("email", email)
        .execute()
    )

    if email_check.data:
        return "Email already registered"

    phone_check = (
        supabase
        .table("users")
        .select("*")
        .eq("phone", phone)
        .execute()
    )

    if phone_check.data:
        return "Phone number already registered"

    pan_check = (
        supabase
        .table("users")
        .select("*")
        .eq("pan", pan)
        .execute()
    )

    if pan_check.data:
        return "PAN already registered"

    return None

def get_pending_users():

    result = supabase.table(
        "users"
    ).select(
        "*"
    ).eq(
        "status",
        "pending"
    ).execute()

    return result.data


def approve_user(user_id):

    supabase.table(
        "users"
    ).update(
        {
            "status": "approved"
        }
    ).eq(
        "id",
        user_id
    ).execute()


# =====================================
# TRANSACTIONS
# =====================================

def get_recent_transactions(user_id):

    result = supabase.table(
        "transactions"
    ).select(
        "*"
    ).eq(
        "sender_id",
        user_id
    ).limit(
        10
    ).execute()

    return result.data

def get_user_by_account_number(account_number):

    result = (
        supabase
        .table("users")
        .select("*")
        .eq("account_number", account_number)
        .execute()
    )

    if not result.data:
        return None

    return result.data[0]

# def add_funds(
#         account_number,
#         amount
# ):

#     user = get_user_by_account_number(
#         account_number
#     )

#     if not user:
#         return False

#     new_balance = (
#         float(user["balance"])
#         + float(amount)
#     )

#     (
#         supabase
#         .table("users")
#         .update({
#             "balance": new_balance
#         })
#         .eq(
#             "id",
#             user["id"]
#         )
#         .execute()
#     )

#     return True

def create_credit_transaction(
        user_id,
        amount
):

    (
        supabase
        .table("transactions")
        .insert({
            "id": str(uuid.uuid4()),
            "sender_id": user_id,
            "receiver_account": "BANK",
            "amount": amount,
            "type": "CREDIT",
            "remarks": "Admin Fund Credit"
        })
        .execute()
    )


def add_funds(
        account_number,
        amount
):

    user = get_user_by_account_number(
        account_number
    )

    if not user:
        return False

    new_balance = (
        float(user["balance"])
        + float(amount)
    )

    (
        supabase
        .table("users")
        .update({
            "balance": new_balance
        })
        .eq(
            "id",
            user["id"]
        )
        .execute()
    )

    create_credit_transaction(
        user["id"],
        amount
    )

    return True

def create_debit_transaction(
        user_id,
        receiver_account,
        amount,
        remarks
):

    (
        supabase
        .table("transactions")
        .insert({
            "id": str(uuid.uuid4()),
            "sender_id": user_id,
            "receiver_account": receiver_account,
            "amount": amount,
            "type": "DEBIT",
            "remarks": remarks
        })
        .execute()
    )


def transfer_money(
        sender_id,
        receiver_account,
        amount,
        remarks
):

    sender = get_user_by_id(
        sender_id
    )

    receiver = get_user_by_account_number(
        receiver_account
    )

    if not receiver:
        return "Account not found"

    if float(sender["balance"]) < float(amount):
        return "Insufficient balance"

    sender_new_balance = (
        float(sender["balance"])
        - float(amount)
    )

    receiver_new_balance = (
        float(receiver["balance"])
        + float(amount)
    )

    (
        supabase
        .table("users")
        .update({
            "balance": sender_new_balance
        })
        .eq(
            "id",
            sender["id"]
        )
        .execute()
    )

    (
        supabase
        .table("users")
        .update({
            "balance": receiver_new_balance
        })
        .eq(
            "id",
            receiver["id"]
        )
        .execute()
    )

    create_debit_transaction(
        sender["id"],
        receiver_account,
        amount,
        remarks
    )

    create_credit_transaction(
        receiver["id"],
        amount
    )

    return "success"

def request_card(
        user_id,
        card_type
):

    (
        supabase
        .table("cards")
        .insert({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "card_type": card_type,
            "status": "pending"
        })
        .execute()
    )

def get_user_cards(user_id):

    result = (
        supabase
        .table("cards")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    return result.data

def get_pending_cards():

    result = (
        supabase
        .table("cards")
        .select("*")
        .eq(
            "status",
            "pending"
        )
        .execute()
    )

    return result.data

def approve_card(
        card_id
):

    (
        supabase
        .table("cards")
        .update({
            "status": "approved"
        })
        .eq(
            "id",
            card_id
        )
        .execute()
    )


def get_user_loans(user_id):

    result = (
        supabase
        .table("loans")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )

    return result.data

def request_loan(
        user_id,
        amount,
        tenure_months
):

    (
        supabase
        .table("loans")
        .insert({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "amount": amount,
            "tenure_months": tenure_months,
            "status": "pending"
        })
        .execute()
    )

def get_pending_loans():

    result = (
        supabase
        .table("loans")
        .select("*")
        .eq(
            "status",
            "pending"
        )
        .execute()
    )

    return result.data

def approve_loan(
        loan_id
):

    (
        supabase
        .table("loans")
        .update({
            "status": "approved"
        })
        .eq(
            "id",
            loan_id
        )
        .execute()
    )