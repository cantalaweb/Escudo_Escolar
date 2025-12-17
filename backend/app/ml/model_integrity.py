"""
Configuración de integridad y seguridad del modelo ML

Este archivo contiene los valores de seguridad validados del modelo:
- Hash SHA-256 del modelo para verificar integridad
- Umbral óptimo validado durante el entrenamiento

IMPORTANTE:
- Si reentrenas el modelo, debes actualizar MODEL_SHA256
- Para calcular el hash: shasum -a 256 models/bullying_detection_model.json
- El umbral debe coincidir con el valor optimizado en el entrenamiento
"""

# Hash SHA-256 del modelo validado
# Generado: 2025-12-17
# Comando usado: shasum -a 256 models/bullying_detection_model.json
MODEL_SHA256 = "4179866ece8c15598bc83bc6a576fbda2ebb34dc3072241782d5d2d31dd2c26a"

# Umbral óptimo del modelo (optimizado para F2-score)
# Este valor debe coincidir con el umbral determinado durante el entrenamiento
OPTIMAL_THRESHOLD = 0.7117

# Metadatos del modelo (para auditoría)
MODEL_METADATA = {
    "version": "1.0",
    "trained_date": "2025-12-16",
    "training_script": "data/src/train_model.py",
    "model_type": "XGBoost Classifier",
    "optimization_metric": "F2-score",
    "expected_threshold": OPTIMAL_THRESHOLD,
}
