"""Evaluate Optuna study and save plots.

This script evaluates an Optuna study from disk and generates standardized plots:
  - Parameter importance plots (FANOVA, MDI, PedANOVA)
  - Optimization history
  - Intermediate values
  - Empirical distribution function
  - Timeline

Data flows from storage → evaluation → disk (never held in memory).
"""

import argparse
import os
import sys
from typing import Tuple
import matplotlib.pyplot as plt
import pandas as pd
import optuna
import optuna.visualization.matplotlib as ovm
from optuna.importance import (
    FanovaImportanceEvaluator,
    MeanDecreaseImpurityImportanceEvaluator,
    PedAnovaImportanceEvaluator,
)


class CleanTimelineStudy:
    """Wrapper for Optuna study that filters out incomplete trials.
    
    Keeps all trials except:
      - RUNNING (should not appear in completed studies)
      - missing datetime_complete (aborted / killed / incomplete)
    """
    
    def __init__(self, study):
        # Keep all trials except the broken ones
        self._trials = [
            t for t in study.get_trials(deepcopy=False)
            if t.datetime_complete is not None
        ]

    @property
    def trials(self):
        return self._trials

    def get_trials(self, deepcopy=True, states=None):
        trials = self._trials
        if states is not None:
            trials = [t for t in trials if t.state in states]
        return trials

    # Minimal required attributes
    @property
    def directions(self):
        return None

    @property
    def study_name(self):
        return "cleaned_timeline"

    @property
    def user_attrs(self):
        return {}

    @property
    def system_attrs(self):
        return {}


def compute_and_plot_importances(
    study: optuna.Study,
    ped_baseline_quantile: float = 0.1,
) -> Tuple[pd.DataFrame, Tuple]:
    """Compute importances and generate corresponding matplotlib figures.
    
    Args:
        study: Optuna study object
        ped_baseline_quantile: Baseline quantile for PedANOVA
        
    Returns:
        DataFrame with importances
        Tuple of (fig_fanova, fig_mdi, fig_ped) matplotlib figures
    """
    # Create evaluators
    eval_fanova = FanovaImportanceEvaluator()
    eval_mdi = MeanDecreaseImpurityImportanceEvaluator()
    eval_ped = PedAnovaImportanceEvaluator(baseline_quantile=ped_baseline_quantile)

    # Compute importances
    imp_fanova = optuna.importance.get_param_importances(study, evaluator=eval_fanova)
    imp_mdi = optuna.importance.get_param_importances(study, evaluator=eval_mdi)
    imp_ped = optuna.importance.get_param_importances(study, evaluator=eval_ped)

    # Merge all param names
    all_params = sorted(set(imp_fanova) | set(imp_mdi) | set(imp_ped))

    # Build dataframe
    df = pd.DataFrame(index=["FANOVA", "MDI", "PED_ANOVA"], columns=all_params)
    for p in all_params:
        df.loc["FANOVA", p] = imp_fanova.get(p, float("nan"))
        df.loc["MDI", p] = imp_mdi.get(p, float("nan"))
        df.loc["PED_ANOVA", p] = imp_ped.get(p, float("nan"))

    # Generate figures with the corresponding evaluator
    fig_fanova = ovm.plot_param_importances(study, evaluator=eval_fanova)
    fig_mdi = ovm.plot_param_importances(study, evaluator=eval_mdi)
    fig_ped = ovm.plot_param_importances(study, evaluator=eval_ped)

    return df, (fig_fanova, fig_mdi, fig_ped)



def validate_study_folder(study_folder: str, study_name: str = "tangram_optuna_study") -> str:
    """Validate that study folder contains the Optuna database file.
    
    Args:
        study_folder: Path to folder containing Optuna DB
        study_name: Optuna study name (used to construct DB filename)
        
    Returns:
        Absolute path to database file
        
    Raises:
        FileNotFoundError if DB file not found
    """
    db_name = f"{study_name}.db"
    db_path = os.path.join(study_folder, db_name)

    if not os.path.exists(db_path):
        raise FileNotFoundError(
            f"Study folder {study_folder} missing expected file: {db_name}"
        )

    return os.path.abspath(db_path)


def main(argv=None):
    """Evaluate Optuna study and save plots to storage."""
    p = argparse.ArgumentParser(
        description="Evaluate Optuna study and save standardized plots."
    )
    p.add_argument(
        'study_folder',
        help="Path to folder containing the Optuna DB file"
    )
    p.add_argument(
        '--study-name',
        default='tangram_optuna_study',
        help='Optuna study name (default: tangram_optuna_study)'
    )
    p.add_argument(
        '--output-dir',
        default=None,
        help='Output directory for plots (default: study_folder/evaluation)'
    )

    args = p.parse_args(argv)

    # Normalize paths
    study_folder = os.path.abspath(args.study_folder)
    study_name = args.study_name

    if not os.path.isdir(study_folder):
        print(f"[ERROR] Study folder not found: {study_folder}")
        sys.exit(1)

    # Validate DB exists
    try:
        db_path = validate_study_folder(study_folder, study_name)
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    # Output directory
    if args.output_dir:
        output_dir = os.path.abspath(args.output_dir)
    else:
        output_dir = os.path.join(f"{study_folder}/evaluation/")

    os.makedirs(output_dir, exist_ok=True)

    print(f"[INFO] Loading Optuna study from: {db_path}")
    print(f"[INFO] Output directory: {output_dir}/evaluation")

    # Load study from storage
    storage = f"sqlite:///{db_path}"
    study = optuna.load_study(study_name=study_name, storage=storage)

    print(f"[INFO] Study has {len(study.trials)} trials")

    # 1. Compute and plot importances
    print("[INFO] Computing parameter importances...")
    df, figs = compute_and_plot_importances(study)

    # Save importance dataframe to Excel
    importance_xlsx = os.path.join(output_dir, f"{study_name}_param_importance.xlsx")
    df.to_excel(importance_xlsx)
    print(f"[INFO] Saved importance dataframe to: {importance_xlsx}")

    # Save individual importance plots
    for label, ax in zip(["anova", "mdi", "ped"], figs):
        fig = ax.figure
        fig_path = os.path.join(output_dir, f"{study_name}_param_importance_{label}.png")
        fig.savefig(fig_path, dpi=200, bbox_inches="tight")
        plt.close(fig)
        print(f"[INFO] Saved {label} importance plot to: {fig_path}")

    # 2. Optimization history
    print("[INFO] Generating optimization history plot...")
    hist_ax = ovm.plot_optimization_history(study)
    hist_fig = hist_ax.figure
    hist_path = os.path.join(output_dir, f"{study_name}_history.png")
    hist_fig.savefig(hist_path, dpi=200, bbox_inches="tight")
    plt.close(hist_fig)
    print(f"[INFO] Saved history plot to: {hist_path}")

    # 3. Intermediate values
    print("[INFO] Generating intermediate values plot...")
    inter_ax = ovm.plot_intermediate_values(study)
    if inter_ax.get_legend():
        inter_ax.get_legend().remove()
    inter_fig = inter_ax.figure
    inter_path = os.path.join(output_dir, f"{study_name}_intermediate_values.png")
    inter_fig.savefig(inter_path, dpi=200, bbox_inches="tight")
    plt.close(inter_fig)
    print(f"[INFO] Saved intermediate values plot to: {inter_path}")

    # 4. Timeline
    print("[INFO] Generating timeline plot...")
    time_ax = ovm.plot_timeline(study)
    time_fig = time_ax.figure
    time_path = os.path.join(output_dir, f"{study_name}_timeline.png")
    time_fig.savefig(time_path, dpi=200, bbox_inches="tight")
    plt.close(time_fig)
    print(f"[INFO] Saved timeline plot to: {time_path}")

    # 5. Empirical distribution function (EDF)
    print("[INFO] Generating EDF plot...")
    edf_ax = ovm.plot_edf(study)
    edf_fig = edf_ax.figure
    edf_path = os.path.join(output_dir, f"{study_name}_edf.png")
    edf_fig.savefig(edf_path, dpi=200, bbox_inches="tight")
    plt.close(edf_fig)
    print(f"[INFO] Saved EDF plot to: {edf_path}")

    print(f"[INFO] All plots saved to: {output_dir}")


if __name__ == '__main__':
    main()
