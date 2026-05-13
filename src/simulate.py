import numpy as np
import json
import os
from datetime import datetime

POPULATION = 10000
INFECTED_0 = 5
BETA = 0.30
GAMMA = 0.07
DAYS = 200
RANDOM_SEED = 42

np.random.seed(RANDOM_SEED)

def run_sir(pop, i0, beta, gamma, days):

    # ehnii utguud
    S = float(pop - i0)
    I = float(i0)
    R = 0.0

    timeline = []

    for day in range(days):

        # SIR tomyo ashiglaj shine haldvar toolno
        new_infected = beta * S * I / pop

        # joohon random noise nemj iluu realistic bolgov
        new_infected += np.random.normal(0, new_infected * 0.05 + 0.1)

        # surug utga garahaas sergiilne
        new_infected = max(0.0, new_infected)

        # edgesen humuusiin too
        new_recovered = gamma * I

        # population update
        S = max(0.0, S - new_infected)
        I = max(0.0, I + new_infected - new_recovered)
        R = min(float(pop), R + new_recovered)

        timeline.append({
            "day": day + 1,
            "S": round(S),
            "I": round(I),
            "R": round(R),
            "prevalence": round(I / pop * 100, 4)
        })

    return timeline


def peak_info(timeline):

    # hamgiin ih haldvar garsan odriig olno
    peak = max(timeline, key=lambda r: r["I"])

    return peak["day"], peak["I"]


def compute_r0(beta, gamma):

    # R0 = beta / gamma
    return round(beta / gamma, 4)


def run_scenarios():

    turshiltuud = [
        {"name": "Baseline", "beta": 0.30, "gamma": 0.07},
        {"name": "High-Contact", "beta": 0.50, "gamma": 0.07},
        {"name": "Fast-Recovery", "beta": 0.30, "gamma": 0.15},
        {"name": "Intervention", "beta": 0.12, "gamma": 0.07},
    ]

    all_results = {}

    for sc in turshiltuud:

        # scenario buriig ajilluulna
        timeline = run_sir(
            POPULATION,
            INFECTED_0,
            sc["beta"],
            sc["gamma"],
            DAYS
        )

        pk_day, pk_I = peak_info(timeline)

        r0 = compute_r0(sc["beta"], sc["gamma"])

        # suuliin R utgiig niit haldvar avsna gej uzne
        total_infected = timeline[-1]["R"]

        all_results[sc["name"]] = {
            "params": sc,
            "r0": r0,
            "peak_day": pk_day,
            "peak_infected": round(pk_I),
            "total_infected": round(total_infected),
            "attack_rate_pct": round(total_infected / POPULATION * 100, 2),
            "timeline": timeline,
        }

        print(
            f" [{sc['name']:15s}] "
            f"R0={r0:.2f} "
            f"orgil={pk_day}-r odor "
            f"niit haldvar={round(total_infected):,}"
        )

    return all_results


def save_outputs(all_results):

    os.makedirs("outputs", exist_ok=True)

    slim = {}

    for name, v in all_results.items():

        # timeline hesgiig summary-s hasav
        slim[name] = {
            k: val for k, val in v.items()
            if k != "timeline"
        }

    with open("outputs/summary.json", "w", encoding="utf-8") as f:

        json.dump({
            "meta": {
                "population": POPULATION,
                "infected_0": INFECTED_0,
                "days": DAYS,
                "generated_at": datetime.now().isoformat()
            },
            "scenarios": slim
        }, f, indent=2, ensure_ascii=False)

    for name, v in all_results.items():

        fname=f"outputs/{name.lower().replace('-','_')}_timeline.json"

        with open(fname, "w", encoding="utf-8") as f:
            json.dump(v["timeline"], f)

        print(f" -> {fname} hadgalagdlaa")


if __name__=="__main__":

    print("=" * 60)
    print(" SIR uvchinii simulation")
    print("=" * 60)

    print(
        f" hun am: {POPULATION:,} | "
        f"ehnii haldvar: {INFECTED_0} | "
        f"honog: {DAYS}"
    )
    print("\nscenario-uud toolj baina...\n")
    results= run_scenarios()
    print("\nfile-uud hadgalj baina...\n")
    save_outputs(results)
    print("\nduuslaa. outputs folderoos harna uu.")
