#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ncurses.h>
#include <unistd.h>
#include <math.h>

#define COLOR_U 1
#define COLOR_V 2
#define COLOR_D 3
#define COLOR_B 4
#define COLOR_C 5
#define COLOR_A 6
#define COLOR_PUPIL 7
#define COLOR_POINT 8
#define COLOR_EXCLUDED 9

// draw_points_mode removed

void draw_pupil_mode(size_t N, double* X, double* Y, int* mascara, double radio) {
    int max_y, max_x;
    getmaxyx(stdscr, max_y, max_x);
    WINDOW *win = newwin(max_y, max_x, 0, 0);
    box(win, 0, 0);
    mvwprintw(win, 0, 4, "[ TERMINAL 1: FILTRADO POR PUPILA (V=Dentro, U=Fuera) ]");
    
    int center_y = max_y / 2;
    int center_x = max_x / 2;
    int radius_y = (max_y - 6) / 2;
    int radius_x = radius_y * 2; 
    
    double max_r = 0;
    for(size_t i=0; i<N; i++) {
        double r = sqrt(X[i]*X[i] + Y[i]*Y[i]);
        if(r > max_r) max_r = r;
    }
    if (max_r == 0) max_r = 1;

    // Circulo pupila (Color D = amarillo/naranja equivalente a matplot)
    wattron(win, COLOR_PAIR(COLOR_D));
    for (int theta = 0; theta < 360; theta += 2) {
        double rad_ang = theta * 3.14159 / 180.0;
        int px = center_x + (int)((radio/max_r) * radius_x * cos(rad_ang));
        int py = center_y - (int)((radio/max_r) * radius_y * sin(rad_ang));
        if (px > 0 && px < max_x - 1 && py > 0 && py < max_y - 1) {
            mvwaddch(win, py, px, '.');
            wrefresh(win);
            napms(2);
        }
    }
    wattroff(win, COLOR_PAIR(COLOR_D));
    napms(200);

    // Puntos (Rojo excluido, Verde incluido)
    for (size_t i = 0; i < N; i++) {
        int px = center_x + (int)((X[i]/max_r) * radius_x);
        int py = center_y - (int)((Y[i]/max_r) * radius_y);
        
        if (px > 0 && px < max_x - 1 && py > 0 && py < max_y - 1) {
            if (mascara[i]) {
                wattron(win, COLOR_PAIR(COLOR_V) | A_BOLD); // Verde
                mvwaddch(win, py, px, 'O');
                wattroff(win, COLOR_PAIR(COLOR_V) | A_BOLD);
            } else {
                wattron(win, COLOR_PAIR(COLOR_U)); // Rojo
                mvwaddch(win, py, px, 'x');
                wattroff(win, COLOR_PAIR(COLOR_U));
            }
            wrefresh(win);
            napms(2);
        }
    }
    
    wattron(win, A_REVERSE);
    mvwprintw(win, max_y - 1, 4, " Terminado. Presiona tecla para cerrar... ");
    wattroff(win, A_REVERSE);
    wrefresh(win);
    flushinp();
    wgetch(win);
    delwin(win);
}

void draw_algo_mode(size_t L, double* A) {
    int max_y, max_x;
    getmaxyx(stdscr, max_y, max_x);
    WINDOW *win_title = newwin(3, max_x, 0, 0);
    WINDOW *win_log = newwin(8, max_x, 3, 0);
    WINDOW *win_bars = newwin((int)L + 2, max_x, 11, 0);

    box(win_title, 0, 0);
    mvwprintw(win_title, 1, (max_x - 36) / 2, "[ TERMINAL 2: RECURSIVO ]");
    wrefresh(win_title);

    box(win_log, 0, 0);
    box(win_bars, 0, 0);
    
    int delay = 200; // 200ms por iteracion (similar a 180ms python)
    
    // Preparar nombres Z
    for (size_t r = 0; r < L; r++) {
        mvwprintw(win_bars, (int)r + 1, 2, "Z%02zu |", r + 1);
    }
    wrefresh(win_bars);
    
    mvwprintw(win_log, 1, 2, ">>> 1. Base polinomial U_r...");
    wrefresh(win_log);
    for (size_t r = 0; r < L; r++) {
        wattron(win_bars, COLOR_PAIR(COLOR_U));
        mvwprintw(win_bars, (int)r + 1, 8, "[ U ]");
        wattroff(win_bars, COLOR_PAIR(COLOR_U));
        wrefresh(win_bars);
        napms(delay);
    }

    mvwprintw(win_log, 2, 2, ">>> 2. Gram-Schmidt V_0...");
    wrefresh(win_log);
    wattron(win_bars, COLOR_PAIR(COLOR_V));
    mvwprintw(win_bars, 1, 15, "[ V ]");
    wattroff(win_bars, COLOR_PAIR(COLOR_V));
    wrefresh(win_bars);
    napms(delay);

    mvwprintw(win_log, 2, 2, ">>> 2. Gram-Schmidt Recursivo (D_r, V_r)...");
    wrefresh(win_log);
    for (size_t r = 1; r < L; r++) {
        wattron(win_bars, COLOR_PAIR(COLOR_D));
        mvwprintw(win_bars, (int)r + 1, 22, "[ D ]");
        wattroff(win_bars, COLOR_PAIR(COLOR_D));
        wrefresh(win_bars);
        napms(delay);
        
        wattron(win_bars, COLOR_PAIR(COLOR_V));
        mvwprintw(win_bars, (int)r + 1, 15, "[ V ]");
        wattroff(win_bars, COLOR_PAIR(COLOR_V));
        wrefresh(win_bars);
        napms(delay);
    }
    
    mvwprintw(win_log, 3, 2, ">>> 3. Pesos ortogonales B_r...");
    wrefresh(win_log);
    for (size_t r = 0; r < L; r++) {
        wattron(win_bars, COLOR_PAIR(COLOR_B));
        mvwprintw(win_bars, (int)r + 1, 29, "[ B ]");
        wattroff(win_bars, COLOR_PAIR(COLOR_B));
        wrefresh(win_bars);
        napms(delay);
    }
    
    mvwprintw(win_log, 4, 2, ">>> 4. Matriz de traslacion C_r...");
    wrefresh(win_log);
    wattron(win_bars, COLOR_PAIR(COLOR_C));
    mvwprintw(win_bars, 1, 36, "[ C ]");
    wattroff(win_bars, COLOR_PAIR(COLOR_C));
    wrefresh(win_bars);
    napms(delay);
    
    for (size_t r = 1; r < L; r++) {
        wattron(win_bars, COLOR_PAIR(COLOR_C));
        mvwprintw(win_bars, (int)r + 1, 36, "[ C ]");
        wattroff(win_bars, COLOR_PAIR(COLOR_C));
        wrefresh(win_bars);
        napms(delay);
    }
    
    mvwprintw(win_log, 5, 2, ">>> 5. Coeficientes A_r (Regresion hacia atras)...");
    wrefresh(win_log);
    for (int r = (int)L - 1; r >= 0; r--) {
        wattron(win_bars, COLOR_PAIR(COLOR_A));
        mvwprintw(win_bars, r + 1, 43, "A = %+.4f", A[r]);
        wattroff(win_bars, COLOR_PAIR(COLOR_A));
        wrefresh(win_bars);
        napms(delay);
    }

    wattron(win_log, A_BOLD);
    mvwprintw(win_log, 6, 2, "==== ANIMACION COMPLETADA ====");
    wattroff(win_log, A_BOLD);
    wattron(win_log, A_REVERSE);
    mvwprintw(win_log, 6, 35, " Presiona tecla para cerrar... ");
    wattroff(win_log, A_REVERSE);
    wrefresh(win_log);

    flushinp();
    wgetch(win_log);

    delwin(win_title);
    delwin(win_log);
    delwin(win_bars);
}

int main(int argc, char** argv) {
    if (argc < 3) return 1;
    const char* mode = argv[1];
    FILE* f = fopen(argv[2], "rb");
    if (!f) return 1;
    
    size_t L, N;
    double radio;
    if (fread(&L, sizeof(size_t), 1, f) != 1) return 1;
    if (fread(&N, sizeof(size_t), 1, f) != 1) return 1;
    if (fread(&radio, sizeof(double), 1, f) != 1) return 1;
    
    double* X = malloc(N * sizeof(double));
    double* Y = malloc(N * sizeof(double));
    int* mascara = malloc(N * sizeof(int));
    double* A = malloc(L * sizeof(double));
    
    fread(X, sizeof(double), N, f);
    fread(Y, sizeof(double), N, f);
    fread(mascara, sizeof(int), N, f);
    fread(A, sizeof(double), L, f);
    fclose(f);
    
    initscr();
    cbreak();
    noecho();
    curs_set(0);
    
    if (has_colors()) {
        start_color();
        init_pair(COLOR_U, COLOR_RED, COLOR_BLACK);
        init_pair(COLOR_V, COLOR_GREEN, COLOR_BLACK);
        init_pair(COLOR_D, COLOR_YELLOW, COLOR_BLACK);
        init_pair(COLOR_B, COLOR_BLUE, COLOR_BLACK);
        init_pair(COLOR_C, COLOR_MAGENTA, COLOR_BLACK);
        init_pair(COLOR_A, COLOR_CYAN, COLOR_BLACK);
        init_pair(COLOR_PUPIL, COLOR_WHITE, COLOR_BLACK);
        init_pair(COLOR_POINT, COLOR_CYAN, COLOR_BLACK);
    }

    if (strcmp(mode, "--pupil") == 0) {
        draw_pupil_mode(N, X, Y, mascara, radio);
    } else if (strcmp(mode, "--algo") == 0) {
        draw_algo_mode(L, A);
    }

    endwin();
    
    free(X); free(Y); free(mascara); free(A);
    return 0;
}
