IBBS = ibbs$(shell date +%m%y)
IBBS_URL = https://www.telnetbbsguide.com/bbslist/$(IBBS).zip

GENERATED = \
	    magiterm.ini \
	    qodem.ini \
	    ibbs.json

all: $(GENERATED)

clean:
	rm -f $(GENERATED)

magiterm.ini: $(IBBS)/syncterm.lst
	python sync2magi.py -i $< -o $@

qodem.ini: $(IBBS)/syncterm.lst
	python sync2qodem.py -i $< -o $@

ibbs.json: $(IBBS)/syncterm.lst
	python sync2json.py -i $< -o $@

$(IBBS).zip:
	curl -o $@ $(IBBS_URL)

$(IBBS): $(IBBS).zip
	unzip -d $@ $<

$(IBBS)/syncterm.lst: $(IBBS)
