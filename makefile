INPUT_BASE=/astro/3/mutchler/mt/drizzled/

help:
	@echo 'makefile for the mtpipeline.                                                    '
	@echo '                                                                                '
	@echo 'Usage:                                                                          '
	@echo '    new_data                      Copy over any new data from the "archive" area'
	@echo '    master_images TARGET=???             Generate master_images table for TARGET'
	@echo '    jpl2db TARGET=???                              Seed the master_finders table'
	@echo '    master_finders                                Genereate master_finders table'
	@echo '    sub_images TARGET=???                   Generate sub_images table for TARGET'
	@echo '    finders                                               Generate finders table'
	@echo '    stage                            Update the contents of the ftp staging tree'
	@echo '    dump DATE=YYYY-MM-DD                                  Create a database dump'
	@echo '                                                                                '


new_data:
	cp -vru /astro/3/mutchler/mt/archive/ /astro/3/mutchler/mt/drizzled/

master_images:
ifdef TARGET
	python ephem/build_master_images_table.py -filelist '$(INPUT_BASE)*$(TARGET)/png/*single_sci_linear.png'
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

stage:
	python tools/update-staging.py -reproc

dump:
ifdef DATE
	mysqldump -u root mtpipeline -p > /astro/3/mutchler/mt/databasedump/mtdump-$(DATE).dump
else
	@echo "You must specify today's date e.g. DATE=YYYY-MM-DD"
endif	
