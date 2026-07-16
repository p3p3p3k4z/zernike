CC = gcc
CFLAGS = -Wall -Wextra -O2 -I./include
LDFLAGS = -lm -lncurses

SRC_DIR = src
OBJ_DIR = obj
BIN_DIR = bin

TARGET_APP = $(BIN_DIR)/zernike_app
TARGET_TUI = $(BIN_DIR)/zernike_tui

all: directories $(TARGET_APP) $(TARGET_TUI)

$(TARGET_APP): $(OBJ_DIR)/main.o $(OBJ_DIR)/data_gen.o $(OBJ_DIR)/matriz.o $(OBJ_DIR)/zernike_algo.o $(OBJ_DIR)/zernike.o
	$(CC) -o $@ $^ $(LDFLAGS)

$(TARGET_TUI): $(OBJ_DIR)/tui_main.o
	$(CC) -o $@ $^ $(LDFLAGS)

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c
	$(CC) $(CFLAGS) -c -o $@ $<

directories:
	@mkdir -p $(OBJ_DIR)
	@mkdir -p $(BIN_DIR)

clean:
	rm -rf $(OBJ_DIR) $(BIN_DIR)

.PHONY: all clean directories
