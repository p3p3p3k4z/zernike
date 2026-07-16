#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "matriz.h"
#include "zernike.h"
#include "zernike_algo.h"
#include "data_gen.h"

void export_data(const char* filename, size_t L, size_t N_raw, double radio,
                 Vector* X_raw, Vector* Y_raw, int* mascara, ZernikeFitResult* res) {
    FILE* f = fopen(filename, "wb");
    if (!f) return;
    fwrite(&L, sizeof(size_t), 1, f);
    fwrite(&N_raw, sizeof(size_t), 1, f);
    fwrite(&radio, sizeof(double), 1, f);
    
    fwrite(X_raw->data, sizeof(double), N_raw, f);
    fwrite(Y_raw->data, sizeof(double), N_raw, f);
    
    if (mascara) {
        fwrite(mascara, sizeof(int), N_raw, f);
    } else {
        int* dummy = malloc(N_raw * sizeof(int));
        for(size_t i=0; i<N_raw; i++) dummy[i]=1;
        fwrite(dummy, sizeof(int), N_raw, f);
        free(dummy);
    }
    fwrite(res->A->data, sizeof(double), L, f);
    fclose(f);
}

const char* get_terminal(void) {
    if (system("which gnome-terminal > /dev/null 2>&1") == 0) return "gnome-terminal --";
    if (system("which xterm > /dev/null 2>&1") == 0) return "xterm -e";
    if (system("which konsole > /dev/null 2>&1") == 0) return "konsole -e";
    if (system("which alacritty > /dev/null 2>&1") == 0) return "alacritty -e";
    if (system("which x-terminal-emulator > /dev/null 2>&1") == 0) return "x-terminal-emulator -e";
    return NULL;
}

Vector* vector_copy(Vector* src) {
    Vector* v = vector_create(src->length);
    memcpy(v->data, src->data, src->length * sizeof(double));
    return v;
}

int main(void) {
    srand(42);
    printf("\n############################################################\n");
    printf("  LIBRERIA DE POLINOMIOS ORTOGONALES DE ZERNIKE\n");
    printf("  ISO 10110 |  Grado k=5  |  L=21 polinomios\n");
    printf("############################################################\n\n");
    
    printf("Selecciona el flujo:\n");
    printf("  1. CUADRANTE\n");
    printf("  2. CIRCULO\n");
    printf("  3. CCD\n");
    printf("  4. CCD_SENSOR\n");
    printf("Opcion (1-4): ");
    
    int opcion;
    if (scanf("%d", &opcion) != 1) opcion = 4;
    
    int c; while ((c = getchar()) != '\n' && c != EOF);
    
    Vector *X_raw=NULL, *Y_raw=NULL, *Z_raw=NULL;
    Vector *X_f=NULL, *Y_f=NULL, *Z_f=NULL;
    int* mascara = NULL;
    double radio = 1.0;
    
    if (opcion == 1) {
        printf("\n============================================================\n");
        printf("  Flujo de ajuste de Zernike (Cuadrante I)\n");
        printf("============================================================\n");
        generar_cuadrante(&X_raw, &Y_raw, &Z_raw);
        X_f = vector_copy(X_raw); Y_f = vector_copy(Y_raw); Z_f = vector_copy(Z_raw);
        radio = 10.0;
    } 
    else if (opcion == 2) {
        printf("\n============================================================\n");
        printf("  Generando datos en el Circulo Unitario Completo\n");
        printf("============================================================\n");
        generar_circulo(50, &X_raw, &Y_raw, &Z_raw);
        X_f = vector_copy(X_raw); Y_f = vector_copy(Y_raw); Z_f = vector_copy(Z_raw);
        radio = 1.0;
    } 
    else if (opcion == 3) {
        printf("\n============================================================\n");
        printf("  Flujo CCD: Sensor + Pupila Optica\n");
        printf("============================================================\n");
        printf("\n  Generando los 4 cuadrantes...\n");
        printf("  Ingresa el diametro de la pupila: ");
        double diametro;
        if (scanf("%lf", &diametro) != 1) diametro = 10.0;
        generar_ccd_raw(&X_raw, &Y_raw, &Z_raw);
        aplicar_filtro_pupila(X_raw, Y_raw, Z_raw, diametro, &mascara, &X_f, &Y_f, &Z_f);
        radio = diametro / 2.0;
    } 
    else {
        printf("\n============================================================\n");
        printf("  Flujo CCD Sensor: Malla generada por parametros\n");
        printf("============================================================\n");
        printf("\n--- Configuracion de la Superficie Z ---\n");
        printf("  Ingresa la ecuacion para Z en terminos de x e y (ej: 2*x*y, x**2 + y**2, 3*x*y + 2*x)\n");
        printf("  Presiona ENTER para usar la ecuacion por defecto\n");
        printf("  Z = ");
        char buf[256];
        if(!fgets(buf, sizeof(buf), stdin)) buf[0]='\0';
        SurfaceEq eq = parse_eq(buf);
        
        printf("\n  Ingresa las dimensiones del sensor:\n");
        int N, M;
        printf("    Numero de filas  (N): "); if(scanf("%d", &N) != 1) N = 20;
        printf("    Numero de columnas (M): "); if(scanf("%d", &M) != 1) M = 20;
        printf("  Ingresa el diametro de la pupila: ");
        double diametro; if(scanf("%lf", &diametro) != 1) diametro = 10;
        
        generar_ccd_sensor_raw(N, M, eq, &X_raw, &Y_raw, &Z_raw);
        aplicar_filtro_pupila(X_raw, Y_raw, Z_raw, diametro, &mascara, &X_f, &Y_f, &Z_f);
        radio = diametro / 2.0;
    }
    
    if (!X_f || X_f->length == 0) {
        printf("  ERROR: Ningun punto genero para ajuste tras el filtro.\n");
        return 1;
    }
    
    vector_normalize_inplace(Z_f);
    
    int L = get_zernike_count();
    ZernikePolyFunc* polys = get_zernike_polynomials();
    
    ZernikeFitResult* resultados = ajuste_completo(X_f, Y_f, Z_f, polys, L);
    
    if (resultados) {
        double mse = 0.0;
        for (size_t i = 0; i < Z_f->length; i++) {
            double err = Z_f->data[i] - resultados->W_fit->data[i];
            mse += err * err;
        }
        double rms = sqrt(mse / Z_f->length);
        
        printf("\nError RMS del ajuste: %e\n", rms);
        
        export_data("zernike_temp.bin", L, X_raw->length, radio, X_raw, Y_raw, mascara, resultados);
        
        const char* term = get_terminal();
        if (term) {
            printf("\nLanzando visualizadores paralelos en 2 terminales...\n");
            char cmd[512];
            snprintf(cmd, sizeof(cmd), "%s ./bin/zernike_tui --pupil zernike_temp.bin &", term);
            int sys1 = system(cmd);
            snprintf(cmd, sizeof(cmd), "%s ./bin/zernike_tui --algo zernike_temp.bin &", term);
            int sys2 = system(cmd);
            (void)sys1; (void)sys2;
        } else {
            printf("\nError: No se encontro terminal compatible para lanzar UI externa.\n");
        }
        
        zernike_fit_free(resultados);
    }
    
    vector_free(X_raw); vector_free(Y_raw); vector_free(Z_raw);
    vector_free(X_f); vector_free(Y_f); vector_free(Z_f);
    if (mascara) free(mascara);
    
    return 0;
}
