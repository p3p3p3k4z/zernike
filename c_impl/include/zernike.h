#ifndef ZERNIKE_H
#define ZERNIKE_H

#include "matriz.h"

/* Definicion de tipo puntero a funcion, permite iterar polinomios desde un arreglo simple. */
typedef double (*ZernikePolyFunc)(double x, double y);

ZernikePolyFunc* get_zernike_polynomials(void);
int get_zernike_count(void);

#endif /* ZERNIKE_H */
