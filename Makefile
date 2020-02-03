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
	ibbs sync2magi -i $< -o $@

qodem.ini: $(IBBS)/syncterm.lst
	ibbs sync2qodem -i $< -o $@

ibbs.json: $(IBBS)/syncterm.lst
	ibbs sync2json -i $< -o $@

$(IBBS).zip:
	curl -o $@ $(IBBS_URL)

$(IBBS): $(IBBS).zip
	unzip -d $@ $<

$(IBBS)/syncterm.lst: $(IBBS)
