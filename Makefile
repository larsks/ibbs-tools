IBBS = ibbs$(shell date +%m%y)
IBBS_URL = https://www.telnetbbsguide.com/bbslist/$(IBBS).zip

all: magiterm.ini qodem.ini

magiterm.ini: $(IBBS)/syncterm.lst
	python sync2magi.py -i $< -o $@

qodem.ini: $(IBBS)/syncterm.lst
	python sync2qodem.py -i $< -o $@

$(IBBS).zip:
	curl -o $@ $(IBBS_URL)

$(IBBS): $(IBBS).zip
	unzip -d $@ $<

$(IBBS)/syncterm.lst: $(IBBS)
