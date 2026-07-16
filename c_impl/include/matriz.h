#ifndef MATRIZ_H
#define MATRIZ_H

#include <stddef.h>

/* Estructura para arreglos 1D para encapsular longitud y facilitar iteraciones seguras. */
typedef struct {
    double* data;
    size_t length;
} Vector;

/* Estructura para arreglos 2D para mapear la relacion entre polinomios y puntos evaluados. */
typedef struct {
    double** data;
    size_t rows;
    size_t cols;
} Matrix;

Vector* vector_create(size_t length);
void vector_free(Vector* v);

Matrix* matrix_create(size_t rows, size_t cols);
void matrix_free(Matrix* m);

double vector_max_abs(const Vector* v);
void vector_normalize_inplace(Vector* v);
void vector_print(const Vector* v, const char* name, int max_items);
void matrix_print(const Matrix* m, const char* name);

#endif /* MATRIZ_H */
