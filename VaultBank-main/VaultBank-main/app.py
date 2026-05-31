from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from dotenv import load_dotenv

load_dotenv()
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@bank.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
from database import (
    approve_card,
    create_user,
    get_pending_cards,
    get_user_by_email,
    get_recent_transactions,
    get_pending_users,
    approve_user,
    get_user_by_id,
    get_user_cards,
    request_card,
    transfer_money,
    user_exists,
    add_funds,
    get_user_loans,
    request_loan,
    get_pending_loans,
    approve_loan
    )

app = FastAPI(title="Neo Bank")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


# ==================================================
# LANDING PAGE
# ==================================================

@app.get("/", response_class=HTMLResponse)
async def landing(request: Request):

    user_id = request.cookies.get("user_id")

    logged_in = False

    if user_id:

        user = get_user_by_id(user_id)

        if user:
            logged_in = True

    return templates.TemplateResponse(
        request=request,
        name="vault-all-pages.html",
        context={
            "logged_in": logged_in
        }
    )

# ==================================================
# SIGNUP
# ==================================================

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):

    user_id = request.cookies.get("user_id")

    if user_id:

        user = get_user_by_id(user_id)

        if user:
            return RedirectResponse(
                url="/dashboard",
                status_code=303
            )

    return templates.TemplateResponse(
        request=request,
        name="signupi.html"
    )

@app.post("/signup")
async def signup(
        request: Request,
        f_name: str = Form(...),
        email: str = Form(...),
        phone: str = Form(...),
        address: str = Form(...),
        pan: str = Form(...),
        password: str = Form(...)
):

    existing = user_exists(
        email=email,
        phone=phone,
        pan=pan
    )

    if existing:

        return templates.TemplateResponse(
            request=request,
            name="signupi.html",
            context={
                "error": existing
            }
        )

    create_user(
        full_name=f_name,
        email=email,
        phone=phone,
        address=address,
        pan=pan,
        password=password
    )

    return RedirectResponse(
        url="/login",
        status_code=303
    )

# ==================================================
# LOGIN
# ==================================================

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):

    user_id = request.cookies.get("user_id")

    if user_id:

        user = get_user_by_id(user_id)

        if user:
            return RedirectResponse(
                url="/dashboard",
                status_code=303
            )

    return templates.TemplateResponse(
        request=request,
        name="logini.html"
    )


@app.post("/login")
async def login(
        request: Request,
        email: str = Form(...),
        password: str = Form(...)
):

    user = get_user_by_email(email)

    if not user:

        return templates.TemplateResponse(
            request=request,
            name="logini.html",
            context={
                "error": "User not found"
            }
        )

    if user["password"] != password:

        return templates.TemplateResponse(
            request=request,
            name="logini.html",
            context={
                "error": "Incorrect password"
            }
        )

    if user["status"] != "approved":

        return templates.TemplateResponse(
            request=request,
            name="logini.html",
            context={
                "error": "Account pending approval-Please Transfer Funds"
            }
        )

    response = RedirectResponse(
        url="/dashboard",
        status_code=303
    )

    response.set_cookie(
        key="user_id",
        value=user["id"],
        httponly=True
    )

    return response

# ==================================================
# DASHBOARD
# ==================================================
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):

    user_id = request.cookies.get("user_id")

    if not user_id:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    user = get_user_by_id(user_id)

    if not user:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    txns = get_recent_transactions(
        user["id"]
    )

    return templates.TemplateResponse(
        request=request,
        name="dashboardi.html",
        context={
            "user": user,
            "transactions": txns
        }
    )
@app.get("/logout")
async def logout():

    response = RedirectResponse(
        url="/",
        status_code=303
    )

    response.delete_cookie(
        "user_id"
    )

    return response
# ==================================================
# ADMIN LOGIN
# ==================================================

@app.get("/admin", response_class=HTMLResponse)
async def admin_login_page(request: Request):

    return templates.TemplateResponse(
        "admin_logini.html",
        {"request": request}
    )


@app.post("/admin")
async def admin_login(request: Request,email: str = Form(...),password: str = Form(...)):
    if email != ADMIN_EMAIL:

        return templates.TemplateResponse(
            request=request,
            name="admin_logini.html",
            context={
                "error": "Unauthorized email"
            }
        )

    if password != ADMIN_PASSWORD:

        return templates.TemplateResponse(
            request=request,
            name="admin_logini.html",
            context={
                "error": "Incorrect password"
            }
        )

    response = RedirectResponse(
        url="/admin/dashboard",
        status_code=303
    )

    response.set_cookie(
        key="admin",
        value="true",
        httponly=True
    )

    return response




# ==================================================
# ADMIN DASHBOARD
# ==================================================

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):

    pending_users = get_pending_users()
    pending_cards=get_pending_cards()
    pending_loan = get_pending_loans()

    return templates.TemplateResponse(
        "admin_dashboardi.html",
        {
            "request": request,
            "pending_users": pending_users,
            "pending_cards": pending_cards,
            "pending_loans" : pending_loan
        }
    )


@app.post("/approve-user")
async def approve_pending_user(
        user_id: str = Form(...)
):

    approve_user(user_id)

    return RedirectResponse(
        url="/admin/dashboard",
        status_code=303
    )

@app.post("/admin/add-funds")
async def admin_add_funds(
        account_number: str = Form(...),
        amount: float = Form(...)
):

    add_funds(
        account_number,
        amount
    )

    return RedirectResponse(
        url="/admin/dashboard",
        status_code=303
    )

@app.get("/send-money",
         response_class=HTMLResponse)
async def send_money_page(
        request: Request
):

    return templates.TemplateResponse(
        request=request,
        name="send_moneyi.html"
    )

@app.post("/send-money")
async def send_money(

        request: Request,

        account_number: str = Form(...),

        amount: float = Form(...),

        remarks: str = Form(...)
):

    user_id = request.cookies.get(
        "user_id"
    )

    result = transfer_money(
        user_id,
        account_number,
        amount,
        remarks
    )

    if result != "success":

        return templates.TemplateResponse(
            request=request,
            name="send_moneyi.html",
            context={
                "error": result
            }
        )

    return RedirectResponse(
        "/dashboard",
        status_code=303
    )

@app.post("/request-card")
async def request_card_route(
        request: Request,
        card_type: str = Form(...)
):

    user_id = request.cookies.get(
        "user_id"
    )

    request_card(
        user_id,
        card_type
    )

    return RedirectResponse(
        "/dashboard",
        status_code=303
    )

@app.get("/cards",
         response_class=HTMLResponse)
async def cards_page(
        request: Request
):

    user_id = request.cookies.get(
        "user_id"
    )

    if not user_id:
        return RedirectResponse(
            "/login",
            status_code=303
        )

    cards = get_user_cards(
        user_id
    )

    return templates.TemplateResponse(
        request=request,
        name="cardsi.html",
        context={
            "cards": cards
        }
    )

@app.post("/approve-card")
async def approve_card_route(
        card_id: str = Form(...)
):

    approve_card(
        card_id
    )

    return RedirectResponse(
        "/admin/dashboard",
        status_code=303
    )

@app.get("/loans",
         response_class=HTMLResponse)
async def loans_page(
        request: Request
):

    user_id = request.cookies.get(
        "user_id"
    )

    loans = get_user_loans(
        user_id
    )

    return templates.TemplateResponse(
        request=request,
        name="loansi.html",
        context={
            "loans": loans
        }
    )

@app.get("/loans",
         response_class=HTMLResponse)
async def loans_page(
        request: Request
):

    user_id = request.cookies.get(
        "user_id"
    )

    loans = get_user_loans(
        user_id
    )

    return templates.TemplateResponse(
        request=request,
        name="loansi.html",
        context={
            "loans": loans
        }
    )

@app.post("/request-loan")
async def request_loan_route(
        request: Request,

        amount: float = Form(...),

        tenure_months: int = Form(...)
):

    user_id = request.cookies.get(
        "user_id"
    )

    request_loan(
        user_id,
        amount,
        tenure_months
    )

    return RedirectResponse(
        "/loans",
        status_code=303
    )

@app.post("/approve-loan")
async def approve_loan_route(
        loan_id: str = Form(...)
):

    approve_loan(
        loan_id
    )

    return RedirectResponse(
        "/admin/dashboard",
        status_code=303
    )