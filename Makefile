MAKEFILE_PATH		:=	$(abspath $(lastword $(MAKEFILE_LIST)))
ROOT_DIR        :=	$(patsubst %/,%,$(dir $(MAKEFILE_PATH)))
APPS_DIR				= 	$(HOME)/.local/share/applications
PACKAGE_NAME		=		flappy-bird-pose-estimation
PACKAGE_DIR			=		$(HOME)/.local/share/$(PACKAGE_NAME)
PACKAGE_DESKTOP	=		$(APPS_DIR)/$(PACKAGE_NAME).desktop
PACKAGE_CONFIG	=		$(HOME)/.config/$(PACKAGE_NAME).json

install:
	/usr/bin/python3 -m pip install -q -r $(ROOT_DIR)/requirements.txt
	mkdir -p $(PACKAGE_DIR)
	cp -r $(ROOT_DIR)/assets $(ROOT_DIR)/flappy.py $(PACKAGE_DIR)
	mkdir -p $(HOME)/.config
	cp $(ROOT_DIR)/config.json $(PACKAGE_CONFIG)
	mkdir -p $(APPS_DIR)
	cp $(ROOT_DIR)/app.desktop $(PACKAGE_DESKTOP)
	sed -ir "s|\$$PACKAGE_DIR|$(PACKAGE_DIR)|" $(PACKAGE_DESKTOP)
	sed -ir "s|\$$PACKAGE_CONFIG|$(PACKAGE_CONFIG)|" $(PACKAGE_DESKTOP)

uninstall:
	rm -drf $(PACKAGE_DIR) $(PACKAGE_ICON) \
		$(PACKAGE_CONFIG) \
		$(PACKAGE_DESKTOP)
