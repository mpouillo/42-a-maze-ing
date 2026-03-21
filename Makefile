# ==============================================================
#							A_MAZE_ING
# ==============================================================

NAME = a_maze_ing.py
SRC_DIR = src
CONFIG_FILE = config.txt

TMP_BASE := $(if $(TMPDIR),$(TMPDIR),/tmp)
USER_NAME := $(shell whoami)
CONDA_DIR := $(TMP_BASE)/$(USER_NAME)_miniconda
CONDA_BIN = $(CONDA_DIR)/bin/conda
CONDA_LINK = $(CURDIR)/miniconda
ENV_NAME = conda_env
ENV_DIR = $(CONDA_DIR)/envs/$(ENV_NAME)
PYTHON_VER = 3.10.12
ENV_PYTHON = $(ENV_DIR)/bin/python

SYSTEM_DEPS =	flake8 \
				mypy \
				pudb \
				libvulkan-headers \
				libvulkan-loader \
				xorg-libxcb \
				xcb-util \
				xcb-util-keysyms \
				xorg-libxext \
				xorg-libxrender \
				xorg-libx11

all:
	@if [ -x "$(ENV_PYTHON)" ]; then \
		MISSING_PKGS=0; \
		INSTALLED_LIST=$$($(CONDA_BIN) list -n $(ENV_NAME)); \
		for pkg in $(SYSTEM_DEPS); do \
			if ! echo "$$INSTALLED_LIST" | grep -q "^$$pkg "; then \
				echo "Missing: $$pkg"; \
				MISSING_PKGS=1; \
			fi; \
		done; \
		if [ $$MISSING_PKGS -eq 1 ]; then \
			$(MAKE) --no-print-directory install; \
		fi; \
		echo "Starting '$(NAME)'..."; \
		$(MAKE) --no-print-directory run; \
	else \
		$(MAKE) --no-print-directory install; \
	fi

install: install_conda create_env
	@echo "Installing dependencies into $(ENV_NAME)..."
	@$(CONDA_BIN) install -y -q -n $(ENV_NAME) --override-channels \
	-c conda-forge --file requirements.txt $(SYSTEM_DEPS) >/dev/null 2>&1 \
		|| (echo "Error: Dependency installation failed."; exit 1)
	@$(MAKE) --no-print-directory install_mlx
	@echo "Setup complete. Use 'make run' to start."

install_mlx:
	@if ! $(ENV_PYTHON) -c "import mlx" >/dev/null 2>&1; then \
		echo "Installing mlx package..."; \
		( \
			wget -q https://cdn.intra.42.fr/document/document/46950/mlx_CLXV-2.2.tgz && \
			tar -xf mlx_CLXV-2.2.tgz && \
			cd mlx_CLXV && \
			export PATH=$(ENV_DIR)/bin:$$PATH && \
			export CPATH=$(ENV_DIR)/include && \
			export LIBRARY_PATH=$(ENV_DIR)/lib && \
			export LD_LIBRARY_PATH=$(ENV_DIR)/lib && \
			$(ENV_PYTHON) -m pip install build && \
			SHELL=/bin/bash ./configure.sh && \
			$(MAKE) \
		) >/dev/null 2>&1 && \
		$(ENV_PYTHON) -m pip install mlx_CLXV/mlx-2.2-py3-none-any.whl -q && \
		$(RM) -r mlx_CLXV mlx_CLXV-2.2.tgz* \
		|| (echo "Error: mlx installation failed."; exit 1); \
	else \
		echo "Mlx already installed."; \
	fi

install_conda:
	@if [ ! -d "$(CONDA_DIR)" ]; then \
		echo "Downloading Miniconda..."; \
		curl -Ls https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o miniconda.sh; \
		echo "Installing Miniconda to '$(CONDA_DIR)'..."; \
		bash miniconda.sh -b -p $(CONDA_DIR) > /dev/null 2>&1 \
		|| (echo "Conda install failed!"; exit 1); \
		$(RM) miniconda.sh; \
	else \
		echo "Miniconda already installed in '$(CONDA_DIR)'."; \
	fi

remove_conda:
	@if [ -L "$(CONDA_LINK)" ] || [ -e "$(CONDA_LINK)" ]; then \
		echo "Removing Miniconda symlink..."; \
		$(RM) "$(CONDA_LINK)"; \
	fi
	@if [ -d "$(CONDA_DIR)" ]; then \
		echo "Removing Miniconda directory..."; \
		$(RM) -r $(CONDA_DIR); \
	fi

create_env:
	@if [ ! -d "$(CONDA_DIR)/envs/$(ENV_NAME)" ]; then \
		echo "Creating Conda environment '$(ENV_NAME)'..."; \
		$(CONDA_BIN) create -y -q -n $(ENV_NAME) python=$(PYTHON_VER) --override-channels -c conda-forge > /dev/null 2>&1; \
	else \
		echo "Environment '$(ENV_NAME)' already exists."; \
	fi
	@echo "Linking $(CONDA_DIR) to $(CONDA_LINK)..."
	@ln -snf $(CONDA_DIR) $(CONDA_LINK)

build:
	@echo "Building the mazegen package..."
	@$(ENV_PYTHON) -m pip install build
	@$(ENV_PYTHON) -m build --wheel --outdir .
	@rm -rf build/ *.egg-info

run:
	@if [ -f "$(ENV_PYTHON)" ]; then \
		$(ENV_PYTHON) $(NAME) $(CONFIG_FILE); \
	else \
		echo "Conda environment not found. Run 'make install'."; \
		exit 1; \
	fi

debug:
	@if [ -f "$(ENV_PYTHON)" ]; then \
		echo "Running in debug mode..."; \
		$(ENV_PYTHON) -m pudb $(NAME) $(CONFIG_FILE); \
	else \
		echo "Conda environment not found. Run 'make install' first."; \
		exit 1; \
	fi

lint:
	@if [ -f "$(ENV_PYTHON)" ]; then \
		echo "Running flake8..."; \
		$(ENV_PYTHON) -m flake8 .; \
		echo "Running mypy..."; \
		$(ENV_PYTHON) -m mypy .; \
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

fclean: clean remove_conda

re: fclean all

.PHONY: install run debug clean fclean re all build
.DEFAULT_GOAL = all
