import json                                     # JSON файл унших сан
import os                                       # хавтасуудтай ажиллах сан
import sys                                      # командын аргументуудыг унших сан

try:                                            # matplotlib байгаа эсэхийг шалгана
    import matplotlib                           # зураг зурах сан
    matplotlib.use("Agg")                       # дэлгэцгүй горим (серверт зориулсан)
    import matplotlib.pyplot as plt             # зурах интерфейс
    import matplotlib.patches as mpatches       # тайлбарын тэмдэглэгээ
    HAS_MPL = True                              # matplotlib байна
except ImportError:                             # matplotlib суулгаагүй бол
    HAS_MPL = False                             # тэмдэглэнэ

COLORS = {                                      # нөхцөл тус бүрийн өнгийн толь бичиг
    "Baseline":      "#2563EB",                 # цэнхэр — ердийн нөхцөл
    "High-Contact":  "#DC2626",                 # улаан — их харилцаатай нөхцөл
    "Fast-Recovery": "#16A34A",                 # ногоон — хурдан эдгэрэлт
    "Intervention":  "#D97706",                 # шар — хөл хорио
}

def load_timeline(name):                        # нөхцлийн цувааны JSON-ийг уншдаг функц
    fname = f"outputs/{name.lower().replace('-','_')}_timeline.json"
    with open(fname, encoding="utf-8") as f:    # файлыг нэнэнэ
        return json.load(f)                     # жагсаалтыг буцаана

def plot_sir_curves(scenario_names):            # SIR муруйг зурдаг функц
    if not HAS_MPL:                             # matplotlib байхгүй бол
        print("  ⚠ matplotlib суулгаагүй — зураг зурахгүй. pip install matplotlib")
        return                                  # функцаас гарна
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))  # 2×2 дэд зургийн тор
    fig.suptitle("SIR Тахлын Дуурайлт — Нөхцөл Тус Бүрийн Муруй",
                 fontsize=15, fontweight="bold", y=1.01)  # ерөнхий гарчиг

    for ax, name in zip(axes.flat, scenario_names):  # нөхцөл тус бүр дэд зурагтай
        tl    = load_timeline(name)             # өдрийн цувааг уншина
        days  = [r["day"] for r in tl]         # өдрүүдийн жагсаалт
        S_arr = [r["S"]   for r in tl]         # мэдрэмтгий хүний тоо
        I_arr = [r["I"]   for r in tl]         # халдвартай хүний тоо
        R_arr = [r["R"]   for r in tl]         # эдгэрсэн хүний тоо

        ax.plot(days, S_arr, color="#6366F1", lw=2, label="S (мэдрэмтгий)")  # S муруй
        ax.plot(days, I_arr, color="#EF4444", lw=2.5, label="I (халдвартай)")  # I муруй
        ax.plot(days, R_arr, color="#22C55E", lw=2, label="R (эдгэрсэн)")    # R муруй
        ax.set_title(name, fontsize=12, color=COLORS.get(name, "#111"))       # дэд гарчиг
        ax.set_xlabel("Өдөр", fontsize=9)       # x тэнхлэгийн шошго
        ax.set_ylabel("Хүний тоо", fontsize=9)  # y тэнхлэгийн шошго
        ax.legend(fontsize=8)                   # тайлбар
        ax.grid(True, alpha=0.3)                # торлосон шугам (тунгалаг)
        ax.yaxis.set_major_formatter(           # y тэнхлэгийг мянгаар форматлана
            plt.FuncFormatter(lambda x, _: f"{int(x):,}"))

    plt.tight_layout()                          # зургийн хоорондын зайг тохируулна
    out = "outputs/sir_curves.png"              # гаралтын файлын нэр
    plt.savefig(out, dpi=150, bbox_inches="tight")  # PNG болгон хадгална
    plt.close()                                 # санах ойг чөлөөлнэ
    print(f"  → {out} хадгалагдлаа")           # мэдэгдэнэ

def plot_peak_comparison(summary):              # оргил утгуудыг харьцуулах баганан диаграм
    if not HAS_MPL:                             # matplotlib байхгүй бол гарна
        return
    names  = list(summary["scenarios"].keys())  # нөхцлийн нэрсийн жагсаалт
    peaks  = [summary["scenarios"][n]["peak_infected"] for n in names]  # оргил тоо
    colors = [COLORS.get(n, "#888") for n in names]  # нөхцлийн өнгө

    fig, ax = plt.subplots(figsize=(9, 5))      # нэг зургийн бүтэц
    bars = ax.bar(names, peaks, color=colors, width=0.55, edgecolor="white", linewidth=1.5)  # баганан диаграм
    for bar, val in zip(bars, peaks):           # бар бүрт тоон шошго нэмнэ
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 60,
                f"{val:,}", ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.set_title("Нөхцөл Бүрийн Оргил Халдвартнуудын Тоо", fontsize=13, fontweight="bold")
    ax.set_ylabel("Хамгийн их халдвартнуудын тоо", fontsize=10)  # y тэнхлэгийн шошго
    ax.set_xlabel("Нөхцөл", fontsize=10)        # x тэнхлэгийн шошго
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.grid(axis="y", alpha=0.3)                # зөвхөн хэвтээ торлосон шугам
    plt.tight_layout()                          # зайг тохируулна
    out = "outputs/peak_comparison.png"         # гаралтын файлын нэр
    plt.savefig(out, dpi=150, bbox_inches="tight")  # хадгална
    plt.close()                                 # санах ойг чөлөөлнэ
    print(f"  → {out} хадгалагдлаа")

def print_table(summary):                       # консол дээр хураангуй хүснэгт хэвлэх функц
    print()
    print("┌─────────────────┬──────┬────────────┬────────────────┬──────────────┐")
    print("│ Нөхцөл          │  R0  │ Оргил өдөр │ Оргил халдвар  │ Нийт халдвар │")
    print("├─────────────────┼──────┼────────────┼────────────────┼──────────────┤")
    for name, v in summary["scenarios"].items():  # нөхцөл бүрийн мөр
        print(f"│ {name:<15s}  │ {v['r0']:4.2f} │    {v['peak_day']:>4}-р өдөр │   "
              f"{v['peak_infected']:>9,}  │  {v['total_infected']:>9,}   │")
    print("└─────────────────┴──────┴────────────┴────────────────┴──────────────┘")

if __name__ == "__main__":                      # шууд ажиллуулах үед
    print("═" * 60)
    print("   Графикийн Модуль — SIR Симуляцийн Дүрслэл")
    print("═" * 60)

    with open("outputs/summary.json", encoding="utf-8") as f:  # хураангуй JSON-ийг уншина
        summary = json.load(f)

    names = list(summary["scenarios"].keys())   # нөхцлийн нэрс

    print("▸ SIR муруйнуудыг зурж байна ...")
    plot_sir_curves(names)                      # SIR муруйн зургийг үүсгэнэ

    print("▸ Оргил харьцуулах диаграм зурж байна ...")
    plot_peak_comparison(summary)               # оргил харьцуулах диаграм үүсгэнэ

    print_table(summary)                        # консол хүснэгтийг хэвлэнэ

    print()
    print("✓ Зурахуй дууслаа! outputs/ хавтасаас харна уу.")
    print("═" * 60)
