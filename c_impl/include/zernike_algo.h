#ifndef ZERNIKE_ALGO_H
#define ZERNIKE_ALGO_H

#include "matriz.h"
#include "zernike.h"

/* Agrupa el estado matematico completo de un ajuste, evitando retornar o gestionar
   multiples punteros dispersos tras ejecutar el pipeline de Gram-Schmidt. */
typedef struct {
    Matrix* U;
    Matrix* V;
    Matrix* D;
    Vector* F;
    Vector* B;
    Matrix* C;
    Vector* A;
    Vector* W_fit;
    
    Vector* X;
    Vector* Y;
    Vector* W;
} ZernikeFitResult;

Matrix* evaluar_polinomios(const Vector* X, const Vector* Y, ZernikePolyFunc* polys, int L);
void construir_base_ortogonal(const Matrix* U, Matrix** out_V, Matrix** out_D, Vector** out_F);
Vector* calcular_B(const Vector* W_exp, const Matrix* V, const Vector* F);
Matrix* calcular_C(const Matrix* D, int L);
Vector* calcular_A(const Vector* B, const Matrix* C, int L);
Vector* reconstruir_W(const Vector* A, const Matrix* U);

ZernikeFitResult* ajuste_completo(const Vector* X, const Vector* Y, const Vector* W, ZernikePolyFunc* polys, int L);

void zernike_fit_free(ZernikeFitResult* res);

#endif /* ZERNIKE_ALGO_H */
