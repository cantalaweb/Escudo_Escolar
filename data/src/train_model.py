import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, precision_recall_curve, fbeta_score
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import os

warnings.simplefilter(action='ignore', category=FutureWarning)
os.makedirs('./models', exist_ok=True)

DATASET_PATH = './data/processed/dataset_training_bullying_enhanced.csv'
MODEL_PATH = './models/bullying_detection_model.json'
TEST_SIZE_ALUMNOS = 0.25
SEED = 42

def entrenar_modelo():
    print("1. Cargando dataset...")
    df = pd.read_csv(DATASET_PATH)
    df = df.dropna(subset=['is_bullying_active'])
    
    print("2. Dividiendo datos...")
    gss = GroupShuffleSplit(n_splits=1, test_size=TEST_SIZE_ALUMNOS, random_state=SEED)
    
    cols_a_excluir = ['fecha', 'colegio_id', 'clase_id', 'alumno_id', 'is_bullying_active']
    cols_trampa = [c for c in df.columns if 'meta_' in c]
    features = [c for c in df.columns if c not in cols_a_excluir + cols_trampa]
    # Limpieza de seguridad
    features = [f for f in features if 'intuicion_mean_30d' not in f and 'n_reportes_testigos_mean_30d' not in f]
    
    target = 'is_bullying_active'
    train_idx, test_idx = next(gss.split(df, groups=df['alumno_id']))
    X_train = df.iloc[train_idx][features]
    y_train = df.iloc[train_idx][target]
    X_test = df.iloc[test_idx][features]
    y_test = df.iloc[test_idx][target]
    
    print("3. Entrenando XGBoost (Smart Interactions)...")
    
    ratio = float(np.sum(y_train == 0)) / np.sum(y_train == 1)
    scale_pos_weight_adjusted = ratio * 1.2 # Mantenemos el peso equilibrado
    
    clf = xgb.XGBClassifier(
        n_estimators=250,
        learning_rate=0.02,
        max_depth=6,
        min_child_weight=2,
        gamma=1.5,
        subsample=0.75,
        colsample_bytree=0.75,
        scale_pos_weight=scale_pos_weight_adjusted, 
        eval_metric='aucpr',
        random_state=SEED,
        n_jobs=-1
    )
    
    clf.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

    print("4. Buscando el Umbral Óptimo (Maximizar F2-Score)...")
    
    y_proba = clf.predict_proba(X_test)[:, 1]
    
    precisions, recalls, thresholds = precision_recall_curve(y_test, y_proba)
    
    # Calcular F2-Score para cada umbral posible
    # F2 penaliza los falsos negativos más que los falsos positivos (beta=2)
    f2_scores = (5 * precisions * recalls) / (4 * precisions + recalls + 1e-10)
    
    # Encontrar el índice del mejor F2
    best_idx = np.argmax(f2_scores)
    best_threshold = thresholds[best_idx]
    best_f2 = f2_scores[best_idx]
    
    print(f"   -> Mejor Umbral encontrado: {best_threshold:.4f}")
    print(f"   -> F2-Score esperado: {best_f2:.4f}")
    
    # Aplicar umbral
    y_pred_adjusted = (y_proba >= best_threshold).astype(int)
    
    print("\n" + "="*60)
    print(f"INFORME FINAL (Optimizado F2)")
    print("="*60)
    
    cm = confusion_matrix(y_test, y_pred_adjusted)
    print(f"Verdaderos Negativos: {cm[0][0]}")
    print(f"Falsos Positivos:     {cm[0][1]}")
    print(f"Falsos Negativos:     {cm[1][0]}")
    print(f"Verdaderos Positivos: {cm[1][1]}")
    
    print(classification_report(y_test, y_pred_adjusted, target_names=['Normal', 'Bullying']))
    
    # Gráfico
    importance = clf.feature_importances_
    feature_imp = pd.DataFrame(sorted(zip(importance, features)), columns=['Value','Feature'])
    top_features = feature_imp.sort_values(by="Value", ascending=False).head(20)
    plt.figure(figsize=(10, 8))
    sns.barplot(x="Value", y="Feature", data=top_features)
    plt.title('Top 20 Variables (Modelo Final)')
    plt.tight_layout()
    plt.savefig('feature_importance_bullying.png')
    
    clf.get_booster().save_model(MODEL_PATH)
    print(f"Modelo guardado en {MODEL_PATH}")
    print(f"NOTA: Umbral recomendado > {best_threshold:.4f}")

if __name__ == "__main__":
    entrenar_modelo()
