#include "zernike_algo.h"
#include <stdlib.h>
#include <stdio.h>
#include <math.h>

/* Calcula proyecciones vectoriales escalares base del algoritmo iterativo. */
static double dot_product(const double* v1, const double* v2, size_t n) {
    double sum = 0.0;
    for (size_t i = 0; i < n; i++) sum += v1[i] * v2[i];
    return sum;
}

Matrix* evaluar_polinomios(const Vector* X, const Vector* Y, ZernikePolyFunc* polys, int L) {
    /* U guarda la matriz de diseno, filas por polinomio (L), columnas por punto espacial (N) */
    size_t N = X->length;
    Matrix* U = matrix_create(L, N);
    if (!U) return NULL;
    
    for (int r = 0; r < L; r++) {
        for (size_t i = 0; i < N; i++) {
            U->data[r][i] = polys[r](X->data[i], Y->data[i]);
        }
    }
    return U;
}

void construir_base_ortogonal(const Matrix* U, Matrix** out_V, Matrix** out_D, Vector** out_F) {
    /* Implementacion del metodo de Gram-Schmidt.
       Cada polinomio U se purga de correlaciones con polinomios inferiores p < r, 
       generando una base verdaderamente ortogonal V. */
    size_t L = U->rows;
    size_t N = U->cols;
    
    Matrix* V = matrix_create(L, N);
    Matrix* D = matrix_create(L, L);
    Vector* F = vector_create(L);
    
    for (size_t i = 0; i < N; i++) V->data[0][i] = U->data[0][i];
    F->data[0] = dot_product(V->data[0], V->data[0], N);
    
    for (size_t r = 1; r < L; r++) {
        for (size_t i = 0; i < N; i++) V->data[r][i] = U->data[r][i];
        
        for (size_t p = 0; p < r; p++) {
            double Drp = -dot_product(U->data[r], V->data[p], N) / F->data[p];
            D->data[r][p] = Drp;
            for (size_t i = 0; i < N; i++) {
                V->data[r][i] += Drp * V->data[p][i];
            }
        }
        F->data[r] = dot_product(V->data[r], V->data[r], N);
    }
    
    *out_V = V;
    *out_D = D;
    *out_F = F;
}

Vector* calcular_B(const Vector* W_exp, const Matrix* V, const Vector* F) {
    size_t L = V->rows;
    size_t N = W_exp->length;
    Vector* B = vector_create(L);
    
    for (size_t p = 0; p < L; p++) {
        B->data[p] = dot_product(W_exp->data, V->data[p], N) / F->data[p];
    }
    return B;
}

Matrix* calcular_C(const Matrix* D, int L) {
    /* Reconstruye dependencias en retroceso para mapear los coeficientes desde V hasta U */
    Matrix* C = matrix_create(L, L);
    
    for (int r = 0; r < L; r++) C->data[r][r] = 1.0;
    
    for (int r = 1; r < L; r++) {
        for (int i = 0; i < r; i++) {
            double sum = 0.0;
            for (int s = 1; s <= r - i; s++) {
                sum += D->data[r][r - s] * C->data[r - s][i];
            }
            C->data[r][i] = sum;
        }
    }
    return C;
}

Vector* calcular_A(const Vector* B, const Matrix* C, int L) {
    /* Obtencion final de coeficientes segun ISO 10110 mediante suma ponderada */
    Vector* A = vector_create(L);
    A->data[L - 1] = B->data[L - 1];
    
    for (int r = L - 2; r >= 0; r--) {
        double sum = 0.0;
        for (int i = r + 1; i < L; i++) {
            sum += B->data[i] * C->data[i][r];
        }
        A->data[r] = B->data[r] + sum;
    }
    return A;
}

Vector* reconstruir_W(const Vector* A, const Matrix* U) {
    size_t L = U->rows;
    size_t N = U->cols;
    Vector* W_fit = vector_create(N);
    
    for (size_t i = 0; i < N; i++) {
        double val = 0.0;
        for (size_t r = 0; r < L; r++) {
            val += A->data[r] * U->data[r][i];
        }
        W_fit->data[i] = val;
    }
    return W_fit;
}

ZernikeFitResult* ajuste_completo(const Vector* X, const Vector* Y, const Vector* W, ZernikePolyFunc* polys, int L) {
    /* Orquesta la memoria y fases algebraicas.
       Concentra todo el flujo y exporta una sola estructura consolidada. */
    ZernikeFitResult* res = (ZernikeFitResult*)malloc(sizeof(ZernikeFitResult));
    if (!res) return NULL;
    
    res->X = (Vector*)X;
    res->Y = (Vector*)Y;
    res->W = (Vector*)W;
    
    res->U = evaluar_polinomios(X, Y, polys, L);
    construir_base_ortogonal(res->U, &res->V, &res->D, &res->F);
    res->B = calcular_B(W, res->V, res->F);
    res->C = calcular_C(res->D, L);
    res->A = calcular_A(res->B, res->C, L);
    res->W_fit = reconstruir_W(res->A, res->U);
    
    return res;
}

void zernike_fit_free(ZernikeFitResult* res) {
    if (res) {
        matrix_free(res->U);
        matrix_free(res->V);
        matrix_free(res->D);
        vector_free(res->F);
        vector_free(res->B);
        matrix_free(res->C);
        vector_free(res->A);
        vector_free(res->W_fit);
        free(res);
    }
}
