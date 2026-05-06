import numpy as np                              # тоон тооцоолол хийх сан
import json                                     # JSON файл бичих/унших сан
import os                                       # файлын системтэй ажиллах сан
from datetime import datetime                   # огноо, цаг авах сан

POPULATION   = 10_000                           # нийт хүн амын тоо
INFECTED_0   = 5                                # эхний халдвартай хүний тоо
BETA         = 0.30                             # халдварын дамжих хурд (нэг өдөрт)
GAMMA        = 0.07                             # эдгэрэх хурд (нэг өдөрт)
DAYS         = 200                              # симуляц хэдэн хоног явуулах
RANDOM_SEED  = 42                               # дахин давтагдах үр дүнгийн тулд санамсаргүй үр

np.random.seed(RANDOM_SEED)                     # санамсаргүй тоог тогтмол болгоно

def run_sir(pop, i0, beta, gamma, days):        # SIR загварын үндсэн функц
    S = float(pop - i0)                         # мэдрэмтгий (Susceptible) хүний анхны тоо
    I = float(i0)                               # халдвартай (Infected) хүний анхны тоо
    R = 0.0                                     # эдгэрсэн (Recovered) хүний анхны тоо

    records = []                                # бүх өдрийн мэдээллийг хадгалах жагсаалт

    for day in range(days):                     # бүх өдрийг давтана
        new_infected = beta * S * I / pop       # шинэ халдвартнуудын тоо (масс-үйлдлийн хуулиар)
        new_infected += np.random.normal(0, new_infected * 0.05 + 0.1)  # бодит байдлыг дуурайсан дуу чимээ
        new_infected  = max(0.0, new_infected)  # сөрөг тоо гарахаас сэргийлнэ

        new_recovered = gamma * I               # шинэ эдгэрсэн хүмүүсийн тоо

        S = max(0.0, S - new_infected)          # мэдрэмтгий хүн буурна
        I = max(0.0, I + new_infected - new_recovered)  # халдвартнуудын тоо өөрчлөгдөнө
        R = min(float(pop), R + new_recovered)  # эдгэрсэн хүний тоо нэмэгдэнэ

        records.append({                        # өдрийн мэдээллийг объект болгон хадгална
            "day":       day + 1,               # өдрийн дугаар (1-ээс эхлэнэ)
            "S":         round(S),              # мэдрэмтгий хүний тоо
            "I":         round(I),              # халдвартай хүний тоо
            "R":         round(R),              # эдгэрсэн хүний тоо
            "prevalence": round(I / pop * 100, 4)  # халдварын давамгайлал хувиар
        })

    return records                              # бүх өдрийн жагсаалтыг буцаана

def peak_info(records):                         # оргил өдрийг олох функц
    peak = max(records, key=lambda r: r["I"])   # хамгийн их I утгатай өдрийг хайна
    return peak["day"], peak["I"]               # оргил өдөр болон тоог буцаана

def compute_r0(beta, gamma):                    # үндсэн репродукцийн тоог тооцоолох функц
    return round(beta / gamma, 4)               # R0 = β / γ томьёо

def run_scenarios():                            # олон нөхцөл байдлын симуляц функц
    scenarios = [                               # туршилтын нөхцөлүүдийн жагсаалт
        {"name": "Baseline",       "beta": 0.30, "gamma": 0.07},  # ердийн нөхцөл
        {"name": "High-Contact",   "beta": 0.50, "gamma": 0.07},  # их харилцаатай нөхцөл
        {"name": "Fast-Recovery",  "beta": 0.30, "gamma": 0.15},  # хурдан эдгэрэх нөхцөл
        {"name": "Intervention",   "beta": 0.12, "gamma": 0.07},  # хөл хорионы нөхцөл
    ]

    all_results = {}                            # бүх нөхцлийн үр дүнг хадгалах толь бичиг

    for sc in scenarios:                        # бүр нөхцөлийг давтана
        records  = run_sir(POPULATION, INFECTED_0, sc["beta"], sc["gamma"], DAYS)
        pk_day, pk_I = peak_info(records)       # оргил мэдээллийг олно
        r0       = compute_r0(sc["beta"], sc["gamma"])  # R0 тооцооно
        total_infected = records[-1]["R"]       # нийт халдвар авсан хүний тоо (эцсийн R)

        all_results[sc["name"]] = {             # нөхцлийн бүрэн мэдээллийг хадгална
            "params":          sc,              # нөхцлийн параметрүүд
            "r0":              r0,              # үндсэн репродукцийн тоо
            "peak_day":        pk_day,          # оргил өдөр
            "peak_infected":   round(pk_I),     # оргил дахь халдвартнуудын тоо
            "total_infected":  round(total_infected),  # нийт халдвар авсан хүний тоо
            "attack_rate_pct": round(total_infected / POPULATION * 100, 2),  # довтолгооны хурд хувиар
            "timeline":        records,         # бүх өдрийн цувааны мэдээлэл
        }
        print(f"  [{sc['name']:15s}]  R0={r0:.2f}  оргил={pk_day}-р өдөр  "
              f"нийт халдвар авсан={round(total_infected):,}")  # үр дүнг хэвлэнэ

    return all_results                          # бүх нөхцлийн үр дүнг буцаана

def save_outputs(all_results):                  # үр дүнг файл болгон хадгалах функц
    os.makedirs("outputs", exist_ok=True)       # outputs хавтасыг үүсгэнэ (байхгүй бол)

    slim = {}                                   # хялбарчилсан хураангуй толь бичиг
    for name, v in all_results.items():         # бүр нөхцлийг давтана
        slim[name] = {k: val for k, val in v.items() if k != "timeline"}  # timeline-г хасна

    with open("outputs/summary.json", "w", encoding="utf-8") as f:  # хураангуй JSON файл нэнэнэ
        json.dump({"meta": {                    # мета мэдээлэл бичнэ
            "population":   POPULATION,         # хүн амын тоо
            "infected_0":   INFECTED_0,         # анхны халдвартнуудын тоо
            "days":         DAYS,               # симуляц хоногийн тоо
            "generated_at": datetime.now().isoformat()  # үүсгэсэн огноо
        }, "scenarios": slim}, f, indent=2, ensure_ascii=False)  # JSON файлд хадгална

    for name, v in all_results.items():         # бүр нөхцлийн цувааг тусад нь хадгална
        fname = f"outputs/{name.lower().replace('-','_')}_timeline.json"
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(v["timeline"], f)         # цувааны мэдээллийг бичнэ
        print(f"  → {fname} хадгалагдлаа")     # хаана хадгалагдсаныг мэдэгдэнэ

if __name__ == "__main__":                      # скриптийг шууд ажиллуулах үед
    print("═" * 60)                             # хэвлэх хязгаарын шугам
    print("   SIR Тахлын Дуурайлт — Монгол Өвчний Загвар")  # гарчиг
    print("═" * 60)
    print(f"   Хүн ам: {POPULATION:,}  |  Анхны халдвар: {INFECTED_0}  |  Хоног: {DAYS}")
    print()
    print("▸ Нөхцөл бүрийг тооцооллож байна ...")
    results = run_scenarios()                   # симуляцийг ажиллуулна
    print()
    print("▸ Файлуудыг хадгалж байна ...")
    save_outputs(results)                       # үр дүнг файл болгон хадгална
    print()
    print("✓ Дуусав! outputs/ хавтасыг шалгана уу.")  # дуусгавар мэдэгдэл
    print("═" * 60)
