from flask import Blueprint, request, render_template, make_response, current_app
from flask_login import login_required
import requests

from models import User, db


class PayrateMath:
    def __init__(self, base_payrate, shift_diff_payrate, overtime_payrate):
        self.base_payrate = base_payrate
        self.shift_diff_payrate = shift_diff_payrate
        self.overtime_ratio = overtime_payrate

    def get_gross_pay_str(self, payrates: list) -> str:
        gross_pay = 0.0

        for rate in payrates:
            gross_pay += float(rate["payRate"]) * float(rate["hours"])

        return f"{gross_pay:.2f}"


pay_calc_bp = Blueprint("PaycheckCalculator", __name__)
pay_calc_api_bp = Blueprint("PaycheckCalculatorAPI", __name__)


@pay_calc_bp.get("/paycheck-calculator")
@login_required
def paycheck_calculator():
    return render_template("old-paycheck-calculator.html")


@pay_calc_api_bp.post("/api/paycheck-calculator")
def api_paycheck_calculator():

    url = "https://calculators.symmetry.com/api/calculators/salary"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Pcc-Api-Key": current_app.config["PAYCHECK_CALC_API_KEY"],
    }

    USER_ID = request.json.get("user_id")

    BASE_PAYRATE = float(request.json.get("base_payrate"))
    SHIFT_DIFF_PAYRATE = float(request.json.get("shiftdiff_payrate"))
    OVERTIME_PAYRATE = BASE_PAYRATE * 1.5

    BASE_HOURS = float(request.json.get("base_hours"))
    SHIFT_DIFF_HOURS = float(request.json.get("shiftdiff_hours"))
    OVERTIME_HOURS = float(request.json.get("overtime_hours"))

    BENEFITS_COST = float(request.json.get("benefit_cost"))
    RETIREMENT_COST = float(request.json.get("retirement_cost"))

    payrates = [
        {"payRate": str(BASE_PAYRATE), "hours": str(BASE_HOURS)},
        {"payRate": str(SHIFT_DIFF_PAYRATE), "hours": str(SHIFT_DIFF_HOURS)},
        {"payRate": str(OVERTIME_PAYRATE), "hours": str(OVERTIME_HOURS)},
    ]

    req_handler = PayrateMath(BASE_PAYRATE, SHIFT_DIFF_PAYRATE, OVERTIME_PAYRATE)
    gross_pay_str = req_handler.get_gross_pay_str(payrates)

    user = User.query.filter_by(id=USER_ID).first()

    if user != None:
        user.base_payrate = BASE_PAYRATE
        user.shift_diff_payrate = SHIFT_DIFF_PAYRATE
        user.benefits_cost = BENEFITS_COST
        user.retirement_cost = RETIREMENT_COST
        db.session.commit()

    RETIREMENT_DOLLARS = float(gross_pay_str) * RETIREMENT_COST / 100
    BENEFITS_COST += RETIREMENT_DOLLARS

    payload = {
        "grossPay": gross_pay_str,
        "grossPayType": "PAY_PER_PERIOD",
        "grossPayYTD": "0",
        "payFrequency": "BI_WEEKLY",
        "w42020": True,
        "federalFilingStatusType2020": "SINGLE",
        "federalFilingStatusType": "SINGLE",
        "federalAllowances": "0",
        "twoJobs2020": "false",
        "dependents2020": "0",
        "otherIncome2020": "0",
        "deductions2020": "0",
        "additionalFederalWithholding": "0",
        "roundFederalWithholding": "false",
        "exemptFederal": "false",
        "exemptFica": "false",
        "exemptMedicare": "false",
        "checkDate": 1737149475000,
        "rates": payrates,
        "state": "PA",
        "stateInfo": {
            "parms": [
                {"name": "stateExemption", "value": False},
                {"name": "additionalStateWithholding", "value": "0"},
                {"name": "MOST_RECENT_WH", "value": "0.0"},
                {"name": "42-000-0000-SUI-000", "value": True},
                {"name": "PA_WAGES_ONLY", "value": "TRUE"},
            ],
            "local": {
                "address1": "270 Midway Road",
                "address2": "",
                "city": "Bethel",
                "zip": "19507",
                "zip4": "",
                "resident": False,
                "exempt": False,
            },
        },
        "voluntaryDeductions": [
            {
                "deductionName": "Benefits",
                "deductionAmount": str(BENEFITS_COST),
                "deductionMethodType": "FIXED_AMOUNT",
                "exemptFederal": False,
                "exemptFica": False,
                "exemptState": False,
                "exemptLocal": False,
                "benefitType": "_Custom",
                "ytdAmount": 0,
            }
        ],
    }

    response = requests.post(url, headers=headers, json=payload)

    return response.json().get("content")
