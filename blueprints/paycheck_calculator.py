from flask import Blueprint, request, render_template, make_response
import requests, tomlkit


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


@pay_calc_bp.route("/paycheck-calculator/")
@pay_calc_bp.route("/paycheck-calculator/<username>")
def paycheck_calculator(username="guest"):
    with open("config.toml", "r") as file_handle:
        toml_config = tomlkit.load(file_handle)
    if username not in toml_config:
        toml_config.update(
            {
                username: {
                    "base_payrate": 0.0,
                    "shiftdiff_payrate": 0.0,
                    "benefit_cost": 0.0,
                    "base_hours": 0.0,
                    "shiftdiff_hours": 0.0,
                    "overtime_hours": 0.0,
                }
            }
        )
    toml_config = toml_config[username]
    return render_template("main.html", username=username, tconfig=toml_config)


@pay_calc_bp.route("/api/paycheck-calculator/", methods=["POST"])
def api_paycheck_calculator():
    if request.method != "POST" or not request.is_json:
        response = make_response({"error": True, "message": "Incorrect usage of api."})
        response.status_code = 422
        return response

    url = "https://calculators.symmetry.com/api/calculators/salary"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Pcc-Api-Key": "102qqx5AOgcpLhIxbX9LcPBuvmdjefA6h39Nbce57gMcsT",
    }

    BASE_PAYRATE = float(request.json.get("base_payrate"))
    SHIFT_DIFF_PAYRATE = float(request.json.get("shiftdiff_payrate"))
    OVERTIME_PAYRATE = BASE_PAYRATE * 1.5

    BASE_HOURS = float(request.json.get("base_hours"))
    SHIFT_DIFF_HOURS = float(request.json.get("shiftdiff_hours"))
    OVERTIME_HOURS = float(request.json.get("overtime_hours"))

    BENEFITS_COST = float(request.json.get("benefit_cost"))

    payrates = [
        {"payRate": str(BASE_PAYRATE), "hours": str(BASE_HOURS)},
        {"payRate": str(SHIFT_DIFF_PAYRATE), "hours": str(SHIFT_DIFF_HOURS)},
        {"payRate": str(OVERTIME_PAYRATE), "hours": str(OVERTIME_HOURS)},
    ]

    req_handler = PayrateMath(BASE_PAYRATE, SHIFT_DIFF_PAYRATE, OVERTIME_PAYRATE)
    gross_pay_str = req_handler.get_gross_pay_str(payrates)

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

    with open("config.toml", "r") as file_handle:
        toml_config = tomlkit.load(file_handle)

    toml_config.update(
        {
            request.json.get("username"): {
                "base_payrate": BASE_PAYRATE,
                "shiftdiff_payrate": SHIFT_DIFF_PAYRATE,
                "benefit_cost": BENEFITS_COST,
                "base_hours": BASE_HOURS,
                "shiftdiff_hours": SHIFT_DIFF_HOURS,
                "overtime_hours": OVERTIME_HOURS,
                "last_netpay": float(response.json().get("content").get("netPay")),
            }
        }
    )

    with open("config.toml", "w") as file_handle:
        tomlkit.dump(toml_config, file_handle)

    return response.json().get("content")
