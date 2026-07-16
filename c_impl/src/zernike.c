#include "zernike.h"
#include <math.h>

static double z1_piston(double x, double y) { (void)x; (void)y; return 1.0; }
static double z2_tilt_x(double x, double y) { (void)y; return x; }
static double z3_tilt_y(double x, double y) { (void)x; return y; }
static double z4_astig_45(double x, double y) { return 2.0 * x * y; }
static double z5_defocus(double x, double y) { return -1.0 + 2.0 * y * y + 2.0 * x * x; }
static double z6_astig_0(double x, double y) { return y * y - x * x; }
static double z7_coma_x(double x, double y) { return 3.0 * x * y * y - x * x * x; }
static double z8_coma_y(double x, double y) { return -2.0 * x + 3.0 * x * y * y + 3.0 * x * x * x; }
static double z9_p9(double x, double y) { return -2.0 * y + 3.0 * y * y * y + 3.0 * x * x * y; }
static double z10_p10(double x, double y) { return y * y * y - 3.0 * x * x * y; }
static double z11_p11(double x, double y) { return 4.0 * y * y * y * x - 4.0 * x * x * x * y; }
static double z12_p12(double x, double y) { return -6.0 * x * y + 8.0 * y * y * y * x + 8.0 * x * x * x * y; }
static double z13_p13(double x, double y) { return 1.0 - 6.0 * y * y - 6.0 * x * x + 6.0 * pow(y, 4) + 12.0 * x * x * y * y + 6.0 * pow(x, 4); }
static double z14_p14(double x, double y) { return -3.0 * y * y + 3.0 * x * x + 4.0 * pow(y, 4) - 4.0 * pow(x, 4); }
static double z15_p15(double x, double y) { return pow(y, 4) - 6.0 * x * x * y * y + pow(x, 4); }
static double z16_p16(double x, double y) { return 5.0 * x * pow(y, 4) - 10.0 * pow(x, 3) * y * y + pow(x, 5); }
static double z17_p17(double x, double y) { return -12.0 * x * y * y + 4.0 * pow(x, 3) + 15.0 * x * pow(y, 4) + 10.0 * pow(x, 3) * y * y - 5.0 * pow(x, 5); }
static double z18_p18(double x, double y) { return 3.0 * x - 12.0 * x * y * y - 12.0 * pow(x, 3) + 10.0 * x * pow(y, 4) + 20.0 * pow(x, 3) * y * y + 10.0 * pow(x, 5); }
static double z19_p19(double x, double y) { return 3.0 * y - 12.0 * pow(y, 3) - 12.0 * x * x * y + 10.0 * pow(y, 5) + 20.0 * x * x * pow(y, 3) + 10.0 * pow(x, 4) * y; }
static double z20_p20(double x, double y) { return -4.0 * pow(y, 3) + 12.0 * x * x * y + 5.0 * pow(y, 5) - 10.0 * x * x * pow(y, 3) - 15.0 * pow(x, 4) * y; }
static double z21_p21(double x, double y) { return pow(y, 5) - 10.0 * x * x * pow(y, 3) + 5.0 * pow(x, 4) * y; }

/* Arreglo estatico que unifica las 21 bases de Zernike. 
   Esto permite que la rutina de evaluacion las calcule iterando con bucles for. */
static ZernikePolyFunc z_funcs[21] = {
    z1_piston, z2_tilt_x, z3_tilt_y, z4_astig_45, z5_defocus,
    z6_astig_0, z7_coma_x, z8_coma_y, z9_p9, z10_p10,
    z11_p11, z12_p12, z13_p13, z14_p14, z15_p15,
    z16_p16, z17_p17, z18_p18, z19_p19, z20_p20,
    z21_p21
};

ZernikePolyFunc* get_zernike_polynomials(void) {
    return z_funcs;
}

int get_zernike_count(void) {
    return 21;
}
