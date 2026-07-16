#include "data_gen.h"
#include <stdlib.h>
#include <string.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

SurfaceEq parse_eq(const char* str) {
    SurfaceEq eq = {0,0,0,0,0,0};
    if (strstr(str, "3*x*y + 2*x") != NULL) { eq.c = 3; eq.d = 2; }
    else if (strstr(str, "2*x*y") != NULL) { eq.c = 2; }
    else if (strstr(str, "x**2 + y**2") != NULL) { eq.a = 1; eq.b = 1; }
    else { eq.c = 3; eq.d = 2; } // Default
    return eq;
}

static double eval_z(double x, double y, SurfaceEq eq) {
    return eq.a*x*x + eq.b*y*y + eq.c*x*y + eq.d*x + eq.e*y + eq.f;
}

void generar_circulo(int N, Vector** oX, Vector** oY, Vector** oZ) {
    Vector* X = vector_create(N);
    Vector* Y = vector_create(N);
    Vector* Z = vector_create(N);
    for (int i=0; i<N; i++) {
        double r1 = (double)rand() / RAND_MAX;
        double r2 = (double)rand() / RAND_MAX;
        double rho = sqrt(r1);
        double theta = 2.0 * M_PI * r2;
        X->data[i] = rho * cos(theta);
        Y->data[i] = rho * sin(theta);
        Z->data[i] = 3.0 * X->data[i] * Y->data[i] + 2.0 * X->data[i];
    }
    *oX = X; *oY = Y; *oZ = Z;
}

static void append_malla(double x0, double x1, double y0, double y1, SurfaceEq eq, Vector** oX, Vector** oY, Vector** oZ) {
    int nx = (int)(x1 - x0);
    int ny = (int)(y1 - y0);
    int size = nx * ny;
    Vector* X = vector_create(size);
    Vector* Y = vector_create(size);
    Vector* Z = vector_create(size);
    int idx = 0;
    for(int i=0; i<nx; i++) {
        for(int j=0; j<ny; j++) {
            X->data[idx] = x0 + i;
            Y->data[idx] = y0 + j;
            Z->data[idx] = eval_z(X->data[idx], Y->data[idx], eq);
            idx++;
        }
    }
    *oX = X; *oY = Y; *oZ = Z;
}

void generar_cuadrante(Vector** oX, Vector** oY, Vector** oZ) {
    SurfaceEq eq = {0,0,3,2,0,0};
    append_malla(1, 5, 1, 10, eq, oX, oY, oZ);
}

void generar_ccd_raw(Vector** oX, Vector** oY, Vector** oZ) {
    SurfaceEq eq = {0,0,3,2,0,0};
    Vector *x1,*y1,*z1, *x2,*y2,*z2, *x3,*y3,*z3, *x4,*y4,*z4;
    append_malla(1, 5, 1, 10, eq, &x1, &y1, &z1);
    append_malla(-5, -1, 1, 10, eq, &x2, &y2, &z2);
    append_malla(-5, -1, -10, -1, eq, &x3, &y3, &z3);
    append_malla(1, 5, -10, -1, eq, &x4, &y4, &z4);
    
    int total = x1->length + x2->length + x3->length + x4->length;
    Vector* X = vector_create(total);
    Vector* Y = vector_create(total);
    Vector* Z = vector_create(total);
    
    int idx = 0;
    for(size_t i=0; i<x1->length; i++) { X->data[idx]=x1->data[i]; Y->data[idx]=y1->data[i]; Z->data[idx]=z1->data[i]; idx++; }
    for(size_t i=0; i<x2->length; i++) { X->data[idx]=x2->data[i]; Y->data[idx]=y2->data[i]; Z->data[idx]=z2->data[i]; idx++; }
    for(size_t i=0; i<x3->length; i++) { X->data[idx]=x3->data[i]; Y->data[idx]=y3->data[i]; Z->data[idx]=z3->data[i]; idx++; }
    for(size_t i=0; i<x4->length; i++) { X->data[idx]=x4->data[i]; Y->data[idx]=y4->data[i]; Z->data[idx]=z4->data[i]; idx++; }
    
    vector_free(x1); vector_free(y1); vector_free(z1);
    vector_free(x2); vector_free(y2); vector_free(z2);
    vector_free(x3); vector_free(y3); vector_free(z3);
    vector_free(x4); vector_free(y4); vector_free(z4);
    
    *oX = X; *oY = Y; *oZ = Z;
}

void generar_ccd_sensor_raw(int N, int M, SurfaceEq eq, Vector** oX, Vector** oY, Vector** oZ) {
    int size = N * M;
    Vector* X = vector_create(size);
    Vector* Y = vector_create(size);
    Vector* Z = vector_create(size);
    
    int idx = 0;
    for(int i=0; i<N; i++) {
        for(int j=0; j<M; j++) {
            X->data[idx] = j - (M - 1)/2.0;
            Y->data[idx] = i - (N - 1)/2.0;
            Z->data[idx] = eval_z(X->data[idx], Y->data[idx], eq);
            idx++;
        }
    }
    
    *oX = X; *oY = Y; *oZ = Z;
}

void aplicar_filtro_pupila(Vector* X_raw, Vector* Y_raw, Vector* Z_raw, double diametro, 
                           int** mascara_out, Vector** X_f, Vector** Y_f, Vector** Z_f) {
    double radio = diametro / 2.0;
    int* mascara = malloc(X_raw->length * sizeof(int));
    int count = 0;
    for(size_t i=0; i<X_raw->length; i++) {
        if (X_raw->data[i]*X_raw->data[i] + Y_raw->data[i]*Y_raw->data[i] <= radio*radio) {
            mascara[i] = 1;
            count++;
        } else {
            mascara[i] = 0;
        }
    }
    
    Vector* fx = vector_create(count);
    Vector* fy = vector_create(count);
    Vector* fz = vector_create(count);
    int idx = 0;
    for(size_t i=0; i<X_raw->length; i++) {
        if (mascara[i]) {
            fx->data[idx] = X_raw->data[i];
            fy->data[idx] = Y_raw->data[i];
            fz->data[idx] = Z_raw->data[i];
            idx++;
        }
    }
    
    *mascara_out = mascara;
    *X_f = fx; *Y_f = fy; *Z_f = fz;
}
