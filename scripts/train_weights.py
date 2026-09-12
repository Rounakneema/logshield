import pandas as pd
import json
import os
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc

def train_optimal_weights(dataset_path: str, output_weights_path: str):
    print(f"Loading dataset from {dataset_path}...")
    df = pd.read_csv(dataset_path)
    
    features = [
        "varname_score", "regex_score", "entropy_score", 
        "token_struct_score", "context_score", "encoding_score"
    ]
    
    X = df[features].fillna(0)
    y = df['label']
    
    # 5-fold Stratified CV for validation
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    fold = 1
    
    model = LogisticRegression(class_weight='balanced', max_iter=1000)
    
    for train_index, test_index in skf.split(X, y):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]
        
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        print(f"--- Fold {fold} ---")
        print(classification_report(y_test, y_pred))
        fold += 1

    # Train final model on all data
    print("Training final model on full dataset...")
    model.fit(X, y)
    
    # Extract coefficients and normalize to sum to 100
    coefs = model.coef_[0]
    # We apply a ReLU-like operation so negative coefficients (if any) become 0
    coefs = [max(0, c) for c in coefs]
    total = sum(coefs)
    
    if total == 0:
        print("Warning: All coefficients are zero!")
        total = 1  # prevent div by zero
        
    weights = {
        "varname":      round((coefs[0] / total) * 100),
        "regex":        round((coefs[1] / total) * 100),
        "entropy":      round((coefs[2] / total) * 100),
        "token_struct": round((coefs[3] / total) * 100),
        "context":      round((coefs[4] / total) * 100),
        "encoding":     round((coefs[5] / total) * 100),
    }
    
    # Adjust for rounding errors so it sums exactly to 100
    diff = 100 - sum(weights.values())
    if diff != 0:
        # add difference to the max weight
        max_k = max(weights, key=weights.get)
        weights[max_k] += diff

    print("\nOptimal Weights Derived:")
    print(json.dumps(weights, indent=2))
    
    with open(output_weights_path, 'w') as f:
        json.dump(weights, f, indent=2)
    print(f"Weights saved to {output_weights_path}")
    
    # Plot ROC curve for the full dataset (for Black Book)
    y_prob = model.predict_proba(X)[:, 1]
    fpr, tpr, _ = roc_curve(y, y_prob)
    roc_auc = auc(fpr, tpr)
    
    plt.figure()
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic')
    plt.legend(loc="lower right")
    roc_path = os.path.join(os.path.dirname(output_weights_path), "roc_curve.png")
    plt.savefig(roc_path)
    print(f"Saved ROC curve to {roc_path}")


if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    data_path = os.path.join(base_dir, "..", "data", "training_dataset.csv")
    out_path = os.path.join(base_dir, "optimal_weights.json")
    train_optimal_weights(data_path, out_path)
