#ifndef DATA_GEN_H
#define DATA_GEN_H

#include "matriz.h"

typedef struct {
    double a, b, c, d, e, f;
} SurfaceEq;

SurfaceEq parse_eq(const char* str);
double eval_z(double x, double y, SurfaceEq eq);

void generar_circulo(int N, Vector** X, Vector** Y, Vector** Z);
void generar_cuadrante(Vector** X, Vector** Y, Vector** Z);
void generar_ccd_raw(Vector** X, Vector** Y, Vector** Z);
void generar_ccd_sensor_raw(int N, int M, SurfaceEq eq, Vector** X, Vector** Y, Vector** Z);
void aplicar_filtro_pupila(Vector* X_raw, Vector* Y_raw, Vector* Z_raw, double diametro, 
                           int** mascara_out, Vector** X_f, Vector** Y_f, Vector** Z_f);

int cargar_csv_xyz(const char* filepath, Vector** X, Vector** Y, Vector** Z);

#endif /* DATA_GEN_H */
