"""
Generate fANOVA importance plots for an Optuna study.

This script generates horizontal or vertical bar charts from Optuna studies,
reading importances from an excels  file written with `evaluate_optuna_study.py`.
"""

import argparse
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# Default pretty name mapping for parameters (LaTeX-friendly)
DEFAULT_PRETTY_NAMES = {
    "lambda_g2": r"$\lambda_{\text{s/g}}$",
    "lambda_geary": r"$\lambda_{\text{geary}}$",
    "lambda_getis_ord": r"$\lambda_{\text{getis\_ord}}$",
    "lambda_moran": r"$\lambda_{\text{moran}}$",
    "lambda_r": r"$\lambda_{\text{entropy}}$",
    "lambda_d": r"$\lambda_{\text{KL}}$",
    "lambda_neighborhood_g1": r"$\lambda_{G}$",
    "lambda_l1": r"$\lambda_{\text{L1}}$",
    "lambda_l2": r"$\lambda_{\text{L2}}$",
    "lambda_ct_islands": r"$\lambda_{\text{CT}}$",
}


def plot_fanova(
    importances: dict,
    savepath: str,
    figsize: tuple = (7, 4),
    style: str | None = None,
) -> None:
    """Plot fANOVA importances as horizontal or vertical bar chart.
    
    Args:
        importances: Dict mapping parameter names to importance values
        savepath: Path to save figure
        pretty_names: Optional dict mapping param names to pretty display names
        figsize: Figure size tuple
        style: Plot horizontal ('horz') or vertical ('vert') bars
    """
    pretty_names = DEFAULT_PRETTY_NAMES

    labels = list(importances.keys())
    values = np.array([importances[k] for k in labels])

    # Sort descending
    idx = np.argsort(values)[::-1]
    labels = [labels[i] for i in idx]
    values = values[idx]
    labels_pretty = [pretty_names.get(k, k) for k in labels]

    fig, ax = plt.subplots(figsize=figsize)

    if style == "horz":
        bars = ax.barh(labels_pretty, values, color="steelblue")
        ax.invert_yaxis()
        ax.set_xlabel("fANOVA importance")
    else:
        bars = ax.bar(labels_pretty, values, color="steelblue")
        ax.set_ylabel("fANOVA importance")

    xmax = max(values) if len(values) > 0 else 1

    if style == "horz":
        ax.set_xlim(0, xmax * 1.20)
    else:
        ax.set_ylim(0, xmax * 1.20)

    for bar, val in zip(bars, values):
        label = "<0.01" if val < 0.01 else f"{val:.3f}"

        if style == "horz":
            x = bar.get_width()
            y = bar.get_y() + bar.get_height() / 2
            ax.text(min(x + xmax * 0.02, xmax * 1.18), y, label,
                    va="center", ha="left", fontsize=8)
        else:
            x = bar.get_x() + bar.get_width() / 2
            y = bar.get_height()
            ax.text(x, min(y + xmax * 0.02, xmax * 1.18), label,
                    va="bottom", ha="center", fontsize=8)

    fig.tight_layout()
    fig.savefig(savepath, dpi=300, bbox_inches="tight")
    plt.close(fig)


def load_importances_from_excel(
    excel_path: str,
) -> dict:
    """Load parameter importances from Excel file.
    
    Args:
        excel_path: Path to Excel file with importances (row: FANOVA, cols: parameters)
        
    Returns:
        Dict mapping parameter names to importance values
    """
    df = pd.read_excel(excel_path, index_col=0)

    # Extract FANOVA row
    if "FANOVA" in df.index:
        fanova_row = df.loc["FANOVA"]
        return fanova_row.to_dict()
    else:
        raise ValueError(f"No FANOVA row found in {excel_path}")


def main(argv=None):
    """Generate fANOVA plots for an Optuna study."""
    p = argparse.ArgumentParser(
        description="Generate fANOVA importance plots for a study."
    )
    p.add_argument(
        'importance_folder',
        help="Path to folder containing parameter importances csv"
    )
    p.add_argument(
        '--study-name',
        default='tangram_optuna_study',
        help='Name of optuna study (default tangram_optuna_study)'
    )
    p.add_argument(
        '--file-name',
        default='tangram_optuna_study_param_importance.xlsx',
        help='Importances excel file name (default study_name_param_importance.xlsx)'
    )
    p.add_argument(
        '--output-dir',
        default=None,
        help='Output directory (default: importance_folder)'
    )
    p.add_argument(
        '--style',
        default="horz",
        help="Bar style (either 'horz' or 'vert')"
    )

    args = p.parse_args(argv)

    importance_folder = os.path.abspath(args.importance_folder)
    output_dir = os.path.abspath(args.output_dir) if args.output_dir else importance_folder

    os.makedirs(output_dir, exist_ok=True)

    excel_path = os.path.join(importance_folder, args.file_name)
    fanova_importances = load_importances_from_excel(excel_path)

    # Generate plot
    h_path = os.path.join(output_dir, f"fanova.png")
    plot_fanova(
        fanova_importances,
        h_path,
        style=args.style,
    )
    print(f"[INFO] Saved plot to: {h_path}")


if __name__ == '__main__':
    main()
