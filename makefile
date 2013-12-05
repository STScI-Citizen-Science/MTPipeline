INPUT_BASE=/astro/3/mutchler/mt/drizzled/

help:
	@echo 'makefile for the mtpipeline.                                                    '
	@echo '                                                                                '
	@echo 'Usage:                                                                          '
	@echo '    master_images TARGET=???             Generate master_images table for TARGET'
	@echo '    master_finders                                Genereate master_finders table'
	@echo '    sub_images TARGET=???                   Generate sub_images table for TARGET'
	@echo '    finders                                               Generate finders table'
	@echo '                                                                                '

master_images:
ifdef TARGET
	python ephem/build_master_table.py -filelist '$(INPUT_BASE)*$(TARGET)/png/*single_sci_linear.png'
else
	@echo "You must specify a target, e.g. TARGET=jupiter."
endif

master_finders:
	python ephem/build_master_finders_table.py

sub_images:
ifdef TARGET
	python ephem/build_sub_images_table.py -filelist '$(INPUT_BASE)*$(TARGET)/png/*_single_sci_linear*.png'
else
	@echo "You must specify a target, e.g. TARGET=jupiter."
endif

finders:
	python ephem/build_finders_table.py
