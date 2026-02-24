# ==============================================================
#							A_MAZE_ING
# ==============================================================

NAME = a_maze_ing.py
SRC_DIR = src
CONFIG_FILE = config.txt

IS_WSL := $(shell grep -qi microsoft /proc/version && echo yes || echo no)
ifeq ($(IS_WSL),yes)
	TMP_BASE := $(if $(TMPDIR),$(TMPDIR),/tmp)
	USER_NAME := $(shell whoami)
	CONDA_DIR := $(TMP_BASE)/$(USER_NAME)_miniconda
else
    CONDA_DIR := $(CURDIR)/miniconda
endif

CONDA_BIN = $(CONDA_DIR)/bin/conda
CONDA_LINK = $(CURDIR)/miniconda
ENV_NAME = conda_env
PYTHON_VER = 3.10.12 # To check
ENV_PYTHON = $(CONDA_DIR)/envs/$(ENV_NAME)/bin/python

MLX_NAME = mlx
MLX_FILE = mlx-2.2-py3-ubuntu-any.whl
MLX_DIR = $(SRC_DIR)/$(MLX_NAME)

SYSTEM_DEPS =	flake8 \
				mypy \
				xorg-libxcb \
				xcb-util \
				xcb-util-keysyms \
				xorg-libxext \
				xorg-libxrender \
				xorg-libx11

all:
	@if [ ! -f "$(ENV_PYTHON)" ]; then \
		$(MAKE) --no-print-directory install; \
	else \
		echo "Starting '$(NAME)'..."; \
		$(MAKE) --no-print-directory run; \
	fi

install: install_mlx install_conda create_env
	@echo "Installing dependencies into $(ENV_NAME)..."
	@$(CONDA_BIN) install -y -n $(ENV_NAME) --override-channels \
	-c conda-forge --file requirements.txt $(SYSTEM_DEPS)
	@echo "Setup complete. Use 'make run' to start."

install_mlx:
	@if [ ! -d "$(MLX_DIR)" ]; then \
		echo "Installing mlx into '$(MLX_DIR)'..."; \
		unzip -u $(MLX_FILE) -d src; \
		rm -rf src/mlx-2.2.dist-info; \
	else \
		echo "Mlx already installed in '$(MLX_DIR)'."; \
	fi


remove_mlx:
	@if [ -d "$(MLX_DIR)" ]; then \
		echo "Removing mlx directory..."; \
		$(RM) -r $(MLX_DIR); \
	fi

install_conda:
	@if [ ! -d "$(CONDA_DIR)" ]; then \
		echo "Downloading Miniconda..."; \
		curl -L https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o miniconda.sh; \
		echo "Installing Miniconda to '$(CONDA_DIR)'..."; \
		bash miniconda.sh -b -p $(CONDA_DIR); \
		rm miniconda.sh; \
	else \
		echo "Miniconda already installed in '$(CONDA_DIR)'."; \
	fi

create_env:
	@if [ ! -d "$(CONDA_DIR)/envs/$(ENV_NAME)" ]; then \
		echo "Creating Conda environment '$(ENV_NAME)'..."; \
		$(CONDA_BIN) create -y -n $(ENV_NAME) python=$(PYTHON_VER) --override-channels -c conda-forge; \
	else \
		echo "Environment '$(ENV_NAME)' already exists."; \
	fi
	@if [ "$(IS_WSL)" = "yes" ] && [ ! -L "$(CONDA_LINK)" ]; then \
		echo "Linking $(CONDA_DIR) to $(CONDA_LINK)..."; \
		ln -s $(CONDA_DIR) $(CONDA_LINK); \
	fi

remove_conda:
	@if [ -L "$(CONDA_LINK)" ]; then \
		echo "Removing symlink..."; \
		rm "$(CONDA_LINK)"; \
	fi
	@if [ -d "$(CONDA_DIR)" ]; then \
		echo "Removing conda directory..."; \
		$(RM) -r $(CONDA_DIR); \
	fi

run:
	@if [ -f "$(ENV_PYTHON)" ]; then \
		$(ENV_PYTHON) $(NAME) $(CONFIG_FILE); \
	else \
		echo "Conda environment not found. Run 'make install'."; \
		exit 1; \
	fi

debug:
	@echo "TODO"

lint:
	@if [ -f "$(ENV_PYTHON)" ]; then \
		echo "Running flake8..."; \
		$(ENV_PYTHON) -m flake8 .; \
		echo "Running mypy with flags..."; \
		$(ENV_PYTHON) -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs; \
	else \
		echo "Conda environment not found. Run 'make install'."; \
		exit 1; \
	fi

lint-strict:
	@if [ -f "$(ENV_PYTHON)" ]; then \
		echo "Running flake8..."; \
		$(ENV_PYTHON) -m flake8 .; \
		echo "Running mypy --strict..."; \
		$(ENV_PYTHON) -m mypy . --strict; \
	else \
		echo "Conda environment not found. Run 'make install'."; \
		exit 1; \
	fi

clean:
	@if [ -n "$$(find . -type d \( -name ".mypy_cache" -o -name "__pycache__" \) -print -quit)" ]; then \
		echo "Cleaning cache files..."; \
		find . -type d \( -name ".mypy_cache" -o -name "__pycache__" \) -exec rm -rf {} +; \
	fi

fclean: clean remove_conda remove_mlx

re: fclean all

.PHONY: install run debug clean fclean re all
.DEFAULT_GOAL = all
