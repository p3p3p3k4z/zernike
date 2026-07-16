#include "matriz.h"
#include <stdlib.h>
#include <stdio.h>
#include <math.h>

Vector* vector_create(size_t length) {
    /* calloc limpia la memoria con ceros, previniendo errores por basura residual. */
    Vector* v = (Vector*)malloc(sizeof(Vector));
    if (!v) return NULL;
    v->length = length;
    v->data = (double*)calloc(length, sizeof(double));
    if (!v->data) {
        free(v);
        return NULL;
    }
    return v;
}

void vector_free(Vector* v) {
    /* Es seguro llamar a free con NULL, pero validamos v primero para evitar segmentation fault. */
    if (v) {
        if (v->data) free(v->data);
        free(v);
    }
}

Matrix* matrix_create(size_t rows, size_t cols) {
    /* Mapeamos un arreglo de punteros, donde cada puntero dirige a una fila.
       Esto permite acceso rapido m->data[r][c] imitando las matrices bidimensionales. */
    Matrix* m = (Matrix*)malloc(sizeof(Matrix));
    if (!m) return NULL;
    m->rows = rows;
    m->cols = cols;
    m->data = (double**)malloc(rows * sizeof(double*));
    if (!m->data) {
        free(m);
        return NULL;
    }
    for (size_t i = 0; i < rows; i++) {
        m->data[i] = (double*)calloc(cols, sizeof(double));
        if (!m->data[i]) {
            for (size_t j = 0; j < i; j++) {
                free(m->data[j]);
            }
            free(m->data);
            free(m);
            return NULL;
        }
    }
    return m;
}

void matrix_free(Matrix* m) {
    if (m) {
        if (m->data) {
            for (size_t i = 0; i < m->rows; i++) {
                if (m->data[i]) free(m->data[i]);
            }
            free(m->data);
        }
        free(m);
    }
}

double vector_max_abs(const Vector* v) {
    double max_val = 0.0;
    for (size_t i = 0; i < v->length; i++) {
        double abs_val = fabs(v->data[i]);
        if (abs_val > max_val) {
            max_val = abs_val;
        }
    }
    return max_val;
}

void vector_normalize_inplace(Vector* v) {
    /* Escala los datos al rango unitario [-1, 1] dividiendo por su valor maximo absoluto.
       Esto previene desbordamientos aritmeticos en el ajuste ortogonal (Gram-Schmidt). */
    double max_val = vector_max_abs(v);
    if (max_val > 0.0) {
        for (size_t i = 0; i < v->length; i++) {
            v->data[i] /= max_val;
        }
    }
}

void vector_print(const Vector* v, const char* name, int max_items) {
    printf("\n--- Vector: %s ---\n", name);
    int limit = (max_items > 0 && (size_t)max_items < v->length) ? max_items : (int)v->length;
    for (int i = 0; i < limit; i++) {
        printf("[%d]: %9.4f\n", i, v->data[i]);
    }
    if ((size_t)limit < v->length) {
        printf("... (%zu elementos en total)\n", v->length);
    }
}

void matrix_print(const Matrix* m, const char* name) {
    printf("\n--- Matriz: %s ---\n", name);
    for (size_t i = 0; i < m->rows; i++) {
        printf("r%02zu | ", i);
        for (size_t j = 0; j < m->cols; j++) {
            if (fabs(m->data[i][j]) > 1e-10) {
                printf("%9.4f ", m->data[i][j]);
            } else {
                printf("   .      ");
            }
        }
        printf("\n");
    }
}
