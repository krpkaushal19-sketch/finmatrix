import numpy as np

def compute_pagerank(bank_names, interbank_loans, alpha=0.85, tolerance=1e-8, max_iter=200):
    """
    PageRank Power Method Implementation
    Based on Linear Algebra Module 3: x⁽ᵏ⁺¹⁾ = G × x⁽ᵏ⁾
    """
    n = len(bank_names)
    idx_map = {name: i for i, name in enumerate(bank_names)}
    
    # Step 1: Build Matrix A (Column-Stochastic)
    out_total = {bank: 0 for bank in bank_names}
    for loan in interbank_loans:
        out_total[loan["from"]] += loan["amount_cr"]
    
    A = np.zeros((n, n))
    for loan in interbank_loans:
        from_idx = idx_map[loan["from"]]
        to_idx = idx_map[loan["to"]]
        if out_total[loan["from"]] > 0:
            A[to_idx][from_idx] += loan["amount_cr"] / out_total[loan["from"]]
    
    # Handle dangling nodes
    for j in range(n):
        if np.sum(A[:, j]) == 0:
            A[:, j] = 1.0 / n
    
    # Step 2: Build Teleportation Matrix E
    E = np.ones((n, n)) / n
    
    # Step 3: Build Google Matrix G = αA + (1-α)E
    G = alpha * A + (1 - alpha) * E
    
    # Step 4: Power Method
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
    scores = {bank_names[i]: float(x[i]) for i in range(n)}
    
    ranking = []
    for rank, (bank, score) in enumerate(sorted(scores.items(), key=lambda item: item[1], reverse=True), 1):
        # Realistic risk levels based on actual bank data
        if score > 0.35:
            risk_level = "HIGH"
            risk_color = "🔴"
        elif score > 0.20:
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
    """Calculate FD maturity amount"""
    amount = principal * ((1 + rate / 100) ** years)
    interest = amount - principal
    return round(amount, 2), round(interest, 2)


def calculate_rd_returns(monthly_amount, rate, years):
    """Calculate RD maturity amount"""
    months = years * 12
    monthly_rate = rate / 12 / 100
    amount = monthly_amount * (((1 + monthly_rate) ** months - 1) / monthly_rate)
    total_invested = monthly_amount * months
    interest = amount - total_invested
    return round(amount, 2), round(interest, 2)


def get_investment_recommendations(principal, monthly_sip, tenure_years):
    """Get FD and RD recommendations"""
    from bank_data import FD_RATES, RD_RATES, get_bank_names
    
    bank_names = get_bank_names()
    fd_recommendations = []
    rd_recommendations = []
    
    for bank in bank_names:
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
    
    return fd_recommendations[:10], rd_recommendations[:10]


def get_credit_card_recommendations(cibil_score, spending):
    """Get credit card recommendations based on CIBIL and spending"""
    from bank_data import CREDIT_CARDS
    
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
            "icon": card_data.get("icon", "💳"),
            "color": card_data.get("color", "#1A5F7A")
        })
    
    recommendations.sort(key=lambda x: (x["eligible"], x["yearly_benefit"]), reverse=True)
    return recommendations