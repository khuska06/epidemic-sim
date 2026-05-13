import json
import os
import sys

try:
    import matplotlib

    # gui shaardahgui backend ashiglana
    matplotlib.use("Agg")

    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches

    HAS_MPL = True

except ImportError:

    # matplotlib baihgui bol zurag zurah hesgiig alгasna
    HAS_MPL = False


COLORS = {

    # scenario buriig oor ongoor haruulah dictionary
    "Baseline": "#2563EB",
    "High-Contact": "#DC2626",
    "Fast-Recovery": "#16A34A",
    "Intervention": "#D97706",
}


def load_timeline(name):

    # scenario neriig file-n helber ruu huvirgaj baina
    fname = f"outputs/{name.lower().replace('-','_')}_timeline.json"

    with open(fname, encoding="utf-8") as f:

        # json data-g python object bolgon unshina
        return json.load(f)


def plot_sir_curves(scenario_names):

    if not HAS_MPL:
        print(" matplotlib oldsongui baina")
        return

    # 2x2 subplot uusgej scenario buriig tusad ni haruulna
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))

    fig.suptitle(
        "SIR Тахлын Дуурайлт — Нөхцөл Тус Бүрийн Муруй",
        fontsize=15,
        fontweight="bold",
        y=1.01
    )

    # axis bolon scenario-iig zereg ashiglana
    for ax, name in zip(axes.flat, scenario_names):

        tl = load_timeline(name)

        # odor buriin utguudiig list comprehension-aar salgaj avna
        days = [r["day"] for r in tl]

        S_arr = [r["S"] for r in tl]
        I_arr = [r["I"] for r in tl]
        R_arr = [r["R"] for r in tl]

        # S murui -> haldvar avah bolomjtoi humuus
        ax.plot(
            days,
            S_arr,
            color="#6366F1",
            lw=2,
            label="S (мэдрэмтгий)"
        )

        # I murui -> odoogiin haldvartai humuus
        ax.plot(
            days,
            I_arr,
            color="#EF4444",
            lw=2.5,
            label="I (халдвартай)"
        )

        # R murui -> edgesen humuus
        ax.plot(
            days,
            R_arr,
            color="#22C55E",
            lw=2,
            label="R (эдгэрсэн)"
        )

        ax.set_title(
            name,
            fontsize=12,
            color=COLORS.get(name, "#111")
        )

        ax.set_xlabel("Өдөр", fontsize=9)
        ax.set_ylabel("Хүний тоо", fontsize=9)

        # legend ni mur bolgon юуг ilerhiilj baigaag haruulna
        ax.legend(fontsize=8)

        # graph unshihad hyalbar bolgoh grid
        ax.grid(True, alpha=0.3)

        # y axis deerh too-g comma-tei haruulah formatting
        ax.yaxis.set_major_formatter(
            plt.FuncFormatter(
                lambda x, _: f"{int(x):,}"
            )
        )

    # subplot hoorondiin зайг automataar taaruulna
    plt.tight_layout()

    out = "outputs/sir_curves.png"

    plt.savefig(
        out,
        dpi=150,
        bbox_inches="tight"
    )

    # memory tseverleh zorilgotoi close hiij baina
    plt.close()

    print(f" -> {out} hadgalagdlaa")


def plot_peak_comparison(summary):

    if not HAS_MPL:
        return

    # scenario-uudiin neriig avna
    names = list(summary["scenarios"].keys())

    # scenario buriin peak haldvariin utga
    peaks = [
        summary["scenarios"][n]["peak_infected"]
        for n in names
    ]

    # scenario buriin ongo
    colors = [
        COLORS.get(n, "#888")
        for n in names
    ]

    fig, ax = plt.subplots(figsize=(9, 5))

    # baganan diagram uusgene
    bars = ax.bar(
        names,
        peaks,
        color=colors,
        width=0.55,
        edgecolor="white",
        linewidth=1.5
    )

    # bar buriin deer toon utga haruulna
    for bar, val in zip(bars, peaks):

        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 60,
            f"{val:,}",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold"
        )

    ax.set_title(
        "Нөхцөл Бүрийн Оргил Халдвартнуудын Тоо",
        fontsize=13,
        fontweight="bold"
    )

    ax.set_ylabel(
        "Хамгийн их халдвартнуудын тоо",
        fontsize=10
    )

    ax.set_xlabel(
        "Нөхцөл",
        fontsize=10
    )

    # y axis deerh too-g comma-tei bolgono
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(
            lambda x, _: f"{int(x):,}"
        )
    )

    # zovhon y axis-iin grid haruulna
    ax.grid(axis="y", alpha=0.3)

    plt.tight_layout()

    out = "outputs/peak_comparison.png"

    plt.savefig(
        out,
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

    print(f" -> {out} hadgalagdlaa")


def print_table(summary):

    print()

    print("┌─────────────────┬──────┬────────────┬────────────────┬──────────────┐")
    print("│ Нөхцөл          │  R0  │ Оргил өдөр │ Оргил халдвар  │ Нийт халдвар │")
    print("├─────────────────┼──────┼────────────┼────────────────┼──────────────┤")

    for name, v in summary["scenarios"].items():

        # f-string ashiglaad table helbereer hevlej baina
        print(
            f"│ {name:<15s}  │ {v['r0']:4.2f} │    {v['peak_day']:>4}-р өдөр │   "
            f"{v['peak_infected']:>9,}  │  {v['total_infected']:>9,}   │"
        )

    print("└─────────────────┴──────┴────────────┴────────────────┴──────────────┘")


if __name__ == "__main__":

    print("=" * 60)
    print(" Graph Module - SIR Simulation")
    print("=" * 60)

    with open("outputs/summary.json", encoding="utf-8") as f:

        # simulate.py-s uusgesen summary file-iig unshij baina
        summary = json.load(f)

    names = list(summary["scenarios"].keys())

    print("SIR murui zurj baina...\n")

    plot_sir_curves(names)

    print("Peak haritsuulsan graph zurj baina...\n")

    plot_peak_comparison(summary)

    print_table(summary)

    print("\nDuuslaa. outputs folderoos harna uu.")
