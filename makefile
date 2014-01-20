INPUT_BASE=/astro/3/mutchler/mt/drizzled/

help:
	@echo 'makefile for the mtpipeline.                                                    '
	@echo '                                                                                '
	@echo 'Usage:                                                                          '
	@echo '    master_images TARGET=???             Generate master_images table for TARGET'
	@echo '    jpl2db TARGET=???                              Seed the master_finders table'
	@echo '    master_finders                                Genereate master_finders table'
	@echo '    sub_images TARGET=???                   Generate sub_images table for TARGET'
	@echo '    finders                                               Generate finders table'
	@echo '    dump DATE=YYYY-MM-DD                                  Create a database dump'
	@echo '                                                                                '

master_images:
ifdef TARGET
	python ephem/build_master_table.py -filelist '$(INPUT_BASE)*$(TARGET)/png/*single_sci_linear.png'
else
	@echo "You must specify a target, e.g. TARGET=jupiter."
endif

jpl2db:
ifdef TARGET
	python ephem/jpl2db.py -filelist '$(INPUT_BASE)*$(TARGET)/*single_sci.fits'
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

dump:
ifdef DATE
	mysqldump -u root mtpipeline -p > /astro/3/mutchler/mt/databasedump/mtdump-$(DATE).sql
else
	@echo "You must specify today's date e.g. DATE=YYYY-MM-DD"
endif	
