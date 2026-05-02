import os

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np

app = Flask(__name__)
CORS(app)

# ============================================================
# BANK DATABASE
# ============================================================

BANK_NAMES = [
    "State Bank of India (SBI)",
    "HDFC Bank",
    "ICICI Bank",
    "Axis Bank",
    "Kotak Mahindra Bank",
    "Yes Bank",
    "Bank of Baroda",
    "Punjab National Bank",
    "Canara Bank",
    "Union Bank of India",
    "Indian Bank",
    "IndusInd Bank",
    "IDFC First Bank",
    "Federal Bank",
    "RBL Bank"
]

# Interbank loans for PageRank calculation
INTERBANK_LOANS = [
    {"from": "State Bank of India (SBI)", "to": "HDFC Bank", "amount_cr": 25000},
    {"from": "State Bank of India (SBI)", "to": "ICICI Bank", "amount_cr": 20000},
    {"from": "State Bank of India (SBI)", "to": "Axis Bank", "amount_cr": 15000},
    {"from": "HDFC Bank", "to": "State Bank of India (SBI)", "amount_cr": 18000},
    {"from": "HDFC Bank", "to": "ICICI Bank", "amount_cr": 12000},
    {"from": "ICICI Bank", "to": "State Bank of India (SBI)", "amount_cr": 15000},
    {"from": "ICICI Bank", "to": "HDFC Bank", "amount_cr": 10000},
    {"from": "Axis Bank", "to": "HDFC Bank", "amount_cr": 12000},
    {"from": "Axis Bank", "to": "ICICI Bank", "amount_cr": 10000},
    {"from": "Yes Bank", "to": "State Bank of India (SBI)", "amount_cr": 5000},
    {"from": "Kotak Mahindra Bank", "to": "HDFC Bank", "amount_cr": 8000},
    {"from": "IndusInd Bank", "to": "ICICI Bank", "amount_cr": 6000}
]

# FD Rates (5 years)
FD_RATES = {
    "Yes Bank": 7.5,
    "RBL Bank": 7.4,
    "IDFC First Bank": 7.35,
    "IndusInd Bank": 7.3,
    "Kotak Mahindra Bank": 7.25,
    "Axis Bank": 7.2,
    "ICICI Bank": 7.15,
    "HDFC Bank": 7.1,
    "State Bank of India (SBI)": 7.05,
    "Bank of Baroda": 6.9,
    "Punjab National Bank": 6.9,
    "Canara Bank": 6.85,
    "Union Bank of India": 6.8,
    "Indian Bank": 6.7,
    "Federal Bank": 6.6
}

# RD Rates
RD_RATES = {
    "Yes Bank": 7.1,
    "RBL Bank": 7.0,
    "IDFC First Bank": 6.95,
    "IndusInd Bank": 6.9,
    "Kotak Mahindra Bank": 6.85,
    "Axis Bank": 6.8,
    "ICICI Bank": 6.75,
    "HDFC Bank": 6.7,
    "State Bank of India (SBI)": 6.65,
    "Bank of Baroda": 6.5,
    "Punjab National Bank": 6.5,
    "Canara Bank": 6.45,
    "Union Bank of India": 6.4,
    "Indian Bank": 6.3,
    "Federal Bank": 6.2
}

# Credit Cards
CREDIT_CARDS = {
    "HDFC Infinia": {
        "rewards": {"Food": 3.3, "Shopping": 3.3, "Travel": 3.3, "Fuel": 3.3, "Entertainment": 3.3},
        "min_cibil": 780, "annual_fee": 12500,
        "benefits": "Unlimited lounge, 10x rewards", "icon": "💎"
    },
    "Axis Magnus": {
        "rewards": {"Food": 3, "Shopping": 3, "Travel": 5, "Fuel": 3, "Entertainment": 3},
        "min_cibil": 780, "annual_fee": 10000,
        "benefits": "Premium travel benefits", "icon": "💎"
    },
    "ICICI Sapphiro": {
        "rewards": {"Food": 2, "Shopping": 2, "Travel": 3, "Fuel": 2, "Entertainment": 2},
        "min_cibil": 760, "annual_fee": 3500,
        "benefits": "Lounge access, Golf", "icon": "💳"
    },
    "HDFC Millennia": {
        "rewards": {"Food": 1, "Shopping": 5, "Travel": 1, "Fuel": 1, "Entertainment": 1},
        "min_cibil": 750, "annual_fee": 1000,
        "benefits": "5% cashback on shopping", "icon": "💳"
    },
    "SBI Cashback": {
        "rewards": {"Food": 1, "Shopping": 5, "Travel": 1, "Fuel": 1, "Entertainment": 1},
        "min_cibil": 720, "annual_fee": 1000,
        "benefits": "5% cashback on online", "icon": "💳"
    },
    "ICICI Amazon Pay": {
        "rewards": {"Food": 2, "Shopping": 5, "Travel": 2, "Fuel": 1, "Entertainment": 2},
        "min_cibil": 700, "annual_fee": 0,
        "benefits": "5% on Amazon", "icon": "💳"
    },
    "Axis Ace": {
        "rewards": {"Food": 2, "Shopping": 2, "Travel": 2, "Fuel": 4, "Entertainment": 2},
        "min_cibil": 720, "annual_fee": 500,
        "benefits": "4% cashback on fuel", "icon": "💳"
    },
    "IDFC First Select": {
        "rewards": {"Food": 3, "Shopping": 3, "Travel": 3, "Fuel": 3, "Entertainment": 3},
        "min_cibil": 740, "annual_fee": 0,
        "benefits": "Railway lounge", "icon": "💳"
    },
    "IndusInd Legend": {
        "rewards": {"Food": 2, "Shopping": 2, "Travel": 2, "Fuel": 2, "Entertainment": 2},
        "min_cibil": 720, "annual_fee": 0,
        "benefits": "Lifetime free", "icon": "💳"
    }
}


# ============================================================
# PAGE RANK POWER METHOD
# ============================================================

def compute_pagerank(alpha=0.85, tolerance=1e-8, max_iter=200):
    """PageRank Power Method Implementation"""
    n = len(BANK_NAMES)
    idx_map = {name: i for i, name in enumerate(BANK_NAMES)}
    
    # Calculate total outgoing loans
    out_total = {bank: 0 for bank in BANK_NAMES}
    for loan in INTERBANK_LOANS:
        out_total[loan["from"]] += loan["amount_cr"]
    
    # Build Matrix A (Column-Stochastic)
    A = np.zeros((n, n))
    for loan in INTERBANK_LOANS:
        from_idx = idx_map[loan["from"]]
        to_idx = idx_map[loan["to"]]
        if out_total[loan["from"]] > 0:
            A[to_idx][from_idx] += loan["amount_cr"] / out_total[loan["from"]]
    
    # Handle dangling nodes
    for j in range(n):
        if np.sum(A[:, j]) == 0:
            A[:, j] = 1.0 / n
    
    # Build Teleportation Matrix E
    E = np.ones((n, n)) / n
    
    # Build Google Matrix G = αA + (1-α)E
    G = alpha * A + (1 - alpha) * E
    
    # Power Method
    x = np.ones(n) / n
    convergence_history = []
    
    for iteration in range(max_iter):
        x_new = G @ x
        error = np.linalg.norm(x_new - x)
        convergence_history.append(float(error))
        
        if error < tolerance:
            break
        x = x_new
    
    # Prepare results
    scores = {BANK_NAMES[i]: float(x[i]) for i in range(n)}
    
    ranking = []
    for rank, (bank, score) in enumerate(sorted(scores.items(), key=lambda item: item[1], reverse=True), 1):
        if score > 0.30:
            risk_level = "HIGH"
            risk_color = "🔴"
        elif score > 0.15:
            risk_level = "MEDIUM"
            risk_color = "🟡"
        else:
            risk_level = "LOW"
            risk_color = "🟢"
        
        ranking.append({
            "rank": rank,
            "bank": bank,
            "health_score": round(score, 4),
            "risk_level": risk_level,
            "risk_color": risk_color
        })
    
    return {
        "scores": scores,
        "ranking": ranking,
        "iterations": iteration + 1,
        "convergence_history": convergence_history,
        "alpha": alpha
    }


def calculate_fd_returns(principal, rate, years):
    amount = principal * ((1 + rate / 100) ** years)
    interest = amount - principal
    return round(amount, 2), round(interest, 2)


def calculate_rd_returns(monthly_amount, rate, years):
    months = years * 12
    monthly_rate = rate / 12 / 100
    amount = monthly_amount * (((1 + monthly_rate) ** months - 1) / monthly_rate)
    total_invested = monthly_amount * months
    interest = amount - total_invested
    return round(amount, 2), round(interest, 2)


# ============================================================
# FLASK API ENDPOINTS
# ============================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "banks": len(BANK_NAMES)})


@app.route('/api/banks', methods=['GET'])
def get_banks():
    return jsonify({"success": True, "banks": [{"name": b} for b in BANK_NAMES], "total": len(BANK_NAMES)})


@app.route('/api/pagerank', methods=['GET'])
def get_pagerank():
    alpha = request.args.get('alpha', 0.85, type=float)
    result = compute_pagerank(alpha)
    return jsonify({"success": True, "result": result})


@app.route('/api/investment', methods=['POST'])
def get_investment():
    data = request.json
    principal = data.get('principal', 50000)
    monthly_sip = data.get('monthly_sip', 5000)
    tenure_years = data.get('tenure_years', 5)
    
    fd_recommendations = []
    rd_recommendations = []
    
    for bank in BANK_NAMES:
        fd_rate = FD_RATES.get(bank, 0)
        if fd_rate > 0:
            amount, interest = calculate_fd_returns(principal, fd_rate, tenure_years)
            fd_recommendations.append({
                "bank": bank,
                "rate": fd_rate,
                "maturity_amount": amount,
                "interest_earned": interest,
                "tenure": tenure_years
            })
        
        rd_rate = RD_RATES.get(bank, 0)
        if rd_rate > 0:
            amount, interest = calculate_rd_returns(monthly_sip, rd_rate, tenure_years)
            rd_recommendations.append({
                "bank": bank,
                "rate": rd_rate,
                "maturity_amount": amount,
                "interest_earned": interest,
                "total_invested": monthly_sip * tenure_years * 12,
                "tenure": tenure_years
            })
    
    fd_recommendations.sort(key=lambda x: x["rate"], reverse=True)
    rd_recommendations.sort(key=lambda x: x["rate"], reverse=True)
    
    return jsonify({
        "success": True,
        "fd_recommendations": fd_recommendations[:10],
        "rd_recommendations": rd_recommendations[:10],
        "principal": principal,
        "monthly_sip": monthly_sip,
        "tenure_years": tenure_years
    })


@app.route('/api/credit-cards', methods=['POST'])
def get_credit_cards():
    data = request.json
    cibil_score = data.get('cibil_score', 750)
    spending = data.get('spending', {
        "Food": 8000, "Shopping": 4000, "Travel": 2000, "Fuel": 1000, "Entertainment": 1000
    })
    
    recommendations = []
    for card_name, card_data in CREDIT_CARDS.items():
        min_cibil = card_data.get("min_cibil", 600)
        eligible = cibil_score >= min_cibil
        
        total_benefit = 0
        for category, amount in spending.items():
            reward_rate = card_data["rewards"].get(category, 1)
            total_benefit += amount * reward_rate / 100
        
        yearly_benefit = total_benefit * 12 - card_data.get("annual_fee", 0)
        
        recommendations.append({
            "card_name": card_name,
            "monthly_benefit": round(total_benefit, 2),
            "yearly_benefit": round(yearly_benefit, 2),
            "annual_fee": card_data.get("annual_fee", 0),
            "min_cibil": min_cibil,
            "eligible": eligible,
            "benefits": card_data.get("benefits", ""),
            "icon": card_data.get("icon", "💳")
        })
    
    recommendations.sort(key=lambda x: (x["eligible"], x["yearly_benefit"]), reverse=True)
    
    # CIBIL tips
    if cibil_score < 650:
        tips = ["Pay all bills on time", "Keep credit utilization below 30%"]
    elif cibil_score < 750:
        tips = ["Good score! Keep improving", "Maintain mix of credit types"]
    else:
        tips = ["Excellent! You qualify for premium cards", "Enjoy best rewards"]
    
    return jsonify({
        "success": True,
        "recommendations": recommendations,
        "cibil_score": cibil_score,
        "tips": tips
    })


@app.route('/api/expense-analyzer', methods=['POST'])
def analyze_expenses():
    data = request.json
    expenses = data.get('expenses', {
        "Food": 8000, "Rent": 15000, "Transport": 3000, "Shopping": 4000,
        "Entertainment": 2000, "Healthcare": 1000, "Utilities": 2000
    })
    
    total = sum(expenses.values())
    percentages = {}
    for category, amount in expenses.items():
        percentages[category] = round(amount / total, 3)
    
    sorted_expenses = sorted(percentages.items(), key=lambda x: x[1], reverse=True)
    top_expense = sorted_expenses[0][0]
    top_percent = sorted_expenses[0][1] * 100
    
    insights = [
        f"📊 {top_expense} is your CENTRAL expense ({top_percent:.0f}% of total)",
        f"💰 Reducing {top_expense} by 20% saves ₹{int(expenses[top_expense] * 0.2):,} per month",
        f"📈 Your total monthly expense is ₹{total:,}",
        f"💡 Track these expenses to save more"
    ]
    
    return jsonify({
        "success": True,
        "expenses": expenses,
        "total": total,
        "percentages": percentages,
        "top_expense": top_expense,
        "insights": insights
    })


if __name__ == '__main__':
    print("=" * 60)
    print("💰 FINMATRIX - Backend Server")
    print("=" * 60)
    print(f"📊 Loaded {len(BANK_NAMES)} banks")
    print(f"💳 Loaded {len(CREDIT_CARDS)} credit cards")
    print(f"🔗 Loaded {len(INTERBANK_LOANS)} interbank loans")
    print("=" * 60)
    print("🚀 Server running at: http://localhost:5000")
    print("📱 Open frontend/index.html in your browser")
    print("=" * 60)
    if __name__ == '__main__':
        port = int(os.environ.get('PORT', 5000))
        app.run(debug=False, host='0.0.0.0', port=port)