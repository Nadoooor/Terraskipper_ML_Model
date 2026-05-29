"""SHAP-based explainability wrapper for AI model."""

import shap
import numpy as np
from typing import Any


def explain_prediction(model: Any, X_test: np.ndarray, 
                       feature_names: list, max_samples: int = 200) -> None:
    """Generate SHAP summary plot for model explainability."""
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test[:max_samples])
    shap.summary_plot(shap_values, X_test[:max_samples],
                      feature_names=feature_names, show=False)
